"""Check a future feasibility pilot's scope and fresh seeds; no observations or fits."""
from pathlib import Path
import importlib.util,json
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('convergence',ROOT/'packages/rp002a/convergence.py')
c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
def check():
 path=ROOT/'research/RP002A/BUDGET_TRANSFER_PLAN.json';p=json.loads(path.read_text())
 if any(type(p[k]) is not bool for k in ['frozen','execution_authorized']) or p['frozen']!=p['execution_authorized']:
  raise ValueError('Freeze and execution flags must agree')
 if p['mode']!='exploratory-budget-transfer' or p['world_replicates']!={'E0':1,'E1':1,'E2':1}:
  raise ValueError('Pilot scope differs')
 base=json.loads(c.base_path(p).read_text());c.validate_plan(p,base)
 if c.digest(c.base_path(p))!=p['base_configuration_sha256']:raise ValueError('Base hash differs')
 for field in ['train_episodes','validation_episodes','episode_observations']:
  if p[field]!=base[field]:raise ValueError('Data size differs from target proposal')
 if p['assessment_episodes']!=base['test_episodes']:raise ValueError('Assessment size differs')
 stage=json.loads((ROOT/'research/RP002A/CONVERGENCE_002_PLAN.json').read_text())
 for field in ['max_epochs','early_stopping_patience','threads','near_cap_last_epochs','late_trace_epochs','late_improvement_threshold_nats','environment']:
  if p[field]!=stage[field]:raise ValueError('Undeclared optimization change')
 if p['max_training_wall_seconds']!=3600:raise ValueError('Pilot deadline differs')
 if not p['execution_authorized'] and (ROOT/'research/RP002A/runs'/p['run_id']).exists():raise ValueError('Unapproved pilot artifacts exist')
 seeds=c.schedule(p);used=set()
 for manifest in (ROOT/'research/RP002A/runs').glob('*/manifest.json'):
  if manifest.parent.name!=p['run_id']:used.update(json.loads(manifest.read_text())['seeds'].values())
 used.update(c.e.seed(base['version'],w,r,split,purpose) for w in base['worlds'] for r in range(base['replicates']) for split in base['splits'] for purpose in base['randomness_purposes'])
 if set(seeds.values()) & used:raise ValueError('Pilot seed collision')
 return {'mode':'plan-only','run_created':False,'seed_count':len(seeds),'plan_sha256':c.digest(path)}
if __name__=='__main__':print(json.dumps(check(),indent=2))
