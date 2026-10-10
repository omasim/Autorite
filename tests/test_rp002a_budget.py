import time,unittest
import numpy as np
from unittest.mock import patch
from packages.rp002a.budget import WallBudget
from packages.rp002a import pipeline

class BudgetTests(unittest.TestCase):
 def test_suspension_counts_against_wall_allowance(self):
  clocks={'monotonic':0.,'wall':1000.}
  b=WallBudget(60,lambda:clocks['monotonic'],lambda:clocks['wall'])
  clocks.update(monotonic=5.,wall=1060.)
  self.assertTrue(b.expired());self.assertEqual(b.timing()['elapsed_wall_seconds'],60)
  self.assertEqual(b.timing()['elapsed_monotonic_seconds'],5)
 def test_backward_wall_adjustment_cannot_extend_allowance(self):
  clocks={'monotonic':0.,'wall':1000.}
  b=WallBudget(60,lambda:clocks['monotonic'],lambda:clocks['wall'])
  clocks.update(monotonic=60.,wall=900.)
  self.assertTrue(b.expired())
 def test_training_stops_before_step_on_wall_expiry(self):
  e=pipeline.e;model=e.FiniteHistory(8,12);data=np.array([[0,1,2,0],[1,2,0,1]])
  opt={'learning_rate':.001,'max_epochs':1,'batch_episodes':2,'gradient_norm_clip':1,'early_stopping_patience':1}
  with patch.object(e.torch.optim.Adam,'step') as step:
   with self.assertRaises(TimeoutError):e.train_model(model,data,data,opt,42,time.monotonic()+60,budget_check=lambda:True)
   step.assert_not_called()
