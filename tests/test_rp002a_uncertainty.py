"""Independent enumeration of bootstrap variance, not coverage calibration."""
import importlib.util,itertools,math,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('uncertainty',ROOT/'packages/rp002a/uncertainty.py');u=importlib.util.module_from_spec(s);s.loader.exec_module(u)
class Uncertainty(unittest.TestCase):
 def test_nested_variance_by_exhaustive_resampling(self):
  rows=[[0.,2.],[4.,8.]];values=[];clusters=[]
  for rs in itertools.product(range(2),repeat=2):
   clusters.append(sum(sum(rows[r])/2 for r in rs)/2)
   for choices in itertools.product(range(2),repeat=4):
    values.append(sum(rows[rs[i]][choices[2*i+j]] for i in range(2) for j in range(2))/4)
  def variance(xs):
   mean=sum(xs)/len(xs);return sum((x-mean)**2 for x in xs)/len(xs)
  r=u.bootstrap_variance(rows)
  self.assertAlmostEqual(r['nested_bootstrap_variance'],variance(values))
  self.assertAlmostEqual(r['whole_cluster_bootstrap_variance'],variance(clusters))
 def test_constant_clusters_remove_inner_component(self):
  r=u.bootstrap_variance([[1,1],[3,3]])
  self.assertEqual(r['nested_added_variance'],0)
 def test_equal_means_still_add_episode_variance(self):
  r=u.bootstrap_variance([[0,2],[0,2]])
  self.assertEqual(r['whole_cluster_bootstrap_variance'],0);self.assertGreater(r['nested_added_variance'],0)
 def test_invalid_inputs(self):
  for x in [[[1,2]],[[1],[2]],[[1,2],[3]],[[1,math.nan],[2,3]]]:
   with self.assertRaises(ValueError):u.bootstrap_variance(x)
 def test_tail_and_resource_sensitivity_no_selection(self):
  r=u.planning({'familywise_alpha':.05,'primary_comparisons':list(range(7))},348.174745125)
  self.assertAlmostEqual(r['bootstrap_tail_resolution'][0]['expected_tail_count'],2000/280)
  self.assertAlmostEqual(r['random_effects_variance_illustrations'][2]['expected_nested_variance_over_true_mean_variance'],.8+2047/2048)
  self.assertIsNone(r['selected_replicate_count']);self.assertIsNone(r['selected_interval_method']);self.assertFalse(r['execution_authorized'])
