"""Check analytic planning against independent short-history enumeration."""
import importlib.util,itertools,math,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def module(name,path):
 s=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
d=module('design','packages/rp002a/design.py');e=module('engine','packages/rp002a/engine.py')
class Design(unittest.TestCase):
 def test_enumerated_conditional_entropy(self):
  for p,q in [(.1,0),(.1,.5),(.5,.5)]:
   alphabet=[0,1] if q==0 else [0,1,2]
   for t in range(1,5):
    expected=0
    for history in itertools.product(alphabet,repeat=t):
     probability=1
     for i,symbol in enumerate(history):probability*=([.5*(1-q),.5*(1-q),q] if i==0 else e.enumerated_next(history[:i],p,q))[symbol]
     pred=e.enumerated_next(history,p,q);expected+=probability*(-sum(x*math.log(x) for x in pred if x))
    self.assertAlmostEqual(expected,d.ideal_loss(p,q,t),places=12)
 def test_null_and_erasure_edges(self):
  for t in [1,8,128]:
   self.assertAlmostEqual(d.ideal_loss(.1,0,t),d.entropy(.1));self.assertAlmostEqual(d.ideal_loss(.5,.5,t),1.5*math.log(2));self.assertEqual(d.ideal_loss(.1,1,t),0)
 def test_window_matches_prefix_then_has_nonnegative_gap(self):
  for t in [1,7,8]:self.assertEqual(d.ideal_loss(.1,.5,t,8),d.ideal_loss(.1,.5,t))
  self.assertGreater(d.ideal_loss(.1,.5,128,8),d.ideal_loss(.1,.5,128))
 def test_invalid_inputs_rejected(self):
  for args in [(.6,.5,1),(.1,-.1,1),(.1,.5,0),(.1,.5,1,0)]:
   with self.assertRaises(ValueError):d.ideal_loss(*args)

 def test_snapshot_noise_and_real_changes(self):
  original={'hash':'unchanged','values':[.039808554540753716]}
  self.assertTrue(d.same_planning(original,{'hash':'unchanged','values':[.03980855454075372]}))
  self.assertFalse(d.same_planning(original,{'hash':'changed','values':original['values']}))
  self.assertFalse(d.same_planning(original,{'hash':'unchanged','values':[.039809]}))
