import unittest,sys,tempfile,time,json
from pathlib import Path
import numpy as np
from scipy.stats import t
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from packages.rp002a import inference as i,pipeline as p,calibration as c
class Inference(unittest.TestCase):
 def test_interval_paired_training_units(self):
  values=[-.03,-.029,-.031,-.028,-.032];r=i.interval(values)
  self.assertEqual(r['n'],5);self.assertAlmostEqual(r['half_width'],2*t.ppf(1-.05/14,4)*np.std(values,ddof=1)/np.sqrt(5))
 def test_strict_decision_boundaries(self):
  self.assertEqual(i.decision([-.03,-.01],'benefit'),'indeterminate');self.assertEqual(i.decision([-.03,-.011],'benefit'),'benefit');self.assertEqual(i.decision([-.01,.009],'equivalence'),'indeterminate');self.assertEqual(i.decision([-.009,.009],'equivalence'),'equivalent')
 def test_invalid_or_zero_variance(self):
  for x in [[1],[[1,2],[3,4]],[1,np.nan],[1,1]]:
   with self.assertRaises(ValueError):i.interval(x)
 def test_secondary_known_probabilities_and_empty_stratum(self):
  r=i.secondary(np.array([[[1.,0,0],[.2,.8,0]]]),np.array([[0,1]]),np.array([[0,1]]),1e-8)
  self.assertAlmostEqual(r['brier_score'],.04);self.assertEqual(r['conditioned']['erasure_current']['log_loss'],None);self.assertEqual(sum(x['timepoints'] for x in r['calibration_bins']),2)
 def test_no_aggregate_for_partial_or_duplicate_records(self):
  base={'worlds':{'E0':{}},'primary_comparisons':['E0:B1-B0']}
  with self.assertRaises(ValueError):p.summarize([],5,base,'variance')
 def test_missing_approval_gate(self):
  with self.assertRaises(PermissionError):p.authorization('__test_missing__',p.CONFIRM,{'frozen':True,'execution_authorized':True})
 def test_synthetic_laws_and_deadline_no_model_training(self):
  rng=np.random.default_rng(1)
  for law in ['normal','centered-gamma2','standardized-t5']:self.assertEqual(c.noise(rng,law,(2,3)).shape,(2,3))
  with tempfile.TemporaryDirectory() as tmp:
   with self.assertRaises(TimeoutError):c.execute(json.loads(p.PLAN.read_text()),Path(tmp),time.monotonic()-1)
 def test_count_rule_only_variance_and_eligible_counts(self):
  plan=json.loads(p.PLAN.read_text());r=i.select_count([.0001]*7,[20,30,50],plan);self.assertEqual(r['selected_n'],20)
  with self.assertRaises(ValueError):i.select_count([.0001]*7,[],plan)
