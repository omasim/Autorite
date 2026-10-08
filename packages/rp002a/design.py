"""Deterministic design calculations, not samples, training or Claim promotion."""
import math
from statistics import NormalDist

def entropy(x):
 if not 0<=x<=1:raise ValueError('Probability outside [0,1]')
 return -sum(p*math.log(p) for p in (x,1-x) if p)

def ideal_loss(p,q,t,window=None):
 if not 0<=p<=.5 or not 0<=q<=1 or type(t) is not int or t<1:raise ValueError('Invalid law or history length')
 if window is not None and (type(window) is not int or window<1):raise ValueError('Invalid window')
 n=t if window is None else min(t,window)
 hidden=sum((1-q)*q**k*entropy((1+(1-2*p)**(k+1))/2) for k in range(n))+q**n*math.log(2)
 return entropy(q)+(1-q)*hidden

def planning(config):
 pairs=config['prediction_pairs_per_episode'];window=config['B1']['window'];rows=[]
 for world,law in config['worlds'].items():
  p,q=law['flip_probability'],law['erasure_probability']
  current=ideal_loss(p,q,1,1);finite=sum(ideal_loss(p,q,t,window) for t in range(1,pairs+1))/pairs
  full=sum(ideal_loss(p,q,t) for t in range(1,pairs+1))/pairs
  rows.append(dict(world=world,current_observation_ideal=current,window_ideal=finite,observed_history_ideal=full,current_to_history_gap=max(0,current-full),window_to_history_gap=max(0,finite-full)))
 z=NormalDist().inv_cdf(1-config['familywise_alpha']/(2*len(config['primary_comparisons'])))
 sensitivity=[]
 for sd in [.01,.03,.05,.1]:
  for n in [5,10,20,30,50]:sensitivity.append(dict(assumed_replicate_sd=sd,replicates=n,normal_approx_interval_half_width=z*sd/math.sqrt(n)))
 return dict(mode='analytic-design-review',trained_models=False,sampled_data=False,prediction_pairs=pairs,window=window,ideal_losses=rows,normal_critical_value=z,precision_sensitivity=sensitivity,limitations=['Ideal distribution-aware references are not learned B0/B1/B2 performance','Standard deviations are assumptions, not pilot estimates','Normal intervals are optimistic planning approximations, not finite-sample guarantees','No scientific Claim promoted or execution authorized'])


def same_planning(saved,current):
 """Allow floating-point platform noise; require exact metadata and structure."""
 if type(saved) is not type(current):return False
 if isinstance(current,float):return math.isfinite(saved) and math.isfinite(current) and math.isclose(saved,current,rel_tol=1e-12,abs_tol=1e-14)
 if isinstance(current,dict):return saved.keys()==current.keys() and all(same_planning(saved[k],current[k]) for k in current)
 if isinstance(current,list):return len(saved)==len(current) and all(same_planning(a,b) for a,b in zip(saved,current))
 return saved==current
