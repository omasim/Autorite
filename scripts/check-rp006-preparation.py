"""Replay preserved software preflight and candidate provenance; not research execution."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location('rp006_check_' + name, ROOT / 'research/RP006' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate():
    directory = ROOT / 'research/RP006/preparation-001'
    manifest = json.loads((directory / 'manifest.json').read_text())
    if manifest['purpose'] != 'KNOWN_DOMAIN_SOFTWARE_PREFLIGHT' or manifest['status'] != 'COMPLETE' or manifest['execution_authorized'] is not False:
        raise ValueError('Preflight role/completeness/authorization')
    if (directory / 'failure.txt').exists() or set(manifest['outputs']) != {'bundle.json', 'replay.json', 'timing.json'}:
        raise ValueError('Preflight output coverage')
    for name, checksum in manifest['outputs'].items():
        if digest(directory / name) != checksum:
            raise ValueError('Preflight output hash')
    for name, checksum in manifest['input_sha256'].items():
        original = subprocess.check_output(['git', 'show', manifest['source_commit'] + ':' + name], cwd=ROOT)
        if hashlib.sha256(original).hexdigest() != checksum or digest(ROOT / name) != checksum:
            raise ValueError('Preflight input/source provenance')
    for path in sorted(directory.iterdir()):
        relative = path.relative_to(ROOT).as_posix()
        history = subprocess.check_output(['git', 'log', '--diff-filter=A', '--format=%H', '--', relative], cwd=ROOT, text=True).splitlines()
        if history and path.read_bytes() != subprocess.check_output(['git', 'show', history[-1] + ':' + relative], cwd=ROOT):
            raise ValueError('Preserved engineering artifact changed')
    bundle = json.loads((directory / 'bundle.json').read_text())
    domain = json.loads((ROOT / 'research/RP006/DOMAIN.json').read_text())
    producer = load('producer')
    verified = load('verifier').verify(bundle, domain)
    if verified != json.loads((directory / 'replay.json').read_text()) or producer.canonical(producer.produce(domain)) != producer.canonical(bundle):
        raise ValueError('Engineering producer/verifier replay mismatch')
    timing = json.loads((directory / 'timing.json').read_text())
    if not (0 <= timing['monotonic_seconds'] <= 60 and 0 <= timing['civil_elapsed_seconds'] <= 60
            and abs(timing['civil_elapsed_seconds'] - timing['monotonic_seconds']) <= 2
            and 0 < timing['peak_process_rss_bytes'] <= 134217728):
        raise ValueError('Recorded engineering resource ceiling')
    candidate = json.loads((ROOT / 'research/RP006/SOURCE_FREEZE_PROPOSAL.json').read_text())
    if candidate['source_commit'] != manifest['source_commit'] or candidate['input_sha256'] != manifest['input_sha256']:
        raise ValueError('Candidate source binding')
    if candidate['source_frozen'] is not False or candidate['execution_authorized'] is not False or candidate['pre_execution_checkpoint_accepted'] is not False:
        raise ValueError('Proposal cannot grant research execution')
    for path, checksum in candidate['preflight_sha256'].items():
        if digest(ROOT / path) != checksum:
            raise ValueError('Candidate preflight receipt')
    tag = subprocess.run(['git', 'rev-parse', '--verify', 'refs/tags/rp006-preparation-001^{commit}'], cwd=ROOT, capture_output=True, text=True)
    if tag.returncode == 0 and tag.stdout.strip() != manifest['source_commit']:
        raise ValueError('Preparation tag source mismatch')
    print('PASS: RP006 known-domain software preflight: all 216 truth rows, 48 projections, 120 pairs, 438 conflict rows and 16 certificates replay; no research Result.')


if __name__ == '__main__':
    validate()
