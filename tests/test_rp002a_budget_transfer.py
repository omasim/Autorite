"""Feasibility-mode software fixtures only; no research model optimization."""
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
import importlib.util,json,tempfile,unittest
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('convergence',ROOT/'packages/rp002a/convergence.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)

class BudgetTransfer(unittest.TestCase):
 def setUp(self):self.path,self.plan,self.base=c.load_plan(3)
 def rows(self):
  return [{'world':w,'replicate':0,'model':m,'assessment_episode_mean_log_loss':1+delta} for w in self.plan['world_replicates'] for m,delta in [('B0',0),('B1',-.1),('B2',-.2),('B3',-.3)]]
 def test_one_replicate_output_has_no_variance_statistics(self):
  x=c.summarize(self.rows(),self.plan,self.base)
  self.assertEqual(x['mode'],'exploratory-budget-transfer');self.assertEqual(len(x['model_assessment']),12)
  self.assertEqual(len(x['paired_contrasts']),7)
  contrast=next(r for r in x['paired_contrasts'] if r['contrast']=='E1:B2-B1')
  self.assertEqual(contrast['n'],1);self.assertAlmostEqual(contrast['paired_difference'],-.1)
  forbidden={'sample_sd','leave_one_out_sd_range','confidence_interval','p_value','model_variability','paired_contrast_variability'}
  for r in x['model_assessment']+x['paired_contrasts']:self.assertFalse(forbidden & set(r))
  self.assertFalse(forbidden & set(x))
 def test_incomplete_duplicate_or_nonfinite_records_rejected(self):
  rows=self.rows()
  bad=[rows[:-1],rows+[rows[0]],rows[:-1]+[dict(rows[-1],assessment_episode_mean_log_loss=float('nan'))]]
  for r in bad:
   with self.assertRaises(ValueError):c.summarize(r,self.plan,self.base)
 def test_unapproved_execution_creates_no_directory(self):
  p=dict(self.plan,frozen=False,execution_authorized=False,run_id='unauthorized-transfer-fixture')
  run=ROOT/'research/RP002A/runs'/p['run_id'];self.assertFalse(run.exists())
  with self.assertRaises(PermissionError):c.execute(self.path,p,self.base,p['run_id'])
  self.assertFalse(run.exists())
 def test_previous_approvals_cannot_authorize_transfer(self):
  with tempfile.TemporaryDirectory() as tmp,patch.object(c,'ROOT',Path(tmp)):
   for name in ['CONVERGENCE_APPROVAL.json','CONVERGENCE_002_APPROVAL.json','BOOTSTRAP_APPROVAL.json']:
    f=Path(tmp)/'docs/research'/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_text('{"approved":true}')
   with self.assertRaisesRegex(PermissionError,'Separate convergence approval'):
    c.authorization(self.path,dict(self.plan,frozen=True,execution_authorized=True))
   self.assertEqual(c.stage_paths(self.plan)[1],'docs/research/BUDGET_TRANSFER_APPROVAL.json')
 def test_mode_and_replicate_scope_are_not_interchangeable(self):
  for changes in [{'mode':'exploratory-convergence'},{'world_replicates':{'E0':2,'E1':1,'E2':1}}]:
   with self.assertRaises(ValueError):c.validate_plan(dict(self.plan,**changes),self.base)
 def test_memory_units_are_explicit_and_normalized(self):
  with patch.object(c.resource,'getrusage',return_value=SimpleNamespace(ru_maxrss=1234)):
   for platform,unit,factor in [('darwin','bytes',1),('linux','KiB',1024)]:
    with patch.object(c.sys,'platform',platform):
     x=c.peak_memory();self.assertEqual(x['raw_unit'],unit);self.assertEqual(x['bytes'],1234*factor)
   with patch.object(c.sys,'platform','unknown'):
    with self.assertRaises(ValueError):c.peak_memory()
 def test_partial_failure_preserves_memory_metadata_without_summary(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);basefile=root/self.plan['base_configuration'];basefile.parent.mkdir(parents=True);basefile.write_bytes((ROOT/self.plan['base_configuration']).read_bytes())
   p=dict(self.plan,train_episodes=3,validation_episodes=3,assessment_episodes=3)
   planpath=root/'plan.json';planpath.write_text(json.dumps(p));arrays=[]
   def generate(*args):
    a=np.full((3,129),len(arrays),dtype=np.int64);arrays.append(a);return a
   def train(model,train,validation,*args):
    self.assertIs(train,arrays[0]);self.assertIs(validation,arrays[1]);self.assertIsNot(train,arrays[2]);raise RuntimeError('synthetic interrupted fit')
   with patch.object(c,'ROOT',root),patch.object(c,'authorization',return_value='fixture'),patch.object(c.e,'generate',side_effect=generate),patch.object(c.e,'train_model',side_effect=train):
    with self.assertRaisesRegex(RuntimeError,'synthetic interrupted'):c.execute(planpath,p,self.base,p['run_id'])
   dest=root/'research/RP002A/runs'/p['run_id'];m=json.loads((dest/'manifest.json').read_text())
   self.assertIn('failure.txt',m['outputs']);self.assertFalse((dest/'summary.json').exists())
   self.assertGreater(m['environment']['peak_process_resident_memory']['bytes'],0)
