"""Validate the longer-budget proposal and seed separation; never train or create data."""
from pathlib import Path
import importlib.util, json

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('convergence', ROOT / 'packages/rp002a/convergence.py')
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)

def check():
    path = ROOT / 'research/RP002A/CONVERGENCE_002_PLAN.json'
    plan = json.loads(path.read_text())
    base = json.loads(c.base_path(plan).read_text())
    c.validate_plan(plan, base)
    if plan['frozen'] is not False or plan['execution_authorized'] is not False:
        raise ValueError('This checker reviews an unfrozen, unauthorized proposal only')
    if (ROOT / 'research/RP002A/runs' / plan['run_id']).exists():
        raise ValueError('Proposal must have no run artifacts')
    prior = json.loads((ROOT / 'research/RP002A/CONVERGENCE_PLAN.json').read_text())
    changed = {k for k in plan if plan[k] != prior.get(k)}
    allowed = {'version', 'frozen', 'execution_authorized', 'run_id', 'max_epochs',
               'early_stopping_patience', 'max_training_wall_seconds',
               'near_cap_last_epochs', 'late_trace_epochs', 'purpose', 'failure_policy'}
    if set(plan) != set(prior) or changed != allowed:
        raise ValueError('Unreviewed change outside the longer-budget proposal')
    seeds = c.schedule(plan)
    used = set(c.schedule(prior).values())
    for manifest in (ROOT / 'research/RP002A/runs').glob('*/manifest.json'):
        used.update(json.loads(manifest.read_text())['seeds'].values())
    for world in base['worlds']:
        for r in range(base['replicates']):
            for split in base['splits']:
                for purpose in base['randomness_purposes']:
                    used.add(c.e.seed(base['version'], world, r, split, purpose))
    if used.intersection(seeds.values()):
        raise ValueError('New proposal seed collides with a declared or executed stage')
    return {'mode': 'plan-only', 'plan_sha256': c.digest(path),
            'seed_count': len(seeds), 'run_created': False,
            'execution_authorized': False, 'plan': plan}

if __name__ == '__main__':
    print(json.dumps(check(), indent=2))
