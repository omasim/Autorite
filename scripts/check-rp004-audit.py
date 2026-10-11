"""Verify all preserved RP004 bytes, committed input provenance and full replay."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'research/RP004'))
from replay import canonical, replay, check_config


def check_run(run):
    manifest = json.loads((run / 'manifest.json').read_text())
    assert set(manifest) == {'configuration', 'seeds', 'environment', 'outputs'}
    config = manifest['configuration']
    assert set(config['output_inventory']) == {'manifest.json', 'frozen-inputs.json', 'answers.jsonl',
        'collisions.jsonl', 'summary.json', 'replay.json', 'timing.json'}
    assert {p.name for p in run.iterdir()} == set(config['output_inventory'])
    assert set(manifest['outputs']) == set(config['output_inventory']) - {'manifest.json'}
    for name, expected in manifest['outputs'].items():
        assert hashlib.sha256((run / name).read_bytes()).hexdigest() == expected, name
    frozen = json.loads((run / 'frozen-inputs.json').read_text())
    assert canonical(frozen) == canonical({k: manifest[k] for k in ('configuration', 'seeds', 'environment')})
    check_config(config['config'])
    assert manifest['seeds'] == config['config']['seeds']
    assert len(config['input_sha256']) == 15
    for name, expected in config['input_sha256'].items():
        original = subprocess.check_output(['git', 'show', config['source_commit'] + ':' + name], cwd=ROOT)
        assert hashlib.sha256(original).hexdigest() == expected, name
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, name
    timing = json.loads((run / 'timing.json').read_text())
    assert timing['status'] == 'COMPLETE'
    assert 0 <= timing['elapsed_monotonic_seconds'] <= config['config']['wall_seconds']
    assert 0 < timing['peak_resident_memory_bytes'] <= config['config']['memory_bytes']
    fixtures = json.loads((ROOT / 'research/RP004/RP004_FIXTURES.json').read_text())
    with (run / 'answers.jsonl').open() as answers, (run / 'collisions.jsonl').open() as pairs:
        summary = replay(answers, pairs, fixtures, config['config'])
    assert canonical(summary) == canonical(json.loads((run / 'summary.json').read_text()))
    audit = json.loads((run / 'replay.json').read_text())
    assert audit == {'status': 'PASS', 'decoder_rows_verified': 864, 'truth_queries_verified': 216,
        'collision_comparisons_verified': 60, 'disclosed_calibration': {'cases': 6, 'cells': 216,
        'collision_controls': 3, 'correct': 119, 'unknown': 97, 'wrong': 0}, 'coverage_order_verified': True,
        'all_projections_truth_answers_counts_and_collision_witnesses_match': True}
    return summary


if __name__ == '__main__':
    summary = check_run(ROOT / 'research/RP004/runs/audit-20261011-001')
    print(f"RP004 audit: {summary['decoder_rows']} decoder rows and {summary['collision_comparisons']} collision comparisons independently replayed; 6 output and 15 input hashes verified")
