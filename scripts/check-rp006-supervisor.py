"""Validate the accepted RP006 source-bound execution gates without running them."""
import ast
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_runner():
    spec = importlib.util.spec_from_file_location(
        'rp006_gate_check', ROOT / 'research/RP006/recorded_attempt.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check():
    plan = json.loads((ROOT / 'research/RP006/ENTRY_PLAN.json').read_text())
    cycle = json.loads((ROOT / 'cycles/cycle-02/manifest.json').read_text())
    freeze_path = ROOT / 'research/RP006/EXECUTION_FREEZE.json'
    auth_path = ROOT / 'research/RP006/EXECUTION_AUTHORIZATION.json'
    test_path = ROOT / 'research/RP006/audit-001/RECORD.md'
    decision_path = ROOT / 'graph/decisions/D-0016.md'
    if not all(path.is_file() for path in (freeze_path, auth_path, test_path, decision_path)):
        raise ValueError('Accepted source freeze, Test, checkpoint Decision and one-run authorization are required')
    if (ROOT / 'research/RP006/attempts').exists():
        raise ValueError('CI validation must not create a recorded research attempt')
    if plan['source_frozen'] is not False or plan['execution_authorized'] is not False:
        raise ValueError('Immutable entry blueprint must remain a preparation plan')
    if cycle['status'] != 'OPEN' or any(item['resolved'] for item in cycle['obligations']):
        raise ValueError('Pre-execution authorization cannot resolve Cycle 02 obligations')
    freeze = json.loads(freeze_path.read_text())
    auth = json.loads(auth_path.read_text())
    if freeze.get('checkpoint_decision_ref') != 'D-0016' or freeze.get('test_ref') != 'TST-RP006001':
        raise ValueError('Execution freeze points to the wrong Test or checkpoint')
    if auth.get('checkpoint_decision_ref') != freeze['checkpoint_decision_ref'] or auth.get('test_ref') != freeze['test_ref']:
        raise ValueError('One-attempt authorization differs from the source freeze')
    if auth.get('execution_authorized') is not True or auth.get('status') != 'ACCEPTED':
        raise ValueError('D-0016 must authorize exactly the frozen attempt')
    runner = load_runner()
    gate = runner.authorize()
    if gate['attempt_id'] != auth['attempt_id'] or gate['head'] != runner.current_commit():
        raise ValueError('Runner gate does not validate against the checked-out source')
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
    print('PASS: RP006 execution gates are source-bound and authorized for one attempt; CI created no run.')


if __name__ == '__main__':
    check()
