"""Validate the consumed RP006 authorization and preserved recorded attempt."""
import ast
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def check():
    plan = json.loads((ROOT / 'research/RP006/ENTRY_PLAN.json').read_text())
    cycle = json.loads((ROOT / 'cycles/cycle-02/manifest.json').read_text())
    freeze_path = ROOT / 'research/RP006/EXECUTION_FREEZE.json'
    auth_path = ROOT / 'research/RP006/EXECUTION_AUTHORIZATION.json'
    test_path = ROOT / 'research/RP006/audit-001/RECORD.md'
    decision_path = ROOT / 'graph/decisions/D-0016.md'
    if not all(path.is_file() for path in (freeze_path, auth_path, test_path, decision_path)):
        raise ValueError('Accepted source freeze, Test, checkpoint Decision and one-run authorization are required')
    attempts = ROOT / 'research/RP006/attempts'
    authorization = json.loads(auth_path.read_text())
    freeze = json.loads(freeze_path.read_text())
    if set(p.name for p in attempts.iterdir() if p.is_dir()) != {authorization['attempt_id']}:
        raise ValueError('Only the D-0016 authorized recorded attempt may be present')
    if plan['source_frozen'] is not False or plan['execution_authorized'] is not False:
        raise ValueError('Immutable entry blueprint must remain a preparation plan')
    resolved = {item['key'] for item in cycle['obligations'] if item['resolved']}
    if cycle['status'] != 'OPEN' or resolved != {'rp006', 'checkpoint-a', 'graph-review', 'synthesis', 'foundation'}:
        raise ValueError('Cycle 02 must remain open with only the RP006 package, checkpoint, graph, synthesis and foundation reviews accepted')
    auth = json.loads(auth_path.read_text())
    if freeze.get('checkpoint_decision_ref') != 'D-0016' or freeze.get('test_ref') != 'TST-RP006001':
        raise ValueError('Execution freeze points to the wrong Test or checkpoint')
    if auth.get('checkpoint_decision_ref') != freeze['checkpoint_decision_ref'] or auth.get('test_ref') != freeze['test_ref']:
        raise ValueError('One-attempt authorization differs from the source freeze')
    if auth.get('execution_authorized') is not True or auth.get('status') != 'ACCEPTED':
        raise ValueError('D-0016 must authorize exactly the frozen attempt')
    for relative, checksum in freeze['input_sha256'].items():
        committed = subprocess.check_output(['git', 'show', freeze['source_commit'] + ':' + relative], cwd=ROOT)
        if __import__('hashlib').sha256(committed).hexdigest() != checksum:
            raise ValueError('Frozen source commit hash mismatch: ' + relative)
    decision = decision_path.read_text()
    review = (ROOT / 'research/RP006/RP006_PREEXECUTION_REVIEW.md').read_text()
    if 'status: ACTIVE' not in decision or 'authorizes one recorded attempt' not in decision:
        raise ValueError('D-0016 must accept the actual pre-execution checkpoint and bounded run')
    if 'authorizes no recorded attempt' in review or 'D-0016' not in review:
        raise ValueError('Pre-execution review is not bound to the accepted checkpoint')
    worker_path = ROOT / 'research/RP006/recorded_worker.py'
    worker = ast.parse(worker_path.read_text())
    imported = set()
    for node in ast.walk(worker):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split('.')[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split('.')[0])
    if imported & {'socket', 'urllib', 'http', 'requests', 'multiprocessing', 'subprocess'}:
        raise ValueError('Worker imports a network or child-process facility')
    text = worker_path.read_text()
    if "sys.addaudithook(no_network_or_children)" not in text or "answer != 'OK\\n'" not in text:
        raise ValueError('Worker must block at each supervisor guard lease')
    outputs = plan['outputs']
    expected = {'truth.jsonl', 'projections.jsonl', 'pairs.jsonl', 'conflicts.jsonl',
                'certificates.json', 'summary.json', 'timing.json', 'replay.json'}
    if set(outputs) != expected:
        raise ValueError('Recorded attempt output inventory differs from accepted protocol')
    from importlib.util import spec_from_file_location, module_from_spec
    spec = spec_from_file_location('rp006_audit_gate', ROOT / 'scripts/check-rp006-audit.py')
    audit = module_from_spec(spec)
    spec.loader.exec_module(audit)
    audit.check()
    print('PASS: RP006 one-attempt authorization consumed; preserved output verified; CI created no run.')


if __name__ == '__main__':
    check()
