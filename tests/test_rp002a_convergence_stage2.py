"""Stage-two authorization and diagnostic fixtures; no research training."""
from pathlib import Path
from unittest.mock import patch
import importlib.util,json,tempfile,unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('convergence',ROOT/'packages/rp002a/convergence.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)

class StageTwo(unittest.TestCase):
 def setUp(self):self.path,self.plan,self.base=c.load_plan(2)
 def trace(self,values):return [{'epoch':i+1,'validation_log_loss':v} for i,v in enumerate(values)]
 def test_unapproved_stage_creates_no_directory(self):
  plan=dict(self.plan,frozen=False,execution_authorized=False,run_id='unauthorized-stage2-fixture')
  run=ROOT/'research/RP002A/runs'/plan['run_id'];self.assertFalse(run.exists())
  with self.assertRaises(PermissionError):c.execute(self.path,plan,self.base,plan['run_id'])
  self.assertFalse(run.exists())
 def test_previous_stage_approval_is_insufficient(self):
  with tempfile.TemporaryDirectory() as tmp,patch.object(c,'ROOT',Path(tmp)):
   approval=Path(tmp)/'docs/research/CONVERGENCE_APPROVAL.json';approval.parent.mkdir(parents=True);approval.write_text('{"approved":true}')
   with self.assertRaisesRegex(PermissionError,'Separate convergence approval'):
    c.authorization(self.path,dict(self.plan,frozen=True,execution_authorized=True))
 def test_wrong_plan_payload_rejected_before_git_or_artifacts(self):
  with tempfile.TemporaryDirectory() as tmp,patch.object(c,'ROOT',Path(tmp)):
   path=Path(tmp)/c.STAGES[2][1];path.parent.mkdir(parents=True);path.write_text(json.dumps(self.plan))
   approval=Path(tmp)/c.STAGES[2][2];approval.parent.mkdir(parents=True);approval.write_text('{"approved":true}')
   with self.assertRaisesRegex(PermissionError,'Plan differs'):
    c.authorization(path,dict(self.plan,frozen=True,execution_authorized=True))
 def test_stage_specific_windows_and_stop_reason(self):
  d=c.trace_summary(self.trace([1-i*.002 for i in range(300)]),self.plan)
  self.assertTrue(d['best_in_final_cap_window']);self.assertTrue(d['late_improvement_flag'])
  self.assertEqual(d['stop_reason'],'epoch_cap');self.assertEqual(d['late_window_epochs'],20)
  self.assertTrue(d['secondary_last_five']['improvement_flag'])
  stopped=c.trace_summary(self.trace([1]+[1.1]*20),self.plan)
  self.assertEqual(stopped['stop_reason'],'early_stopping_patience');self.assertFalse(stopped['best_in_final_cap_window'])
  with self.assertRaisesRegex(ValueError,'Trace ended'):
   c.trace_summary(self.trace([1,.9]),self.plan)
 def test_five_epoch_secondary_is_distinct(self):
  values=[1-i*.001 for i in range(280)]+[.65]+[.7]*19
  d=c.trace_summary(self.trace(values),self.plan)
  self.assertFalse(d['late_improvement_flag']);self.assertFalse(d['secondary_last_five']['improvement_flag'])
  self.assertEqual(d['secondary_last_five']['window_epochs'],5)
 def test_stage_identity_cannot_choose_old_approval(self):
  self.assertEqual(c.stage_paths(self.plan)[1],'docs/research/CONVERGENCE_002_APPROVAL.json')
  with self.assertRaises(PermissionError):c.stage_paths(dict(self.plan,version='unknown'))
