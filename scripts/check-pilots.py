"""Audit saved exploratory artifacts without retraining or scientific promotion."""
from pathlib import Path
import hashlib,importlib.util,json,subprocess
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('engine',ROOT/'packages/rp002a/engine.py');e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)
for run in sorted((ROOT/'research/RP002A/runs').glob('pilot-*')):
 m=json.loads((run/'manifest.json').read_text());plan=m['configuration']['plan'];base=m['configuration']['base']
 assert m['environment']['mode']=='exploratory-pilot' and plan['mode']=='exploratory-pilot'
 assert set(m['outputs'])=={p.name for p in run.iterdir() if p.is_file() and p.name!='manifest.json'},'Untracked/missing run output'
 for name,h in m['outputs'].items():
  p=(run/name).resolve();assert p.is_relative_to(run.resolve()) and hashlib.sha256(p.read_bytes()).hexdigest()==h,'Output checksum mismatch'
 history=subprocess.check_output(['git','log','--diff-filter=A','--format=%H','--',str(run.relative_to(ROOT)/'manifest.json')],cwd=ROOT,text=True).splitlines()
 if history:
  first=history[-1];tree=subprocess.check_output(['git','ls-tree','-r','--name-only',first,'--',str(run.relative_to(ROOT))],cwd=ROOT,text=True).splitlines()
  assert set(tree)=={str(p.relative_to(ROOT)) for p in run.iterdir() if p.is_file()},'Immutable run file set changed'
  for p in tree:assert (ROOT/p).read_bytes()==subprocess.check_output(['git','show',first+':'+p],cwd=ROOT),'Immutable run changed'
 if (run/'failure.txt').exists():
  print(f'PASS: preserved failed pilot {run.name}; no outcome promotion');continue
 assert len(set(m['seeds'].values()))==len(m['seeds'])
 diagnostics=json.loads((run/'diagnostics.json').read_text());assert len(diagnostics)==12
 for world,law in base['worlds'].items():
  datasets={}
  for split,n in [('train',plan['train_episodes']),('validation',plan['validation_episodes']),('diagnostic',plan['diagnostic_episodes'])]:
   a=np.load(run/f'{world}-{split}.npy',allow_pickle=False);assert a.shape==(n,plan['episode_observations'])
   np.testing.assert_array_equal(a,e.generate(law['flip_probability'],law['erasure_probability'],n,plan['episode_observations'],m['seeds'][f'{world}/{split}/data']))
   datasets[split]=a
  diagnostic=datasets['diagnostic'];table=e.fit_b0(datasets['train'],base['B0']['laplace_alpha'])
  np.testing.assert_array_equal(table,np.load(run/f'{world}-B0-table.npy',allow_pickle=False))
  for name in ['B0','B1','B2','B3']:
   p=np.load(run/f'{world}-{name}-probabilities.npy',allow_pickle=False);loss=np.load(run/f'{world}-{name}-losses.npy',allow_pickle=False)
   assert p.shape==(plan['diagnostic_episodes'],plan['episode_observations']-1,3) and np.isfinite(p).all()
   np.testing.assert_allclose(loss,e.losses(p,diagnostic[:,1:],base['probability_clip']),atol=1e-12)
   row=next(d for d in diagnostics if d['world']==world and d['model']==name);assert np.isclose(row['diagnostic_mean_log_loss'],loss.mean(),atol=1e-12)
   if name=='B0':np.testing.assert_allclose(p,table[diagnostic[:,:-1]],atol=1e-12)
   if name=='B3':np.testing.assert_allclose(p,e.oracle(diagnostic[:,:-1],law['flip_probability'],law['erasure_probability']),atol=1e-12)
   if name in ['B1','B2']:
    trace=json.loads((run/f'{world}-{name}-trace.json').read_text());assert 0<len(trace)<=plan['max_epochs'] and all(np.isfinite(t['validation_log_loss']) for t in trace)
 print(f'PASS: {run.name}: {len(m["outputs"])} checksums, observed-data replay, B0/B3 replay and 12 loss summaries; no retraining.')
