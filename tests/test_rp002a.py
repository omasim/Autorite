"""Deterministic software fixtures, not scientific model-comparison runs."""
import importlib.util,itertools,time,unittest
from pathlib import Path
import numpy as np
import torch
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('rp002a',ROOT/'packages/rp002a/engine.py');e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)
torch.set_num_threads(2)
class Acceptance(unittest.TestCase):
 def test_seed_schedule_disjoint(self):
  seeds=[e.seed('proposal-0.1',w,r,s,p) for w,r,s,p in itertools.product(['E0','E1','E2'],range(5),['train','validation','test'],['data','initialization','batch_order','bootstrap'])]
  self.assertEqual(len(seeds),len(set(seeds)))
 def test_generator_reproducible(self):
  a=e.generate(.1,.5,8,9,42);np.testing.assert_array_equal(a,e.generate(.1,.5,8,9,42));self.assertEqual(a.shape,(8,9))
 def test_e0_never_erases(self):self.assertFalse((e.generate(.1,0,16,16,42)==2).any())
 def test_filter_matches_independent_enumeration(self):
  for p,q in [(.1,0),(.1,.5),(.5,.5)]:
   alphabet=[0,1] if q==0 else [0,1,2]
   for h in itertools.product(alphabet,repeat=4):np.testing.assert_allclose(e.oracle([h],p,q)[0,-1],e.enumerated_next(h,p,q),atol=1e-12)
 def test_e0_present_sufficient(self):np.testing.assert_allclose(e.oracle([[0,1,0],[1,1,0]],.1,0)[:,-1],[[.9,.1,0],[.9,.1,0]])
 def test_e2_history_irrelevant(self):np.testing.assert_allclose(e.oracle([[0,2,2],[1,1,2]],.5,.5)[:,-1],[[.25,.25,.5],[.25,.25,.5]])
 def test_e1_alias_is_predictively_distinct(self):
  a=e.oracle([[0,2],[1,2]],.1,.5)[:,-1];self.assertGreater(abs(a[0,0]-a[1,0]),.1)
 def test_impossible_history_rejected(self):
  with self.assertRaises(ValueError):e.oracle([[2]],.1,0)
 def test_features_causal_and_episode_local(self):
  a=np.array([[0,1,2,0],[1,0,2,1]]);b=a.copy();b[:,2:]=1
  np.testing.assert_array_equal(e.features(a,3)[:,:2],e.features(b,3)[:,:2])
  np.testing.assert_array_equal(e.features(a,3)[1],e.features(a[1:],3)[0])
  np.testing.assert_array_equal(e.features(a,3)[:,0,-3:],[[0,0,1],[0,0,1]])
 def test_models_causal_and_reset(self):
  torch.manual_seed(23);a=np.array([[0,1,2,0],[1,2,0,1]]);b=a.copy();b[:,2:]=1
  for model in [e.FiniteHistory(),e.RecursiveState()]:
   np.testing.assert_allclose(e.probabilities(model,a)[:,:2],e.probabilities(model,b)[:,:2],atol=1e-6)
   np.testing.assert_allclose(e.probabilities(model,a)[1],e.probabilities(model,a[1:])[0],atol=1e-6)
 def test_proposed_parameter_counts(self):
  self.assertEqual(sum(p.numel() for p in e.FiniteHistory().parameters()),579);self.assertEqual(sum(p.numel() for p in e.RecursiveState().parameters()),651)
 def test_b0_only_training_counts(self):
  a=np.array([[0,1,0]]);table=e.fit_b0(a);np.testing.assert_allclose(table,[[.25,.5,.25],[.5,.25,.25],[1/3,1/3,1/3]])
 def test_log_loss_known_probabilities(self):
  np.testing.assert_allclose(e.losses([[[.25,.25,.5]]],[[2]]),[[np.log(2)]])
  with self.assertRaises(ValueError):e.losses([[[1,1,1]]],[[2]])
 def test_paired_bootstrap_retains_pairing(self):
  a=np.arange(12,dtype=float).reshape(3,4);r=e.paired_interval(a,a,100,.05,42);self.assertEqual(r['interval'],[0,0])
 def test_optimizer_checkpoint_fixture(self):
  config=dict(learning_rate=.001,max_epochs=1,batch_episodes=2,gradient_norm_clip=1.,early_stopping_patience=1)
  # Fixed arbitrary arrays; no declared E0/E1/E2 comparison or research outcomes.
  a=np.array([[0,1,2],[1,2,0]]);torch.manual_seed(42);model=e.RecursiveState();before={k:v.clone() for k,v in model.state_dict().items()}
  trace=e.train_model(model,a,a,config,1,time.monotonic()+10)
  self.assertEqual(len(trace),1);self.assertTrue(any(not torch.equal(v,before[k]) for k,v in model.state_dict().items()))
 def test_training_deadline(self):
  c=dict(learning_rate=.001,max_epochs=1,batch_episodes=2,gradient_norm_clip=1.,early_stopping_patience=1)
  with self.assertRaises(TimeoutError):e.train_model(e.RecursiveState(),[[0,1]],[[0,1]],c,1,time.monotonic()-1)
 def test_pilot_gate_before_artifact_creation(self):
  import subprocess
  path=ROOT/'research/RP002A/runs/unauthorized-acceptance-fixture'
  self.assertFalse(path.exists())
  result=subprocess.run(['python3',str(ROOT/'scripts/rp002a-pilot.py'),'--execute','--run-id',path.name],cwd=ROOT,capture_output=True,text=True)
  self.assertNotEqual(result.returncode,0);self.assertIn('not frozen/authorized',result.stderr);self.assertFalse(path.exists())
if __name__=='__main__':unittest.main()
