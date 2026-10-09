"""Paired training-replicate inference; conditional distribution assumptions explicit."""
import math
import numpy as np
from scipy.stats import t,chi2,beta

def interval(values,alpha=.05,family=7,inflation=2.):
 a=np.asarray(values,dtype=float)
 if a.ndim!=1 or len(a)<2 or not np.isfinite(a).all() or not 0<alpha<1 or type(family) is not int or family<1 or inflation<1:raise ValueError('Invalid replicate interval')
 mean=float(a.mean());sd=float(a.std(ddof=1));critical=float(t.ppf(1-alpha/(2*family),len(a)-1))*inflation
 if sd==0:raise ValueError('Zero observed variance: no automatic precision claim')
 width=critical*sd/math.sqrt(len(a))
 return dict(n=len(a),mean=mean,sample_sd=sd,critical=critical,half_width=width,interval=[mean-width,mean+width],method='twofold-inflated replicate-mean Student-t Bonferroni',assumptions='Independent replicate means; normal-theory interval with stress simulation, not distribution-free validity')

def decision(bounds,kind,margin=.01):
 lo,hi=bounds
 if not np.isfinite([lo,hi]).all() or lo>hi:raise ValueError('Invalid bounds')
 if kind=='benefit':return 'benefit' if hi < -margin else 'indeterminate'
 if kind=='equivalence':return 'equivalent' if lo > -margin and hi < margin else 'indeterminate'
 raise ValueError('Unknown primary decision')

def rate_upper(failures,total,alpha=.05):
 if not 0<=failures<=total or total<1:raise ValueError('Invalid binomial counts')
 return 1. if failures==total else float(beta.ppf(1-alpha,failures+1,total-failures))

def select_count(sd_values,eligible,plan):
 """Only independent exploratory SDs, never confirmatory means, choose n."""
 s=np.asarray(sd_values,dtype=float)
 if s.shape!=(7,) or not np.isfinite(s).all() or (s<=0).any():raise ValueError('Seven positive variance-stage SDs required')
 df=plan['variance']['replicates']-1
 # Simultaneous normal-theory upper SD bounds. Strong assumption recorded.
 scale=math.sqrt(df/chi2.ppf(.05/7,df));upper=float(s.max())*scale
 for n in plan['confirmation_rule']['candidate_counts']:
  if n in eligible and plan['confirmation_rule']['inflation']*t.ppf(1-.05/14,n-1)*upper/math.sqrt(n)<=plan['confirmation_rule']['target_half_width']:
   return dict(selected_n=n,maximum_observed_sd=float(s.max()),upper_sd=upper,upper_sd_factor=scale,precision_target=.005,assumptions='Normal replicate differences; conservative assumed-SD planning, not guaranteed power',precision_target_met_under_assumptions=True)
 n=max(eligible) if eligible else None
 if n is None:raise ValueError('No calibrated candidate; confirmation gate closed')
 return dict(selected_n=n,maximum_observed_sd=float(s.max()),upper_sd=upper,upper_sd_factor=scale,precision_target=.005,assumptions='Normal replicate differences; resource-limited precision, no power guarantee',precision_target_met_under_assumptions=False)

def secondary(p,target,current,clip):
 p=np.asarray(p,dtype=float);y=np.asarray(target);selected=np.take_along_axis(p,y[...,None],axis=-1)[...,0];loss=-np.log(np.maximum(selected,clip))
 out={'brier_score':float(((p-np.eye(3)[y])**2).sum(-1).mean()),'clipped_target_fraction':float((selected<clip).mean()),'unclipped_log_loss':float(-np.log(selected).mean()) if (selected>0).all() else None,'conditioned':{}}
 for label,mask in [('erasure_current',current==2),('visible_current',current!=2)]:
  out['conditioned'][label]={'timepoints':int(mask.sum()),'log_loss':float(loss[mask].mean()) if mask.any() else None}
 confidence=p.max(-1);correct=p.argmax(-1)==y;bins=np.minimum((confidence*10).astype(int),9);out['calibration_bins']=[]
 for b in range(10):
  mask=bins==b;out['calibration_bins'].append({'bin':b,'lower':b/10,'upper':(b+1)/10,'includes_one':b==9,'timepoints':int(mask.sum()),'mean_confidence':float(confidence[mask].mean()) if mask.any() else None,'accuracy':float(correct[mask].mean()) if mask.any() else None})
 return out
