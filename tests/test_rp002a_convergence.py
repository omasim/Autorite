"""Software fixtures only; no convergence research is executed by these tests."""
from pathlib import Path
from unittest.mock import patch
import copy,importlib.util,json,tempfile,unittest
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('convergence',ROOT/'packages/rp002a/convergence.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
class Convergence(unittest.TestCase):
 def setUp(self):self.path,self.plan,self.base=c.load_plan()
 def test_seed_namespace_disjoint(self):
  seeds=c.schedule(self.plan);self.assertEqual(len(seeds),140)
  old=json.loads((ROOT/'research/RP002A/runs/pilot-20261008-001/manifest.json').read_text())['seeds']
  self.assertFalse(set(seeds.values()) & set(old.values()))
  confirm={c.e.seed(self.base['version'],w,r,split,p) for w in self.base['worlds'] for r in range(self.base['replicates']) for split in self.base['splits'] for p in self.base['randomness_purposes']}
  self.assertFalse(set(seeds.values()) & confirm)
 def test_fixed_unit_sample_sd(self):
  d=c.sample_stats([1,2,3]);self.assertEqual(d['n'],3);self.assertEqual(d['mean'],2);self.assertEqual(d['sample_sd'],1)
  with self.assertRaises(ValueError):c.sample_stats([1,2,float('nan')])
 def test_paired_replicate_summary_and_incomplete_refusal(self):
  rows=[]
  for w,n in self.plan['world_replicates'].items():
   for r in range(n):
    for m,delta in [('B0',0),('B1',-.2),('B2',-.3),('B3',-.4)]:rows.append({'world':w,'replicate':r,'model':m,'assessment_episode_mean_log_loss':1+r*.01+delta})
  d=c.summarize(rows,self.plan,self.base);x=next(x for x in d['paired_contrast_variability'] if x['contrast']=='E1:B2-B1')
  self.assertEqual(x['n'],10);self.assertAlmostEqual(x['mean'],-.1);self.assertAlmostEqual(x['sample_sd'],0)
  for bad in [rows[:-1],rows+[rows[0]]]:
   with self.assertRaises(ValueError):c.summarize(bad,self.plan,self.base)
 def test_trace_flags_are_descriptive_and_cap_specific(self):
  trace=[{'epoch':i+1,'validation_log_loss':1-i*.002} for i in range(50)];x=c.trace_summary(trace,self.plan)
  self.assertTrue(x['reached_epoch_cap']);self.assertTrue(x['best_in_final_cap_window']);self.assertTrue(x['late_improvement_flag'])
  self.assertFalse(c.trace_summary(trace[:5],self.plan)['best_in_final_cap_window'])
  with self.assertRaises(ValueError):c.trace_summary([{'epoch':1,'validation_log_loss':float('nan')}],self.plan)
 def test_reject_unfixed_or_invalid_budgets(self):
  for updates in [{'assessment_episodes':0},{'max_epochs':0},{'world_replicates':{'E1':10}},{'base_configuration_sha256':'changed'}]:
   with self.assertRaises(ValueError):c.validate_plan(dict(self.plan,**updates),self.base)
 def test_gate_creates_no_artifacts(self):
  plan=dict(self.plan,frozen=False,execution_authorized=False,run_id='unauthorized-convergence-fixture');run=ROOT/'research/RP002A/runs'/plan['run_id'];self.assertFalse(run.exists())
  with self.assertRaisesRegex(PermissionError,'not frozen/authorized'):c.execute(self.path,plan,self.base,plan['run_id'])
  self.assertFalse(run.exists())
 def test_first_pilot_approval_cannot_authorize_stage(self):
  with tempfile.TemporaryDirectory() as tmp,patch.object(c,'ROOT',Path(tmp)):
   old=Path(tmp)/'docs/research/BOOTSTRAP_APPROVAL.json';old.parent.mkdir(parents=True);old.write_text('{"approved":true}')
   with self.assertRaisesRegex(PermissionError,'Separate convergence approval'):
    c.authorization(self.path,dict(self.plan,frozen=True,execution_authorized=True))
 def test_fixed_run_id_before_creation(self):
  with patch.object(c,'authorization',return_value='fixture'):
   with self.assertRaisesRegex(ValueError,'one fixed run ID'):c.execute(self.path,self.plan,self.base,'unapproved-id')
 def test_optimization_sees_no_assessment_and_failure_is_preserved(self):
  # Synthetic distinct arrays in a temporary directory. No optimizer is invoked.
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);basefile=root/self.plan['base_configuration'];basefile.parent.mkdir(parents=True);basefile.write_bytes((ROOT/self.plan['base_configuration']).read_bytes())
   planpath=root/'plan.json';planpath.write_text(json.dumps(self.plan));arrays=[]
   def generate(p,q,n,length,seed):
    a=np.full((n,length),len(arrays),dtype=np.int64);arrays.append(a);return a
   def train(model,train,validation,*args):
    self.assertIs(train,arrays[0]);self.assertIs(validation,arrays[1]);self.assertIsNot(train,arrays[2]);self.assertIsNot(validation,arrays[2]);raise RuntimeError('fixture interrupted fit')
   with patch.object(c,'ROOT',root),patch.object(c,'authorization',return_value='fixture'),patch.object(c.e,'generate',side_effect=generate),patch.object(c.e,'train_model',side_effect=train):
    with self.assertRaisesRegex(RuntimeError,'fixture interrupted'):c.execute(planpath,self.plan,self.base,self.plan['run_id'])
   dest=root/'research/RP002A/runs'/self.plan['run_id'];m=json.loads((dest/'manifest.json').read_text());self.assertIn('failure.txt',m['outputs']);self.assertFalse((dest/'summary.json').exists())
   self.assertTrue((dest/'E0-r00-train.npy').exists());self.assertIn('elapsed_wall_seconds',m['environment'])
