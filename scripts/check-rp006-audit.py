"""Verify one preserved RP006 recorded attempt and its independent full replay."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
RUN_ID = '570e92be-204b-4330-8300-bcbc4e2078d2'
RUN = ROOT / 'research/RP006/attempts' / RUN_ID
POST_RUN_VALIDATION_FILES = {
    'packages/research-schema/validate.py',
    'scripts/check-rp006-preparation.py',
    'scripts/check-rp006-supervisor.py',
    'cycles/cycle-02/manifest.json',
}
POST_RUN_COMPATIBLE_IMPLEMENTATIONS = {
    'research/RP006/producer.py',
    'research/RP006/verifier.py',
}
OUTPUTS = {'truth.jsonl', 'projections.jsonl', 'pairs.jsonl', 'conflicts.jsonl',
           'certificates.json', 'summary.json', 'timing.json', 'replay.json'}


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_rows(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check():
    authorization = json.loads((ROOT / 'research/RP006/EXECUTION_AUTHORIZATION.json').read_text())
    freeze = json.loads((ROOT / 'research/RP006/EXECUTION_FREEZE.json').read_text())
    if authorization['attempt_id'] != RUN_ID:
        raise ValueError('Result run does not match the accepted one-attempt authorization')
    if authorization['status'] != 'ACCEPTED' or authorization['execution_authorized'] is not True:
        raise ValueError('D-0016 authorization is not active for this recorded attempt')
    if freeze['source_commit'] != authorization['source_commit']:
        raise ValueError('Authorization and source freeze commit differ')
    if not re.fullmatch(r'[0-9a-f]{40}', freeze['source_commit']) or freeze['status'] != 'ACCEPTED':
        raise ValueError('Malformed or unaccepted source freeze')
    manifest_path = RUN / 'manifest.json'
    manifest = json.loads(manifest_path.read_text())
    if manifest['status'] != 'COMPLETE' or manifest['failure'] is not None or manifest['run_id'] != RUN_ID:
        raise ValueError('Attempt is not a complete, failure-free recorded run')
    if set(manifest['outputs']) != OUTPUTS or {p.name for p in RUN.iterdir()} != OUTPUTS | {'manifest.json'}:
        raise ValueError('Recorded output inventory differs from the fixed Test')
    for name, checksum in manifest['outputs'].items():
        if digest(RUN / name) != checksum:
            raise ValueError('Output checksum mismatch: ' + name)
    if (RUN / 'worker.json').exists() or list(RUN.glob('*.partial')):
        raise ValueError('Temporary or unreviewed worker artifacts remain')
    if digest(ROOT / 'research/RP006/EXECUTION_AUTHORIZATION.json') != manifest['authorization']['authorization_sha256']:
        raise ValueError('Attempt authorization hash mismatch')
    if manifest['authorization']['source_freeze_sha256'] != digest(ROOT / 'research/RP006/EXECUTION_FREEZE.json'):
        raise ValueError('Attempt source freeze hash mismatch')
    if manifest['authorization']['source_commit'] != authorization['source_commit']:
        raise ValueError('Attempt source commit mismatch')
    if freeze['source_commit'] not in subprocess.check_output(
            ['git', 'rev-list', 'HEAD'], cwd=ROOT, text=True).splitlines():
        raise ValueError('Frozen source is not in the current ancestry')
    for relative, checksum in freeze['input_sha256'].items():
        committed = subprocess.check_output(['git', 'show', freeze['source_commit'] + ':' + relative], cwd=ROOT)
        if hashlib.sha256(committed).hexdigest() != checksum:
            raise ValueError('Frozen source commit hash mismatch: ' + relative)
        if (relative not in POST_RUN_VALIDATION_FILES
                and relative not in POST_RUN_COMPATIBLE_IMPLEMENTATIONS
                and digest(ROOT / relative) != checksum):
            raise ValueError('Frozen input changed: ' + relative)
    timing = json.loads((RUN / 'timing.json').read_text())
    for key in ('monotonic_seconds', 'suspend_aware_seconds', 'civil_elapsed_seconds'):
        if not 0 <= timing[key] <= 60:
            raise ValueError('Whole-attempt time ceiling exceeded: ' + key)
    if timing['conservative_process_tree_peak_rss_bytes'] > 134217728:
        raise ValueError('Conservative process-tree memory ceiling exceeded')
    if timing['clock'] != 'mach_continuous_time' or abs(timing['clock_gap_seconds']) > 2:
        raise ValueError('Suspend-aware host clock contract failed')

    actual = {
        'truth': read_rows(RUN / 'truth.jsonl'),
        'projections': read_rows(RUN / 'projections.jsonl'),
        'pairs': read_rows(RUN / 'pairs.jsonl'),
        'conflicts': read_rows(RUN / 'conflicts.jsonl'),
        'certificates': json.loads((RUN / 'certificates.json').read_text()),
        'summary': json.loads((RUN / 'summary.json').read_text()),
    }
    domain = json.loads((ROOT / 'research/RP006/DOMAIN.json').read_text())
    producer = load('rp006_recorded_producer', ROOT / 'research/RP006/producer.py')
    produced = producer.produce(domain)
    if any(produced.get(key) != value for key, value in actual.items()):
        raise ValueError('Current producer no longer reproduces the recorded frozen result')
    verifier = load('rp006_independent_verifier', ROOT / 'research/RP006/verifier.py')
    replay = verifier.verify(actual, domain)
    if replay != json.loads((RUN / 'replay.json').read_text()):
        raise ValueError('Saved independent replay report differs from a fresh full verifier replay')
    summary = actual['summary']
    if (summary['truth_rows'], summary['projections'], summary['pair_mask_comparisons'],
            summary['conflict_rows'], summary['family_mask_verdicts']) != (216, 48, 120, 438, 16):
        raise ValueError('Prospective coverage inventory is incomplete')
    if summary['families']['FULL']['minimal_masks'] != ['001'] or summary['families']['TOPOLOGY_STATE']['minimal_masks'] != ['001', '010']:
        raise ValueError('Finite-corpus minimal-mask classifications differ from exact replay')
    print('PASS: RP006 attempt hashes, D-0016 authorization, resource limits, all 216 truth rows and independent certificates/replay verified.')


if __name__ == '__main__':
    check()
