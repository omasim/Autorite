"""Validate frozen stage definitions and immutable outputs without new fits/samples."""
import sys,json,hashlib,subprocess
from pathlib import Path
import numpy as np
import torch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from packages.rp002a import pipeline as p,inference as inf,calibration as cal
ROOT=p.ROOT
def audit(run):
 m=json.loads((run/'manifest.json').read_text());stage=m['stage'];plan=m['plan'];base=m['base']
 assert run.name==m['run_id'] and plan['frozen'] and plan['execution_authorized']
 assert set(m['outputs'])=={f.name for f in run.iterdir() if f.is_file() and f.name!='manifest.json'}
 for name,h in m['outputs'].items():assert '/' not in name and p.digest(run/name)==h
 prefix=str(run.relative_to(ROOT));history=subprocess.check_output(['git','log','--diff-filter=A','--format=%H','--',prefix+'/manifest.json'],cwd=ROOT,text=True).splitlines()
 if history:
  first=history[-1];tree=subprocess.check_output(['git','ls-tree','-r','--name-only',first,'--',prefix],cwd=ROOT,text=True).splitlines();assert set(tree)=={str(f.relative_to(ROOT)) for f in run.iterdir() if f.is_file()}
  for f in tree:assert (ROOT/f).read_bytes()==subprocess.check_output(['git','show',first+':'+f],cwd=ROOT)
 source=m['source_commit'];raw=subprocess.check_output(['git','show',source+':'+m['plan_path']],cwd=ROOT);assert hashlib.sha256(raw).hexdigest()==m['plan_sha256'] and json.loads(raw)==plan
 raw_a=subprocess.check_output(['git','show',source+':'+m['approval_path']],cwd=ROOT);a=json.loads(raw_a);assert hashlib.sha256(raw_a).hexdigest()==m['approval_sha256'] and a['stage']==stage and a['run_id']==run.name and a['approved'] and a['plan_sha256']==m['plan_sha256']
 assert a['baseline_manifest_sha256']==hashlib.sha256(subprocess.check_output(['git','show',source+':baseline/SNAPSHOT.json'],cwd=ROOT)).hexdigest()
 subprocess.check_call(['git','merge-base','--is-ancestor',a['source_commit'],source],cwd=ROOT)
 assert not set(subprocess.check_output(['git','diff','--name-only',a['source_commit'],source],cwd=ROOT,text=True).splitlines())-{m['approval_path']}
 assert hashlib.sha256(subprocess.check_output(['git','show',source+':'+plan['base_configuration']],cwd=ROOT)).hexdigest()==plan['base_configuration_sha256']
 mem=m['peak_process_resident_memory'];assert mem['bytes']==mem['raw_value']*(1 if mem['platform']=='darwin' else 1024)
 if (run/'failure.txt').exists():assert not (run/'summary.json').exists();print('PASS partial:',run.name);return
 summary=json.loads((run/'summary.json').read_text())
 if stage=='calibration':
  cfg=plan['calibration'];count=len(summary['student_t']);assert count==90
  for i,row in enumerate(summary['student_t']):
   archive=np.load(run/f'student-{i:03d}.npz',allow_pickle=False);data=archive['trials'];mean=archive['means'];sd=archive['sds'];assert mean.shape==sd.shape==(cfg['trials'],7)
   from scipy.stats import t
   width=cfg['inflation']*t.ppf(1-.05/14,row['n']-1)*sd/np.sqrt(row['n'])
   assert np.array_equal(data[:,0],np.any(np.abs(mean)>width,axis=1))
   assert np.array_equal(data[:,1],np.any(mean+width<0,axis=1))
   assert np.array_equal(data[:,2],np.any(((mean-width>0)&(mean+width<2))|((mean+width<0)&(mean-width>-2)),axis=1))
   assert np.array_equal(data[:,3],np.all((mean-width>-1)&(mean+width<1),axis=1))
   assert np.array_equal(data[:,4],np.any(np.abs(mean)>width/cfg['inflation'],axis=1))
   assert np.allclose(data[:,5],width.mean(1))
   assert data.shape==(cfg['trials'],6) and np.isfinite(data).all();failure=int(data[:,0].sum())
   assert row['coverage_failures']==failure and row['eligible_cell']==(inf.rate_upper(failure,cfg['trials'],.05/count)<=.05)
   assert np.isclose(row['mean_standardized_half_width'],data[:,5].mean())
  for i,row in enumerate(summary['bootstrap_benchmarks']):
   data=np.load(run/f'benchmark-{i:02d}.npz',allow_pickle=False)['trials'];assert data.shape==(cfg['benchmark_trials'],8)
   for j,key in enumerate(['whole_cluster','nested']):assert np.allclose(list(row[key].values()),data[:,4*j:4*j+4].mean(0))
  expected=[n for n in [20,30,50] if all(x['eligible_cell'] for x in summary['student_t'] if x['n']==n)];assert summary['eligible_counts']==expected
 else:
  n=plan['variance']['replicates'] if stage=='variance' else plan['replicates'];spec=plan['variance'] if stage=='variance' else plan;training=plan['training'];assert m['seeds']==p.seeds(spec['version'],n,base)
  rows=json.loads((run/'replicates.json').read_text());expected=p.summarize(rows,n,base,stage,plan.get('inflation',2),plan.get('margin',.01),plan.get('decision_kinds'))
  assert compare(summary,expected)
  torch.set_num_threads(training['threads'])
  for world,law in base['worlds'].items():
   for r in range(n):
    stem=f'{world}-r{r:02d}';data=np.load(run/f'{stem}-datasets.npz',allow_pickle=False);arrays=np.load(run/f'{stem}-assessment.npz',allow_pickle=False);metrics=json.loads((run/f'{stem}-secondary.json').read_text())
    for split in ['train','validation','assessment']:np.testing.assert_array_equal(data[split],p.e.generate(law['flip_probability'],law['erasure_probability'],training[split+'_episodes'],training['episode_observations'],m['seeds'][f'{world}/{r}/{split}/data']))
    table=p.e.fit_b0(data['train'],base['B0']['laplace_alpha']);np.testing.assert_array_equal(table,np.load(run/f'{stem}-B0-table.npy',allow_pickle=False))
    for model in ['B0','B1','B2','B3']:
     prob=arrays[model+'-probabilities'];loss=arrays[model+'-losses'];np.testing.assert_allclose(loss,p.e.losses(prob,data['assessment'][:,1:],base['probability_clip']),atol=1e-12)
     row=next(x for x in rows if (x['world'],x['replicate'],x['model'])==(world,r,model));assert np.isclose(row['assessment_episode_mean_log_loss'],loss.mean(),atol=1e-12)
     if model=='B0':pred=table[data['assessment'][:,:-1]]
     elif model=='B3':pred=p.e.oracle(data['assessment'][:,:-1],law['flip_probability'],law['erasure_probability'])
     else:
      trace=json.loads((run/f'{stem}-{model}-trace.json').read_text());saved=dict(row['trace_summary']);assert saved.pop('fit_wall_seconds')>=0;assert compare(saved,p.trace_summary(trace,training))
      model_obj=p.e.FiniteHistory(base['B1']['window'],base['B1']['hidden_units']) if model=='B1' else p.e.RecursiveState(base['B2']['state_dimension']);model_obj.load_state_dict(torch.load(run/f'{stem}-{model}.pt',map_location='cpu',weights_only=True));pred=p.e.probabilities(model_obj,data['assessment'][:,:-1])
     np.testing.assert_allclose(prob,pred,rtol=1e-5,atol=1e-6)
     sec=inf.secondary(prob,data['assessment'][:,1:],data['assessment'][:,:-1],base['probability_clip']);sec['gap_to_B3']=float((loss-arrays['B3-losses']).mean());assert compare(metrics[model],sec)
 print('PASS:',run.name,len(m['outputs']),'hashes and analysis/checkpoint replay; no training')
def compare(a,b):
 import importlib.util
 spec=importlib.util.spec_from_file_location('design',ROOT/'packages/rp002a/design.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d);return d.same_planning(a,b)
def check_plan():
 _,plan,base=p.load('calibration');assert plan['calibration']['trials']==20000 and plan['training']['max_epochs']==300 and plan['variance']['replicates']==5
 assert plan['confirmation_rule']['candidate_counts']==[20,30,50] and plan['confirmation_rule']['inflation']==2 and plan['confirmation_rule']['margin']==.01
 used=set()
 for f in (ROOT/'research/RP002A/runs').glob('*/manifest.json'):
  if f.parent.name not in [plan['variance']['run_id'],plan['confirmation_rule']['run_id']]:used.update(json.loads(f.read_text()).get('seeds',{}).values())
 v=set(p.seeds(plan['variance']['version'],5,base).values());confirm=set(p.seeds(plan['confirmation_rule']['version'],50,base).values());assert not v&confirm and not used&(v|confirm)
 if p.CONFIRM.exists():
  config=json.loads(p.CONFIRM.read_text());cal_s=json.loads((ROOT/'research/RP002A/runs'/plan['calibration']['run_id']/'summary.json').read_text());var_s=json.loads((ROOT/'research/RP002A/runs'/plan['variance']['run_id']/'summary.json').read_text());selected=inf.select_count([x['sample_sd'] for x in var_s['contrasts']],cal_s['eligible_counts'],plan)
  assert config['replicates']==selected['selected_n'] and config['training']==plan['training'] and config['inflation']==2 and config['margin']==.01 and config['decision_kinds']==plan['confirmation_rule']['decision_kinds'] and config['max_wall_seconds']==14400
  for relative,h in config['dependency_sha256'].items():assert p.digest(ROOT/relative)==h
 print('PASS: fixed pipeline budgets, fresh variance/confirmation namespaces; no execution')
if __name__=='__main__':
 check_plan()
 for run in sorted((ROOT/'research/RP002A/runs').iterdir()):
  if run.name.startswith(('calibration-','target-variance-','confirmatory-')):audit(run)
