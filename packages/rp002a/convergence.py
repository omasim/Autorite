"""A separately gated exploratory stage; importing creates no outcomes."""
from pathlib import Path
import hashlib,importlib.util,json,platform,subprocess,sys,time,traceback
import numpy as np
import torch
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('engine',ROOT/'packages/rp002a/engine.py');e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def base_path(plan):
 path=(ROOT/plan['base_configuration']).resolve()
 if not path.is_relative_to(ROOT.resolve()) or not path.is_file():raise ValueError('Invalid base configuration path')
 return path

def load_plan():
 path=ROOT/'research/RP002A/CONVERGENCE_PLAN.json';plan=json.loads(path.read_text());base=json.loads(base_path(plan).read_text());validate_plan(plan,base);return path,plan,base

def validate_plan(plan,base):
 if plan['mode']!='exploratory-convergence' or not plan['version'] or not plan['run_id'] or not all(c.isalnum() or c in '-_' for c in plan['run_id']):raise ValueError('Invalid stage identity')
 if set(plan['world_replicates'])!=set(base['worlds']) or any(type(n) is not int or n<3 for n in plan['world_replicates'].values()):raise ValueError('Replicates must be declared for each world')
 for key in ['train_episodes','validation_episodes','assessment_episodes','episode_observations','max_epochs','early_stopping_patience','threads','max_training_wall_seconds','near_cap_last_epochs','late_trace_epochs']:
  if type(plan[key]) is not int or plan[key]<1:raise ValueError('Invalid positive budget: '+key)
 if plan['episode_observations']<2 or plan['max_epochs']<plan['late_trace_epochs'] or plan['late_trace_epochs']<2 or plan['near_cap_last_epochs']>plan['max_epochs']:raise ValueError('Invalid convergence window')
 if not np.isfinite(plan['late_improvement_threshold_nats']) or plan['late_improvement_threshold_nats']<=0:raise ValueError('Invalid diagnostic threshold')
 if plan['base_configuration_sha256']!=digest(base_path(plan)):raise ValueError('Base configuration hash differs')

def schedule(plan):
 seeds={}
 for world,n in sorted(plan['world_replicates'].items()):
  for r in range(n):
   for split in ['train','validation','assessment']:seeds[f'{world}/{r}/{split}/data']=e.seed(plan['version'],world,r,split,'data')
   for name in ['B1','B2']:
    for purpose in ['initialization','batch-order']:seeds[f'{world}/{r}/{name}/{purpose}']=e.seed(plan['version'],world,r,'train',name+'-'+purpose)
 if len(set(seeds.values()))!=len(seeds):raise ValueError('Duplicate seeds')
 return seeds

def authorization(path,plan):
 if plan.get('frozen') is not True or plan.get('execution_authorized') is not True:raise PermissionError('Convergence stage not frozen/authorized; no run created.')
 approval=ROOT/'docs/research/CONVERGENCE_APPROVAL.json'
 if not approval.is_file():raise PermissionError('Separate convergence approval is missing; no run created.')
 d=json.loads(approval.read_text());head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();source=d.get('source_commit','')
 if d.get('approved') is not True or d.get('run_id')!=plan['run_id'] or d.get('plan_sha256')!=digest(path) or d.get('baseline_manifest_sha256')!=digest(ROOT/'baseline/SNAPSHOT.json') or len(source)!=40:raise PermissionError('Approval differs from exact stage/baseline/source')
 if subprocess.run(['git','merge-base','--is-ancestor',source,head],cwd=ROOT,capture_output=True).returncode:raise PermissionError('Approved source is not in current history')
 changed=subprocess.check_output(['git','diff','--name-only',source,head],cwd=ROOT,text=True).splitlines()
 if set(changed)-{'docs/research/CONVERGENCE_APPROVAL.json'}:raise PermissionError('Source changed after approval')
 if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip():raise PermissionError('Execution requires clean checkout')
 actual={'python':platform.python_version(),'numpy':np.__version__,'torch':torch.__version__.split('+')[0],'platform':sys.platform,'machine':platform.machine(),'device':'CPU'}
 if actual!=plan['environment']:raise PermissionError('Actual environment differs from declared stage environment')
 return head

def sample_stats(values):
 a=np.asarray(values,dtype=float)
 if a.ndim!=1 or len(a)<3 or not np.isfinite(a).all():raise ValueError('Need at least three finite independent replicate means')
 loo=[float(np.delete(a,i).std(ddof=1)) for i in range(len(a))]
 return {'n':len(a),'mean':float(a.mean()),'sample_sd':float(a.std(ddof=1)),'minimum':float(a.min()),'maximum':float(a.max()),'leave_one_out_sd_range':[min(loo),max(loo)]}

def trace_summary(trace,plan):
 values=np.asarray([t['validation_log_loss'] for t in trace],dtype=float)
 if len(values)<1 or not np.isfinite(values).all() or [t['epoch'] for t in trace]!=list(range(1,len(trace)+1)) or len(values)>plan['max_epochs']:raise ValueError('Invalid training trace')
 best=int(values.argmin())+1;late=values[-plan['late_trace_epochs']:];improvement=float(late[0]-late[-1])
 capped=len(values)==plan['max_epochs'];near_cap=capped and best>plan['max_epochs']-plan['near_cap_last_epochs']
 return {'epochs_completed':len(values),'best_epoch':best,'best_validation_log_loss':float(values.min()),'final_validation_log_loss':float(values[-1]),'reached_epoch_cap':capped,'best_in_final_cap_window':near_cap,'late_window_epochs':len(late),'late_validation_improvement_nats':improvement,'late_improvement_flag':len(late)==plan['late_trace_epochs'] and improvement>plan['late_improvement_threshold_nats'],'interpretation':'Descriptive trace flags; not a convergence proof'}

def summarize(rows,plan,base):
 expected={(w,r,m) for w,n in plan['world_replicates'].items() for r in range(n) for m in ['B0','B1','B2','B3']}
 keys=[(r['world'],r['replicate'],r['model']) for r in rows]
 if len(keys)!=len(set(keys)) or set(keys)!=expected:raise ValueError('Incomplete or duplicated replicate records')
 by={(r['world'],r['replicate'],r['model']):r for r in rows};models=[];contrasts=[]
 for w,n in sorted(plan['world_replicates'].items()):
  for m in ['B0','B1','B2','B3']:models.append({'world':w,'model':m,**sample_stats([by[w,r,m]['assessment_episode_mean_log_loss'] for r in range(n)])})
 for c in base['primary_comparisons']:
  w,pair=c.split(':');a,b=pair.split('-');n=plan['world_replicates'][w]
  contrasts.append({'contrast':c,**sample_stats([by[w,r,a]['assessment_episode_mean_log_loss']-by[w,r,b]['assessment_episode_mean_log_loss'] for r in range(n)])})
 return {'mode':'exploratory-convergence','unit':'One independently trained replicate mean; episodes/timepoints are not training replicates','model_variability':models,'paired_contrast_variability':contrasts,'interpretation':'Descriptive SD and leave-one-out sensitivity only; no power estimate, inferential interval, hypothesis or equivalence decision'}

def execute(path,plan,base,run_id):
 validate_plan(plan,base);head=authorization(path,plan)
 if run_id!=plan['run_id']:raise ValueError('Approval is for one fixed run ID')
 dest=ROOT/'research/RP002A/runs'/run_id;dest.mkdir(parents=True,exist_ok=False)
 seeds=schedule(plan);rows=[];started=time.monotonic();deadline=started+plan['max_training_wall_seconds']
 def check_deadline():
  if time.monotonic()>=deadline:raise TimeoutError('Declared exploratory-stage deadline exhausted')
 try:
  torch.set_num_threads(plan['threads']);torch.use_deterministic_algorithms(True)
  for r in range(max(plan['world_replicates'].values())):
   for world,n in sorted(plan['world_replicates'].items()):
    if r>=n:continue
    check_deadline();law=base['worlds'][world];stem=f'{world}-r{r:02d}';datasets={}
    for split in ['train','validation','assessment']:
     datasets[split]=e.generate(law['flip_probability'],law['erasure_probability'],plan[split+'_episodes'],plan['episode_observations'],seeds[f'{world}/{r}/{split}/data'])
     np.save(dest/f'{stem}-{split}.npy',datasets[split],allow_pickle=False)
    table=e.fit_b0(datasets['train'],base['B0']['laplace_alpha']);np.save(dest/f'{stem}-B0-table.npy',table,allow_pickle=False)
    probabilities={'B0':table[datasets['assessment'][:,:-1]]};traces={}
    config=dict(base['optimization'],max_epochs=plan['max_epochs'],early_stopping_patience=plan['early_stopping_patience'])
    for name,constructor in [('B1',lambda:e.FiniteHistory(base['B1']['window'],base['B1']['hidden_units'])),('B2',lambda:e.RecursiveState(base['B2']['state_dimension']))]:
     check_deadline();torch.manual_seed(seeds[f'{world}/{r}/{name}/initialization']);model=constructor();fit_started=time.monotonic()
     # Only train and validation enter optimization/checkpoint selection.
     trace=e.train_model(model,datasets['train'],datasets['validation'],config,seeds[f'{world}/{r}/{name}/batch-order'],deadline)
     traces[name]={**trace_summary(trace,plan),'fit_wall_seconds':time.monotonic()-fit_started}
     torch.save(model.state_dict(),dest/f'{stem}-{name}.pt');(dest/f'{stem}-{name}-trace.json').write_text(json.dumps(trace,indent=2)+'\n')
     check_deadline();probabilities[name]=e.probabilities(model,datasets['assessment'][:,:-1])
    probabilities['B3']=e.oracle(datasets['assessment'][:,:-1],law['flip_probability'],law['erasure_probability'])
    for name,p in probabilities.items():
     losses=e.losses(p,datasets['assessment'][:,1:],base['probability_clip']);np.save(dest/f'{stem}-{name}-probabilities.npy',p,allow_pickle=False);np.save(dest/f'{stem}-{name}-losses.npy',losses,allow_pickle=False)
     rows.append({'world':world,'replicate':r,'model':name,'assessment_episode_mean_log_loss':float(losses.mean(axis=1).mean()),'trace_summary':traces.get(name)})
    (dest/'replicates.json').write_text(json.dumps(rows,indent=2)+'\n');check_deadline()
  (dest/'summary.json').write_text(json.dumps(summarize(rows,plan,base),indent=2)+'\n')
 except BaseException:
  (dest/'failure.txt').write_text(traceback.format_exc());raise
 finally:
  environment={'python':platform.python_version(),'platform':platform.platform(),'machine':platform.machine(),'numpy':np.__version__,'torch':torch.__version__,'source_commit':head,'mode':plan['mode'],'plan_sha256':digest(path),'base_configuration_sha256':digest(base_path(plan)),'elapsed_wall_seconds':time.monotonic()-started}
  manifest={'configuration':{'plan':plan,'base':base},'seeds':seeds,'environment':environment,'outputs':{p.name:digest(p) for p in sorted(dest.iterdir()) if p.is_file()}}
  (dest/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 return dest
