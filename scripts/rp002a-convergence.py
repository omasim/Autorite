"""Plan the separate convergence stage; execution is gated before artifact creation."""
from pathlib import Path
import argparse,importlib.util,json,sys
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('convergence',ROOT/'packages/rp002a/convergence.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage',type=int,choices=[1,2,3],default=1);p.add_argument('--execute',action='store_true');p.add_argument('--run-id');a=p.parse_args();path,plan,base=c.load_plan(a.stage)
 if a.execute:
  try:print(c.execute(path,plan,base,a.run_id))
  except PermissionError as ex:sys.exit(str(ex))
 else:print(json.dumps({'mode':'plan-only','plan':plan,'plan_sha256':c.digest(path),'seed_count':len(c.schedule(plan)),'run_created':False},indent=2))
