"""Reproduce saved deterministic design calculations; never run an experiment."""
from pathlib import Path
import argparse,importlib.util,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('design',ROOT/'packages/rp002a/design.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
p=ROOT/'research/RP002A/CONFIG_PROPOSAL.json';result=d.planning(json.loads(p.read_text()));result['configuration_sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
text=json.dumps(result,indent=2)+'\n';dest=ROOT/'research/RP002A/design/ANALYTIC_REVIEW.json'
a=argparse.ArgumentParser();a.add_argument('--check',action='store_true');args=a.parse_args()
if args.check:
 assert dest.read_text()==text,'Design calculation snapshot differs';print('PASS: analytic design calculations reproduce; no samples or training.')
else:dest.write_text(text);print(dest)
