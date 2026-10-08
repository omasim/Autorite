"""Plan an isolated pilot; execution requires explicit pre-outcome approval files."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,platform,subprocess,sys,time,traceback
import numpy as np
import torch
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('engine',ROOT/'packages/rp002a/engine.py');e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load_plan():
 path=ROOT/'research/RP002A/PILOT_PLAN.json';plan=json.loads(path.read_text());base=json.loads((ROOT/plan['base_configuration']).read_text())
 return path,plan,base

def authorization(path,plan):
 if plan.get('frozen') is not True or plan.get('execution_authorized') is not True:raise PermissionError('Pilot is not frozen/authorized; no run created.')
 approval=ROOT/'docs/research/BOOTSTRAP_APPROVAL.json'
 if not approval.is_file():raise PermissionError('Audited bootstrap approval is missing; no run created.')
 d=json.loads(approval.read_text());head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 source=d.get('source_commit','')
 if d.get('approved') is not True or d.get('baseline_manifest_sha256')!=digest(ROOT/'baseline/SNAPSHOT.json') or d.get('pilot_plan_sha256')!=digest(path) or len(source)!=40:raise PermissionError('Approval does not match baseline, pilot plan and source commit.')
 if subprocess.run(['git','merge-base','--is-ancestor',source,head],cwd=ROOT,capture_output=True).returncode:raise PermissionError('Approved source is not in current history.')
 changed=subprocess.check_output(['git','diff','--name-only',source,head],cwd=ROOT,text=True).splitlines()
 if set(changed)-{'docs/research/BOOTSTRAP_APPROVAL.json'}:raise PermissionError('Source changed after approval; a new source review is required.')
 if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip():raise PermissionError('Execution requires a clean source checkout.')
 if np.__version__!='2.0.2' or torch.__version__.split('+')[0]!='2.8.0':raise PermissionError('Installed libraries differ from the pinned research environment.')
 return head

def execute(path,plan,base,run_id):
 head=authorization(path,plan)  # Gate before creating files or accessing pilot outcomes.
 if not run_id or not all(c.isalnum() or c in '-_' for c in run_id):raise ValueError('Invalid run ID')
 dest=ROOT/'research/RP002A/runs'/run_id;dest.mkdir(parents=True,exist_ok=False)
 torch.set_num_threads(base['resource_cap']['threads']);torch.use_deterministic_algorithms(True)
 deadline=time.monotonic()+plan['max_training_wall_seconds'];results=[];schedule={}
 try:
  for world,law in base['worlds'].items():
   datasets={}
   for split,n in [('train',plan['train_episodes']),('validation',plan['validation_episodes']),('diagnostic',plan['diagnostic_episodes'])]:
    s=e.seed(plan['version'],world,0,split,'data');schedule[f'{world}/{split}/data']=s
    datasets[split]=e.generate(law['flip_probability'],law['erasure_probability'],n,plan['episode_observations'],s)
    np.save(dest/f'{world}-{split}.npy',datasets[split],allow_pickle=False)
   trace_config=dict(base['optimization']);trace_config['max_epochs']=plan['max_epochs']
   diagnostic=datasets['diagnostic'];predictions={}
   table=e.fit_b0(datasets['train'],base['B0']['laplace_alpha']);predictions['B0']=table[diagnostic[:,:-1]]
   np.save(dest/f'{world}-B0-table.npy',table,allow_pickle=False)
   for name,constructor in [('B1',lambda:e.FiniteHistory(base['B1']['window'],base['B1']['hidden_units'])),('B2',lambda:e.RecursiveState(base['B2']['state_dimension']))]:
    init=e.seed(plan['version'],world,0,'train',name+'-initialization');batch=e.seed(plan['version'],world,0,'train',name+'-batch-order');schedule[f'{world}/{name}/initialization']=init;schedule[f'{world}/{name}/batch-order']=batch
    torch.manual_seed(init);model=constructor()
    trace=e.train_model(model,datasets['train'],datasets['validation'],trace_config,batch,deadline)
    torch.save(model.state_dict(),dest/f'{world}-{name}.pt');(dest/f'{world}-{name}-trace.json').write_text(json.dumps(trace,indent=2)+'\n')
    predictions[name]=e.probabilities(model,diagnostic[:,:-1])
   predictions['B3']=e.oracle(diagnostic[:,:-1],law['flip_probability'],law['erasure_probability'])
   for name,p in predictions.items():
    values=e.losses(p,diagnostic[:,1:],base['probability_clip']);np.save(dest/f'{world}-{name}-probabilities.npy',p,allow_pickle=False);np.save(dest/f'{world}-{name}-losses.npy',values,allow_pickle=False)
    results.append(dict(world=world,model=name,diagnostic_mean_log_loss=float(values.mean()),interpretation='Exploratory engineering diagnostic only'))
  (dest/'diagnostics.json').write_text(json.dumps(results,indent=2)+'\n')
 except Exception:
  (dest/'failure.txt').write_text(traceback.format_exc());raise
 finally:
  environment={'python':platform.python_version(),'platform':platform.platform(),'machine':platform.machine(),'numpy':np.__version__,'torch':torch.__version__,'source_commit':head,'mode':'exploratory-pilot','pilot_plan_sha256':digest(path),'base_configuration_sha256':digest(ROOT/plan['base_configuration'])}
  outputs={p.name:digest(p) for p in sorted(dest.iterdir()) if p.is_file()}
  manifest=dict(configuration={'plan':plan,'base':base},seeds=schedule or {'failure':'before seed schedule creation'},environment=environment,outputs=outputs)
  (dest/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 return dest

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--execute',action='store_true');parser.add_argument('--run-id');args=parser.parse_args();path,plan,base=load_plan()
 if args.execute:
  try:print(execute(path,plan,base,args.run_id))
  except PermissionError as ex:sys.exit(str(ex))
 else:print(json.dumps({'mode':'plan-only','plan':plan,'plan_sha256':digest(path),'base_configuration_sha256':digest(ROOT/plan['base_configuration']),'run_created':False},indent=2))
