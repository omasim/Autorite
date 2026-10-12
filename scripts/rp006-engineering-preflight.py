"""Exclusive, committed-source engineering preflight; no Test/Result or run authorization."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import subprocess
import sys
import traceback

ROOT = Path(__file__).resolve().parents[1]
INPUTS = ['research/RP006/producer.py', 'research/RP006/verifier.py', 'research/RP006/resources.py',
          'research/RP004/lineage.py', 'research/RP004/replay.py', 'research/RP006/DOMAIN.json',
          'research/RP006/ENTRY_PLAN.json', 'research/RP006/RP006_OPERATIONAL_PROTOCOL.md',
          'research/RP006/RP006_PRIOR_ART_REVIEW.md', 'tests/test_rp006_implementation.py',
          'scripts/rp006-engineering-preflight.py']


def load(name):
    spec = importlib.util.spec_from_file_location('rp006_preflight_' + name, ROOT / 'research/RP006' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def preflight():
    if sys.version_info < (3, 11):
        raise ValueError('Preflight requires Python 3.11+')
    source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    for name in INPUTS:
        if (ROOT / name).read_bytes() != subprocess.check_output(['git', 'show', source + ':' + name], cwd=ROOT):
            raise ValueError('Commit the exact preflight source before collecting artifacts')
    hashes = {name: digest(ROOT / name) for name in INPUTS}
    producer, verifier, resource = load('producer'), load('verifier'), load('resources')
    directory = ROOT / 'research/RP006/preparation-001'
    directory.mkdir(exist_ok=False)
    manifest = {'purpose': 'KNOWN_DOMAIN_SOFTWARE_PREFLIGHT', 'scientific_status_promotion': False,
        'execution_authorized': False, 'source_commit': source, 'input_sha256': hashes,
        'environment': {'python': sys.version, 'platform': platform.platform(), 'machine': platform.machine()},
        'status': 'INCOMPLETE', 'limits': {'monotonic_seconds': 60, 'civil_elapsed_seconds': 60,
        'clock_gap_seconds': 2, 'peak_process_rss_bytes': 134217728}, 'outputs': {}}
    guard = resource.Guard()
    try:
        domain = json.loads((ROOT / 'research/RP006/DOMAIN.json').read_text())
        bundle = producer.produce(domain, guard)
        replay = verifier.verify(bundle, domain, guard)
        for name, value in [('bundle.json', bundle), ('replay.json', replay)]:
            guard()
            (directory / name).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n')
            guard()
        timing = guard()
        timing.update(measurement_scope='Guard starts after source checks/imports and includes generation, independent replay and serialization. RSS is process lifetime peak.',
                      rss_raw_unit='bytes' if sys.platform == 'darwin' else 'KiB',
                      child_processes='none inside measured computation',
                      deadline_policy='Cooperative dual-clock rejection only. External suspension-aware supervisor contract is pending before a recorded run.')
        (directory / 'timing.json').write_text(json.dumps(timing, indent=2) + '\n')
        guard()
        if hashes != {name: digest(ROOT / name) for name in INPUTS}:
            raise ValueError('Source changed during preflight')
        manifest['status'] = 'COMPLETE'
    except BaseException:
        (directory / 'failure.txt').write_text(traceback.format_exc())
        raise
    finally:
        manifest['outputs'] = {p.name: digest(p) for p in sorted(directory.iterdir()) if p.name != 'manifest.json'}
        (directory / 'manifest.json').write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'purpose': manifest['purpose'], 'status': manifest['status'],
                      'timing': timing, 'counts': bundle['summary']}, sort_keys=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--engineering-preflight', action='store_true', required=True)
    parser.parse_args()
    preflight()
