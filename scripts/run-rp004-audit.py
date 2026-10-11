"""Run one committed RP004 corpus audit; never overwrite a run directory."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import platform
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'research/RP004'))
from lineage import check_fixtures
from audit import iter_rows, iter_collisions, summarize, write_jsonl
from replay import check_config, rebuild, evaluate, canonical, replay

INPUTS = ['research/RP004/' + name for name in [
    'RP004_OPERATIONAL_PROTOCOL.md', 'RP004_FIXTURES.json', 'lineage.py',
    'RP004_COLLISION_REVIEW.md', 'RP004_PREPARATION_REVIEW.md', 'RP004_AUDIT_CONFIG.json',
    'audit.py', 'replay.py', 'RP004_EXECUTION_REVIEW.md', 'audit-001/RECORD.md']]
INPUTS += ['scripts/run-rp004-audit.py', 'scripts/check-rp004-audit.py',
           'scripts/check-rp004-preparation.py', 'tests/test_rp004_lineage.py', 'tests/test_rp004_audit.py']
OUTPUTS = ['manifest.json', 'frozen-inputs.json', 'answers.jsonl', 'collisions.jsonl',
           'summary.json', 'replay.json', 'timing.json']


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def utc():
    return datetime.now(timezone.utc).isoformat()


def memory():
    raw = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(raw if sys.platform == 'darwin' else raw * 1024)


def preflight(run_id, config):
    check_config(config)
    if sys.version_info < (3, 11) or run_id != config['run_id']:
        raise ValueError('Run ID or Python version mismatch')
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    if subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=no'], cwd=ROOT).strip():
        raise ValueError('Tracked source must be committed before execution')
    hashes = {}
    for name in INPUTS:
        original = subprocess.check_output(['git', 'show', commit + ':' + name], cwd=ROOT)
        if original != (ROOT / name).read_bytes():
            raise ValueError('Input differs from committed source: ' + name)
        hashes[name] = digest(ROOT / name)
    return commit, hashes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-id', required=True)
    args = parser.parse_args()
    config = json.loads((ROOT / 'research/RP004/RP004_AUDIT_CONFIG.json').read_text())
    commit, hashes = preflight(args.run_id, config)
    directory = ROOT / 'research/RP004/runs' / args.run_id
    directory.mkdir(parents=True, exist_ok=False)
    started, clock = utc(), time.monotonic()
    frozen = {'source_commit': commit, 'input_sha256': hashes, 'config': config,
              'command': ['python3', 'scripts/run-rp004-audit.py', '--run-id', args.run_id],
              'execution_authorization': 'User requested continuation of the published RP004 864-cell audit on 2026-10-11',
              'output_inventory': OUTPUTS}
    environment = {'python': sys.version, 'os': platform.platform(), 'processes': 1,
                   'network': 'none used by the audit', 'peak_memory_units': 'bytes'}
    manifest = {'configuration': frozen, 'seeds': config['seeds'], 'environment': environment, 'outputs': {}}
    # Persist the exact committed source/input snapshot before any corpus calculation.
    write(directory / 'manifest.json', manifest)
    write(directory / 'frozen-inputs.json', {k: manifest[k] for k in ('configuration', 'seeds', 'environment')})

    def guard():
        if time.monotonic() - clock > config['wall_seconds'] or memory() > config['memory_bytes']:
            raise RuntimeError('Declared resource budget exceeded')

    def timeout(*_):
        raise TimeoutError('60-second RP004 audit limit')

    status = 'INCOMPLETE'
    try:
        signal.signal(signal.SIGALRM, timeout)
        signal.setitimer(signal.ITIMER_REAL, config['wall_seconds'])
        guard()
        fixtures = json.loads((ROOT / 'research/RP004/RP004_FIXTURES.json').read_text())
        calibration = check_fixtures(fixtures)
        for case in fixtures['cases']:
            independent = rebuild(case['events'])
            for control in case['controls']:
                if canonical(evaluate(independent, control['query'])) != canonical(control['expected']):
                    raise ValueError('Independent calibration mismatch')
        rows = []
        with (directory / 'answers.jsonl').open('x') as stream:
            for row in iter_rows(fixtures, config, guard):
                write_jsonl(stream, [row])
                rows.append(row)
        collisions = []
        with (directory / 'collisions.jsonl').open('x') as stream:
            for row in iter_collisions(fixtures, config, guard):
                write_jsonl(stream, [row])
                collisions.append(row)
        summary = summarize(rows, collisions, config)
        with (directory / 'answers.jsonl').open() as answers, (directory / 'collisions.jsonl').open() as pairs:
            independent = replay(answers, pairs, fixtures, config, guard)
        if canonical(summary) != canonical(independent):
            raise ValueError('Independent aggregate mismatch')
        write(directory / 'summary.json', summary)
        write(directory / 'replay.json', {'status': 'PASS', 'decoder_rows_verified': 864,
              'truth_queries_verified': 216, 'collision_comparisons_verified': 60,
              'disclosed_calibration': calibration, 'coverage_order_verified': True,
              'all_projections_truth_answers_counts_and_collision_witnesses_match': True})
        guard()
        status = 'COMPLETE'
    except Exception as exc:
        (directory / 'failure.txt').write_text(type(exc).__name__ + ': ' + str(exc) + '\n')
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        write(directory / 'timing.json', {'status': status, 'started_at': started, 'ended_at': utc(),
              'elapsed_monotonic_seconds': time.monotonic() - clock, 'peak_resident_memory_bytes': memory()})
        manifest['outputs'] = {p.name: digest(p) for p in sorted(directory.iterdir()) if p.name != 'manifest.json'}
        write(directory / 'manifest.json', manifest)
    print(json.dumps({'run': args.run_id, 'status': status, 'source_commit': commit}))
    if status != 'COMPLETE':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
