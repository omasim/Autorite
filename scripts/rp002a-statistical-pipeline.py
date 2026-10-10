"""Plan by default; exact separately approved stages execute once."""
import argparse,sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from packages.rp002a import pipeline
p=argparse.ArgumentParser();p.add_argument('stage',choices=['calibration','variance','confirmation']);p.add_argument('--config',help='Separate repository-relative confirmation configuration');p.add_argument('--execute',action='store_true');a=p.parse_args()
if a.execute:print(pipeline.execute(a.stage,a.config))
else:print(json.dumps(pipeline.load(a.stage,a.config)[1],indent=2))
