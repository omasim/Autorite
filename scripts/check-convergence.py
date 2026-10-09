"""Audit immutable exploratory artifacts without training or hypothesis decisions."""
from pathlib import Path
import hashlib,importlib.util,json,subprocess
import numpy as np
import torch
ROOT=Path(__file__).resolve().parents[1]
def module(name,path):
 s=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
c=module('convergence','packages/rp002a/convergence.py');design=module('design','packages/rp002a/design.py')
def audit(run):
 m=json.loads((run/'manifest.json').read_text());plan=m['configuration']['plan'];base=m['configuration']['base']
 assert set(m)=={'configuration','seeds','environment','outputs'} and m['environment']['mode']==plan['mode'] and plan['mode'] in {'exploratory-convergence','exploratory-budget-transfer'}
 assert run.name==plan['run_id'] and m['seeds']==c.schedule(plan)
 assert set(m['outputs'])=={p.name for p in run.iterdir() if p.is_file() and p.name!='manifest.json'}
 for name,h in m['outputs'].items():
  p=(run/name).resolve();assert p.is_relative_to(run.resolve()) and hashlib.sha256(p.read_bytes()).hexdigest()==h,'Run output checksum mismatch'
 prefix=str(run.relative_to(ROOT));history=subprocess.check_output(['git','log','--diff-filter=A','--format=%H','--',prefix+'/manifest.json'],cwd=ROOT,text=True).splitlines()
 if history:
  first=history[-1];tree=subprocess.check_output(['git','ls-tree','-r','--name-only',first,'--',prefix],cwd=ROOT,text=True).splitlines()
  assert set(tree)=={str(p.relative_to(ROOT)) for p in run.iterdir() if p.is_file()},'Immutable run file set changed'
  for path in tree:assert (ROOT/path).read_bytes()==subprocess.check_output(['git','show',first+':'+path],cwd=ROOT),'Immutable run changed'
 plan_relative,approval_relative=c.stage_paths(plan)
 source=m['environment']['source_commit'];saved_plan=subprocess.check_output(['git','show',source+':'+plan_relative],cwd=ROOT)
 saved_base=subprocess.check_output(['git','show',source+':'+plan['base_configuration']],cwd=ROOT)
 approved=json.loads(subprocess.check_output(['git','show',source+':'+approval_relative],cwd=ROOT))
 assert plan['frozen'] is True and plan['execution_authorized'] is True and approved['approved'] is True
 assert approved['run_id']==plan['run_id'] and approved['plan_sha256']==m['environment']['plan_sha256']
 assert approved['baseline_manifest_sha256']==hashlib.sha256(subprocess.check_output(['git','show',source+':baseline/SNAPSHOT.json'],cwd=ROOT)).hexdigest()
 anchor=approved['source_commit'];subprocess.check_call(['git','merge-base','--is-ancestor',anchor,source],cwd=ROOT)
 changed=subprocess.check_output(['git','diff','--name-only',anchor,source],cwd=ROOT,text=True).splitlines()
 assert not set(changed)-{approval_relative},'Unapproved source changes'
 assert hashlib.sha256(saved_plan).hexdigest()==m['environment']['plan_sha256'] and json.loads(saved_plan)==plan
 assert hashlib.sha256(saved_base).hexdigest()==m['environment']['base_configuration_sha256']==plan['base_configuration_sha256'] and json.loads(saved_base)==base
 if c.is_transfer(plan):
  memory=m['environment']['peak_process_resident_memory'];assert memory['metric']=='RUSAGE_SELF.ru_maxrss'
  assert memory['platform']==plan['environment']['platform'] and type(memory['raw_value']) is int and memory['raw_value']>0
  factor=1 if memory['platform']=='darwin' else 1024
  assert memory['raw_unit']==('bytes' if factor==1 else 'KiB') and memory['bytes']==memory['raw_value']*factor
 if (run/'failure.txt').exists():
  assert not (run/'summary.json').exists();print(f'PASS: {run.name}: immutable partial failure; no aggregate inference');return
 rows=json.loads((run/'replicates.json').read_text());assert design.same_planning(json.loads((run/'summary.json').read_text()),c.summarize(rows,plan,base))
 torch.set_num_threads(plan['threads'])
 for world,n in plan['world_replicates'].items():
  law=base['worlds'][world]
  for r in range(n):
   stem=f'{world}-r{r:02d}';datasets={}
   for split in ['train','validation','assessment']:
    a=np.load(run/f'{stem}-{split}.npy',allow_pickle=False);assert a.shape==(plan[split+'_episodes'],plan['episode_observations'])
    np.testing.assert_array_equal(a,c.e.generate(law['flip_probability'],law['erasure_probability'],len(a),a.shape[1],m['seeds'][f'{world}/{r}/{split}/data']));datasets[split]=a
   assessment=datasets['assessment'];table=c.e.fit_b0(datasets['train'],base['B0']['laplace_alpha']);np.testing.assert_array_equal(table,np.load(run/f'{stem}-B0-table.npy',allow_pickle=False))
   for name in ['B0','B1','B2','B3']:
    p=np.load(run/f'{stem}-{name}-probabilities.npy',allow_pickle=False);loss=np.load(run/f'{stem}-{name}-losses.npy',allow_pickle=False)
    np.testing.assert_allclose(loss,c.e.losses(p,assessment[:,1:],base['probability_clip']),atol=1e-12)
    row=next(x for x in rows if (x['world'],x['replicate'],x['model'])==(world,r,name));assert np.isclose(row['assessment_episode_mean_log_loss'],loss.mean(axis=1).mean(),atol=1e-12)
    if name=='B0':np.testing.assert_allclose(p,table[assessment[:,:-1]],atol=1e-12)
    elif name=='B3':np.testing.assert_allclose(p,c.e.oracle(assessment[:,:-1],law['flip_probability'],law['erasure_probability']),atol=1e-12)
    else:
     trace=json.loads((run/f'{stem}-{name}-trace.json').read_text());summary=dict(row['trace_summary']);assert summary.pop('fit_wall_seconds')>=0
     assert design.same_planning(summary,c.trace_summary(trace,plan))
     model=c.e.FiniteHistory(base['B1']['window'],base['B1']['hidden_units']) if name=='B1' else c.e.RecursiveState(base['B2']['state_dimension'])
     model.load_state_dict(torch.load(run/f'{stem}-{name}.pt',map_location='cpu',weights_only=True))
     np.testing.assert_allclose(p,c.e.probabilities(model,assessment[:,:-1]),rtol=1e-5,atol=1e-6)
 print(f'PASS: {run.name}: {len(m["outputs"])} immutable hashes, seeds/data/reference/checkpoint replay and replicate-level summaries; no training.')
if __name__=='__main__':
 runs=sorted(p for p in (ROOT/'research/RP002A/runs').iterdir() if p.is_dir() and p.name.startswith(('convergence-','budget-transfer-')))
 for run in runs:audit(run)
 if not runs:print('PASS: no convergence runs yet; no outcomes created by validation.')
