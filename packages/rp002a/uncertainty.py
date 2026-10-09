"""Deterministic uncertainty-design diagnostics; no sampling or training."""
import math
from statistics import NormalDist

def bootstrap_variance(episode_differences):
 """Exact conditional variance of current nested and whole-cluster resampling.

 Equal cluster sizes; independent inner draws for every selected occurrence.
 All empirical variances use population denominators, as resampling does.
 """
 rows=[list(row) for row in episode_differences]
 if len(rows)<2 or len(rows[0])<2 or any(len(row)!=len(rows[0]) for row in rows):
  raise ValueError('At least two equal-sized replicate/episode axes required')
 if any(not math.isfinite(x) for row in rows for x in row):raise ValueError('Nonfinite difference')
 n,m=len(rows),len(rows[0]);means=[sum(row)/m for row in rows];overall=sum(means)/n
 between=sum((x-overall)**2 for x in means)/n
 within=sum(sum((x-mu)**2 for x in row)/m for row,mu in zip(rows,means))/n
 cluster=between/n;extra=within/(n*m)
 return dict(replicates=n,episodes=m,whole_cluster_bootstrap_variance=cluster,
             nested_added_variance=extra,nested_bootstrap_variance=cluster+extra)

def planning(config,elapsed):
 alpha=config['familywise_alpha'];k=len(config['primary_comparisons']);tail=alpha/(2*k)
 z=NormalDist().inv_cdf(1-tail)
 precision=[]
 for sd in [.001,.003,.01,.03]:
  for half_width in [.005,.01]:
   precision.append(dict(assumed_sd_of_replicate_means=sd,target_half_width=half_width,
     known_sd_normal_minimum_n=max(2,math.ceil((z*sd/half_width)**2))))
 tails=[]
 for count in [2000,10000,50000]:
  expected=count*tail;binomial_sd=math.sqrt(count*tail*(1-tail))
  tails.append(dict(resamples=count,tail_probability=tail,expected_tail_count=expected,
    tail_count_sd=binomial_sd,relative_tail_count_sd=binomial_sd/expected))
 # Random-effects illustration only: D_ri=mu+U_r+epsilon_ri.
 ratios=[]
 for n in [5,10,20,30,50]:
  for fraction in [0,.5,1]:
   # fraction of Var(replicate mean) contributed by finite held-out sampling.
   cluster=(n-1)/n;added=(2048-1)/2048*fraction
   ratios.append(dict(replicates=n,within_episode_fraction=fraction,
      expected_whole_cluster_variance_over_true_mean_variance=cluster,
      expected_nested_variance_over_true_mean_variance=cluster+added))
 return dict(mode='deterministic-uncertainty-design-review',sampled_data=False,trained_models=False,
  family_size=k,familywise_alpha=alpha,normal_critical_value=z,
  assumed_precision=precision,bootstrap_tail_resolution=tails,random_effects_variance_illustrations=ratios,
  runtime_sensitivity=[dict(replicates_per_world=n,pilot_linear_seconds=n*elapsed,
    twofold_seconds=2*n*elapsed,fourfold_seconds=4*n*elapsed) for n in [5,10,20,30,50]],
  selected_replicate_count=None,selected_interval_method=None,execution_authorized=False)
