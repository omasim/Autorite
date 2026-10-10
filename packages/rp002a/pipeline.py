"""Separately frozen statistical stages and immutable compressed artifacts."""
from pathlib import Path
import hashlib,importlib.util,json,platform,subprocess,sys,time,traceback
import numpy as np
import scipy
import torch
from . import inference,calibration
from .budget import WallBudget
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('convergence',ROOT/'packages/rp002a/convergence.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c);e=c.e
PLAN=ROOT/'research/RP002A/STATISTICAL_PIPELINE_PLAN.json'
CONFIRM=ROOT/'research/RP002A/CONFIRMATORY_CONFIG.json'
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load(stage):
 path=CONFIRM if stage=='confirmation' else PLAN
 p=json.loads(path.read_text());base=json.loads((ROOT/p['base_configuration']).read_text())
 if p['base_configuration_sha256']!=digest(ROOT/p['base_configuration']):raise ValueError('Base proposal changed')
 return path,p,base

def authorization(stage,path,plan):
 approval=ROOT/f'docs/research/{stage.upper()}_APPROVAL.json'
 if not approval.is_file() or plan.get('frozen') is not True or plan.get('execution_authorized') is not True:raise PermissionError('Separately bound stage approval missing')
 a=json.loads(approval.read_text());head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();anchor=a['source_commit']
 if not a['approved'] or a['stage']!=stage or a['plan_sha256']!=digest(path) or a['baseline_manifest_sha256']!=digest(ROOT/'baseline/SNAPSHOT.json'):raise PermissionError('Approval binding differs')
 if subprocess.run(['git','merge-base','--is-ancestor',anchor,head],cwd=ROOT,capture_output=True).returncode:raise PermissionError('Source ancestry differs')
 changed=subprocess.check_output(['git','diff','--name-only',anchor,head],cwd=ROOT,text=True).splitlines()
 if set(changed)-{str(approval.relative_to(ROOT))}:raise PermissionError('Source changed after approval anchor')
 if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip():raise PermissionError('Clean execution source required')
 actual=dict(python=platform.python_version(),numpy=np.__version__,torch=torch.__version__.split('+')[0],scipy=scipy.__version__,platform=sys.platform,machine=platform.machine(),device='CPU')
 if actual!=plan['environment']:raise PermissionError('Pinned stage environment differs')
 return head,approval,a

def seeds(version,n,base):
 s={}
 for w in sorted(base['worlds']):
  for r in range(n):
   for split in ['train','validation','assessment']:s[f'{w}/{r}/{split}/data']=e.seed(version,w,r,split,'data')
   for model in ['B1','B2']:
    for purpose in ['initialization','batch-order']:s[f'{w}/{r}/{model}/{purpose}']=e.seed(version,w,r,'train',model+'-'+purpose)
 if len(set(s.values()))!=len(s):raise ValueError('Seed collision')
 return s

def trace_summary(trace,training):return c.trace_summary(trace,{**training,'version':c.STAGES[2][0]})
def summarize(rows,n,base,stage,inflation=2,margin=.01,kinds=None):
 expected={(w,r,m) for w in base['worlds'] for r in range(n) for m in ['B0','B1','B2','B3']}
 keys=[(x['world'],x['replicate'],x['model']) for x in rows]
 if len(keys)!=len(set(keys)) or set(keys)!=expected:raise ValueError('Incomplete stage: no aggregate decisions')
 by={(x['world'],x['replicate'],x['model']):x for x in rows};contrasts=[]
 for i,label in enumerate(base['primary_comparisons']):
  w,pair=label.split(':');a,b=pair.split('-');values=[by[w,r,a]['assessment_episode_mean_log_loss']-by[w,r,b]['assessment_episode_mean_log_loss'] for r in range(n)]
  item=dict(contrast=label,**c.sample_stats(values))
  if stage=='confirmation':
   ci=inference.interval(values,inflation=inflation);item.update(ci);item['decision_kind']=kinds[i];item['decision']=inference.decision(ci['interval'],kinds[i],margin)
  contrasts.append(item)
 warnings=[{'world':x['world'],'replicate':x['replicate'],'model':x['model']} for x in rows if x['trace_summary'] and (x['trace_summary']['best_in_final_cap_window'] or x['trace_summary']['late_improvement_flag'] or x['trace_summary']['secondary_last_five']['improvement_flag'])]
 return dict(mode=stage,training_replicates_per_world=n,units=3*n,learned_fits=6*n,contrasts=contrasts,trace_warnings=warnings,interpretation='Fixed-budget algorithm comparison; trace warnings limit optimization claims, not the definition of this algorithm. Conditional normal-theory intervals are not distribution-free; no universal history or recurrence-necessity claim.')

def train_stage(dest,plan,base,stage,deadline,budget_check=None):
 if stage=='variance':p=plan['variance'];n=p['replicates'];training=plan['training'];kinds=None
 else:p=plan;n=p['replicates'];training=p['training'];kinds=p['decision_kinds']
 s=seeds(p['version'],n,base);rows=[]
 torch.set_num_threads(training['threads']);torch.use_deterministic_algorithms(True)
 opt={**base['optimization'],'max_epochs':training['max_epochs'],'early_stopping_patience':training['early_stopping_patience']}
 for w,law in sorted(base['worlds'].items()):
  for r in range(n):
   if time.monotonic()>=deadline or (budget_check is not None and budget_check()):raise TimeoutError('Stage allowance exhausted')
   stem=f'{w}-r{r:02d}';data={split:e.generate(law['flip_probability'],law['erasure_probability'],training[split+'_episodes'],training['episode_observations'],s[f'{w}/{r}/{split}/data']) for split in ['train','validation','assessment']}
   np.savez_compressed(dest/f'{stem}-datasets.npz',**{k:v.astype(np.uint8) for k,v in data.items()})
   table=e.fit_b0(data['train'],base['B0']['laplace_alpha']);np.save(dest/f'{stem}-B0-table.npy',table,allow_pickle=False)
   probs={'B0':table[data['assessment'][:,:-1]]};traces={}
   for model_name in ['B1','B2']:
    if time.monotonic()>=deadline or (budget_check is not None and budget_check()):raise TimeoutError('Stage allowance exhausted')
    torch.manual_seed(s[f'{w}/{r}/{model_name}/initialization']);model=e.FiniteHistory(base['B1']['window'],base['B1']['hidden_units']) if model_name=='B1' else e.RecursiveState(base['B2']['state_dimension'])
    started=time.time();trace=e.train_model(model,data['train'],data['validation'],opt,s[f'{w}/{r}/{model_name}/batch-order'],deadline,budget_check=budget_check)
    traces[model_name]={**trace_summary(trace,training),'fit_wall_seconds':max(0,time.time()-started)}
    (dest/f'{stem}-{model_name}-trace.json').write_text(json.dumps(trace,indent=2)+'\n');torch.save(model.state_dict(),dest/f'{stem}-{model_name}.pt')
    probs[model_name]=e.probabilities(model,data['assessment'][:,:-1])
   probs['B3']=e.oracle(data['assessment'][:,:-1],law['flip_probability'],law['erasure_probability'])
   arrays={};metrics={};losses={name:e.losses(p,data['assessment'][:,1:],base['probability_clip']) for name,p in probs.items()}
   for name,p in probs.items():
    arrays[name+'-probabilities']=p;arrays[name+'-losses']=losses[name]
    rows.append(dict(world=w,replicate=r,model=name,assessment_episode_mean_log_loss=float(losses[name].mean()),trace_summary=traces.get(name)))
    metrics[name]=inference.secondary(p,data['assessment'][:,1:],data['assessment'][:,:-1],base['probability_clip']);metrics[name]['gap_to_B3']=float((losses[name]-losses['B3']).mean())
   np.savez_compressed(dest/f'{stem}-assessment.npz',**arrays);(dest/f'{stem}-secondary.json').write_text(json.dumps(metrics,indent=2)+'\n')
   (dest/'replicates.json').write_text(json.dumps(rows,indent=2)+'\n');(dest/'progress.json').write_text(json.dumps({'completed_units':len(rows)//4,'total_units':3*n})+'\n')
   if time.monotonic()>=deadline or (budget_check is not None and budget_check()):raise TimeoutError('Stage allowance exhausted')
 (dest/'summary.json').write_text(json.dumps(summarize(rows,n,base,stage,inflation=plan.get('inflation',2),margin=plan.get('margin',.01),kinds=kinds),indent=2)+'\n')
 return s

def execute(stage):
 if stage not in ['calibration','variance','confirmation']:raise ValueError('Unknown stage')
 path,p,base=load(stage);head,approval,a=authorization(stage,path,p)
 spec=p if stage=='confirmation' else p[stage];run_id=spec['run_id']
 if a['run_id']!=run_id:raise PermissionError('Wrong one-run authorization')
 if stage=='variance':
  cal=ROOT/'research/RP002A/runs'/p['calibration']['run_id']/'summary.json'
  if not cal.is_file() or not json.loads(cal.read_text())['eligible_counts']:raise PermissionError('Calibration gate not met')
 if stage=='confirmation':
  for relative,h in p['dependency_sha256'].items():
   if digest(ROOT/relative)!=h:raise PermissionError('Design dependency changed')
 dest=ROOT/'research/RP002A/runs'/run_id;dest.mkdir(parents=True,exist_ok=False);budget=WallBudget(spec['max_wall_seconds']);deadline=budget.started_monotonic+spec['max_wall_seconds'];s=seeds(spec['version'],spec['replicates'] if stage=='variance' else p['replicates'],base) if stage!='calibration' else {}
 try:
  if stage=='calibration':
   cfg=p['calibration']
   s={f'{n}/{law}/{rho}/{fraction}':calibration.seed(f'{n}/{law}/{rho}/{fraction}') for n in cfg['candidate_n'] for law in cfg['laws'] for rho in cfg['correlations'] for fraction in cfg['within_mean_variance_fractions']}
   s.update({f'benchmark/{n}/{law}/{fraction}':calibration.seed(f'benchmark/{n}/{law}/{fraction}') for n in cfg['benchmark_n'] for law in cfg['laws'] for fraction in cfg['benchmark_fractions']})
   calibration.execute(p,dest,deadline,budget_check=budget.expired)
  else:train_stage(dest,p,base,stage,deadline,budget_check=budget.expired)
  if budget.expired():raise TimeoutError('Stage wall-time allowance exhausted before finalization')
 except BaseException:
  if (dest/'summary.json').exists():(dest/'summary.json').unlink()
  (dest/'failure.txt').write_text(traceback.format_exc());raise
 finally:
  timing=budget.timing();(dest/'timing.json').write_text(json.dumps(timing,indent=2)+'\n')
  manifest=dict(stage=stage,run_id=run_id,source_commit=head,approval_path=str(approval.relative_to(ROOT)),approval_sha256=digest(approval),plan_path=str(path.relative_to(ROOT)),plan_sha256=digest(path),plan=p,base=base,seeds=s,environment=p['environment'],elapsed_wall_seconds=timing['elapsed_wall_seconds'],peak_process_resident_memory=c.peak_memory(),outputs={f.name:digest(f) for f in sorted(dest.iterdir()) if f.is_file()})
  (dest/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 return dest
