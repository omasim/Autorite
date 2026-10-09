"""Synthetic assumption stress tests, not empirical RP002A observations."""
import hashlib,time,json
import numpy as np
from scipy.stats import t
from .inference import rate_upper

def seed(label):return int.from_bytes(hashlib.sha256(('rp002a/calibration-1.0/'+label).encode()).digest()[:8],'big')
def noise(rng,law,shape):
 if law=='normal':return rng.normal(size=shape)
 if law=='centered-gamma2':return (rng.gamma(2,size=shape)-2)/np.sqrt(2)
 if law=='standardized-t5':return rng.standard_t(5,size=shape)*np.sqrt(3/5)
 raise ValueError('Unknown synthetic law')
def execute(plan,dest,deadline):
 c=plan['calibration'];rows=[];seeds={};all_trials=[]
 count=len(c['candidate_n'])*len(c['laws'])*len(c['correlations'])*len(c['within_mean_variance_fractions'])
 for n in c['candidate_n']:
  for law in c['laws']:
   for rho in c['correlations']:
    for fraction in c['within_mean_variance_fractions']:
     label=f'{n}/{law}/{rho}/{fraction}';seeds[label]=seed(label);rng=np.random.default_rng(seeds[label]);flags=[];widths=[];means_saved=[];sds_saved=[]
     for start in range(0,c['trials'],500):
      if time.monotonic()>deadline:raise TimeoutError('Calibration allowance exhausted')
      size=min(500,c['trials']-start);shape=(size,n,7)
      cluster=np.sqrt(rho)*noise(rng,law,(size,n,1))+np.sqrt(1-rho)*noise(rng,law,shape)
      episode=rng.normal(size=shape)
      a=np.sqrt(1-fraction)*cluster+np.sqrt(fraction)*episode
      mean=a.mean(1);means_saved.append(mean);sds_saved.append(a.std(1,ddof=1));width=c['inflation']*t.ppf(1-c['alpha']/(2*c['family']),n-1)*a.std(1,ddof=1)/np.sqrt(n)
      # All seven truths at zero. Translation to benefit/equivalence boundaries
      # preserves false-claim tests; conservative coverage dominates both.
      flags.append(np.stack([np.any(np.abs(mean)>width,axis=1),np.any(mean+width<0,axis=1),np.any(((mean-width>0)&(mean+width<2))|((mean+width<0)&(mean-width>-2)),axis=1),np.all((mean-width>-1)&(mean+width<1),axis=1),np.any(np.abs(mean)>width/c['inflation'],axis=1)],axis=1));widths.append(width.mean(1))
     flag=np.concatenate(flags);width=np.concatenate(widths);np.savez_compressed(dest/f'student-{len(rows):03d}.npz',trials=np.column_stack([flag,width]),means=np.concatenate(means_saved),sds=np.concatenate(sds_saved))
     failure=int(flag[:,0].sum());upper=rate_upper(failure,c['trials'],.05/count)
     rows.append(dict(n=n,law=law,rho=rho,within_fraction=fraction,trials=c['trials'],simultaneous_coverage=1-failure/c['trials'],coverage_failures=failure,failure_upper_simultaneous=upper,false_benefit_boundary_rate=float(flag[:,1].mean()),false_equivalence_boundary_rate=float(flag[:,2].mean()),mean_standardized_half_width=float(width.mean()),center_equivalence_rate=float(flag[:,3].mean()),uninflated_student_t_coverage=1-float(flag[:,4].mean()),decision_scenario='SD=.01, margin=.01; truths at benefit -.01, equivalence +/-.01 and zero',eligible_cell=upper<=.05))
     (dest/'student-cells.json').write_text(json.dumps(rows,indent=2)+'\n')
     (dest/'progress.json').write_text(json.dumps({'completed_cells':len(rows),'total_cells':count})+'\n')
 (dest/'student-cells.json').write_text(json.dumps(rows,indent=2)+'\n')
 benchmarks=[]
 for n in c['benchmark_n']:
  for law in c['laws']:
   for fraction in c['benchmark_fractions']:
    label=f'benchmark/{n}/{law}/{fraction}';seeds[label]=seed(label);rng=np.random.default_rng(seeds[label]);results=[]
    for trial in range(c['benchmark_trials']):
     if time.monotonic()>deadline:raise TimeoutError('Calibration benchmark allowance exhausted')
     # Eight episodes are an explicit computational stress fixture, not 2048.
     m=c['benchmark_episodes'];cluster=noise(rng,law,(n,1,7));episode=rng.normal(size=(n,m,7))
     a=np.sqrt(1-fraction)*cluster+np.sqrt(fraction*m)*episode
     indices=rng.integers(n,size=(c['benchmark_resamples'],n));cluster_est=a.mean(1)[indices].mean(1)
     # Independent episode draw per selected occurrence, exact nested kernel.
     nested=np.zeros_like(cluster_est)
     for j in range(n):
      es=rng.integers(m,size=(c['benchmark_resamples'],m));nested+=a[indices[:,j,None],es].mean(1)/n
     item=[]
     for est in [cluster_est,nested]:
      lo,hi=np.quantile(est,[c['alpha']/(2*c['family']),1-c['alpha']/(2*c['family'])],axis=0)
      item.extend([float(np.all((lo<=0)&(hi>=0))),float(np.any(hi<0)),float(np.any(lo>0)),float((hi-lo).mean()/2)])
     results.append(item)
    matrix=np.asarray(results);np.savez_compressed(dest/f'benchmark-{len(benchmarks):02d}.npz',trials=matrix)
    benchmarks.append(dict(n=n,law=law,within_fraction=fraction,trials=c['benchmark_trials'],episodes=m,resamples=c['benchmark_resamples'],whole_cluster=dict(zip(['coverage','false_benefit_boundary','false_equivalence_boundary','half_width'],matrix[:,:4].mean(0).tolist())),nested=dict(zip(['coverage','false_benefit_boundary','false_equivalence_boundary','half_width'],matrix[:,4:].mean(0).tolist())),interpretation='Low-Monte-Carlo-resolution benchmark; not the selection gate'))
 eligible=[n for n in [20,30,50] if all(row['eligible_cell'] for row in rows if row['n']==n)]
 result=dict(mode='synthetic-calibration',student_t=rows,bootstrap_benchmarks=benchmarks,eligible_counts=eligible,interpretation='Synthetic stress scenarios do not establish coverage for actual learned-model differences; fixed twofold inflation and conditional normal-theory assumptions remain explicit')
 (dest/'summary.json').write_text(json.dumps(result,indent=2)+'\n');return seeds
