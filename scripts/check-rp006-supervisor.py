"""Check that RP006 has an implementation gate, not an accepted execution."""
import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check():
    proposal = json.loads((ROOT / 'research/RP006/SOURCE_FREEZE_PROPOSAL.json').read_text())
    plan = json.loads((ROOT / 'research/RP006/ENTRY_PLAN.json').read_text())
    cycle = json.loads((ROOT / 'cycles/cycle-02/manifest.json').read_text())
    if any(proposal.get(key) is not False for key in
           ('source_frozen', 'execution_authorized', 'pre_execution_checkpoint_accepted')):
        raise ValueError('Preparation proposal must keep all actual-run gates false')
    if plan['source_frozen'] is not False or plan['execution_authorized'] is not False:
        raise ValueError('Immutable entry blueprint must remain a preparation plan')
    if cycle['status'] != 'OPEN' or any(item['resolved'] for item in cycle['obligations']):
        raise ValueError('Supervisor preparation cannot resolve Cycle 02 obligations')
    if any((ROOT / path).exists() for path in (
            'research/RP006/EXECUTION_FREEZE.json',
            'research/RP006/EXECUTION_AUTHORIZATION.json',
            'research/RP006/audit-001/RECORD.md',
            'research/RP006/attempts')):
        raise ValueError('No execution gate or recorded run may exist at this preparation stage')
    decision = (ROOT / 'graph/decisions/D-0015.md').read_text()
    review = (ROOT / 'research/RP006/RP006_EXECUTION_SUPERVISOR_REVIEW.md').read_text()
    if 'status: ACTIVE' not in decision or 'authorizes no recorded attempt' not in review:
        raise ValueError('D-0015 is limited to engineering preparation')
    if 'processes: 2' not in review or 'mach_continuous_time' not in review or 'CLOCK_BOOTTIME' not in review:
        raise ValueError('Reviewed two-process suspend-aware runtime profile is incomplete')
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
    print('PASS: RP006 suspend-aware supervisor prepared; no Test, source freeze, authorization or run exists.')


if __name__ == '__main__':
    check()
