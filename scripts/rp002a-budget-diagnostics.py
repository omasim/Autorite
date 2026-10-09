"""Review recorded validation traces against observed-history references; no training."""
from pathlib import Path
import argparse,hashlib,importlib.util,json
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,ROOT/path)
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
c=module('convergence','packages/rp002a/convergence.py')
design=module('design','packages/rp002a/design.py')
RUN=ROOT/'research/RP002A/runs/convergence-20261009-002'
OUT=ROOT/'research/RP002A/design/CONVERGENCE_002_DIAGNOSTICS.json'

def review():
 manifest=json.loads((RUN/'manifest.json').read_text())
 plan=manifest['configuration']['plan'];base=manifest['configuration']['base'];inputs={}
 def read(name):
  path=RUN/name;inputs[name]=c.digest(path)
  if inputs[name]!=manifest['outputs'][name]:raise ValueError('Recorded input checksum differs')
  return path
 rows=[]
 for world,n in sorted(plan['world_replicates'].items()):
  law=base['worlds'][world]
  for r in range(n):
   stem=f'{world}-r{r:02d}'
   # Only the checkpoint-selection validation split is inspected here.
   val=np.load(read(stem+'-validation.npy'),allow_pickle=False)
   table=np.load(read(stem+'-B0-table.npy'),allow_pickle=False)
   b0=float(c.e.losses(table[val[:,:-1]],val[:,1:],base['probability_clip']).mean())
   b3=float(c.e.losses(c.e.oracle(val[:,:-1],law['flip_probability'],law['erasure_probability']),val[:,1:],base['probability_clip']).mean())
   for model in ['B1','B2']:
    trace=json.loads(read(stem+'-'+model+'-trace.json').read_text())
    summary=c.trace_summary(trace,plan)
    values=np.array([t['validation_log_loss'] for t in trace])
    rows.append({'world':world,'replicate':r,'model':model,
      'epochs':len(values),'best_epoch':summary['best_epoch'],
      'near_cap':summary['best_in_final_cap_window'],
      'last_20_endpoint_decline':float(values[-20]-values[-1]) if len(values)>=20 else None,
      'last_50_endpoint_decline':float(values[-50]-values[-1]) if len(values)>=50 else None,
      'last_20_loss_range':float(np.ptp(values[-20:])),
      'selected_validation_loss':float(values.min()),
      'b0_validation_loss':b0,'b3_validation_loss':b3,
      'selected_minus_b0':float(values.min()-b0),
      'selected_minus_b3':float(values.min()-b3)})
 groups=[]
 for world in sorted(plan['world_replicates']):
  for model in ['B1','B2']:
   rs=[r for r in rows if r['world']==world and r['model']==model]
   groups.append({'world':world,'model':model,'n':len(rs),
    'near_cap_count':sum(r['near_cap'] for r in rs),
    'mean_selected_minus_b0':float(np.mean([r['selected_minus_b0'] for r in rs])),
    'mean_selected_minus_b3':float(np.mean([r['selected_minus_b3'] for r in rs]))})
 return {'kind':'post-outcome validation-only planning review',
   'source_run':RUN.name,'source_manifest_sha256':c.digest(RUN/'manifest.json'),
   'input_sha256':inputs,'fits':rows,'world_model_summaries':groups,
   'limits':'Reused checkpoint-selection validation, not independent evidence; no assessment inspected, training, new observations, changed convergence disposition, Claims or Cycle resolutions.'}

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--write',action='store_true');args=parser.parse_args();result=review()
 if args.write:OUT.write_text(json.dumps(result,indent=2)+'\n')
 elif not OUT.exists() or not design.same_planning(json.loads(OUT.read_text()),result):
  raise SystemExit('Saved budget diagnostics differ; review source before updating.')
 print('PASS: 40 recorded validation traces and reference comparisons; no assessment, new observations or training.')
