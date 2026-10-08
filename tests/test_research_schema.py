import importlib.util,json,shutil,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('validator',ROOT/'packages/research-schema/validate.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
class SchemaTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)/'repo'
  shutil.copytree(ROOT,self.root,ignore=shutil.ignore_patterns('.git','apps','output','__pycache__','.venv'))
 def tearDown(self):self.temp.cleanup()
 def change(self,path,update):
  p=self.root/path;d,body=v.read_record(p);update(d);p.write_text('---\n'+json.dumps(d)+'\n---\n'+body)
 def reject(self,fragment):
  with self.assertRaisesRegex(v.Invalid,fragment):v.validate(self.root)
 def test_current_records(self):
  records,cycles=v.validate(self.root);self.assertTrue({'Q-0','Q-1','Q-2','Q-3','Q-4','Q-5','RP-002A','RP-003','RP-004','RP-005A'} <= set(records));self.assertEqual(len(cycles),1)
 def test_status_typing(self):
  self.change('graph/sources/SRC-PSR2001.md',lambda d:d.update(status='VALID'));self.reject('missing/unknown fields')
 def test_unknown_id(self):
  self.change('research/RP002A/RECORD.md',lambda d:d.update(question_refs=['Q-MISSING']));self.reject('Unknown ID')
 def test_alias_shadowing(self):
  self.change('research/RP002A/RECORD.md',lambda d:d.update(aliases=['Q-3']));self.reject('Alias shadows')
 def test_unknown_field(self):
  self.change('research/RP002A/RECORD.md',lambda d:d.update(stauts='ACTIVE'));self.reject('missing/unknown')
 def test_unsafe_path(self):
  self.change('research/RP002A/RECORD.md',lambda d:d.update(protocol_ref='../outside.md'));self.reject('Unsafe path')
 def test_premature_full_ring(self):
  p=self.root/'cycles/cycle-01/manifest.json';d=json.loads(p.read_text())
  for o in d['obligations']:o.update(resolved=True,resolution='completed',evidence_refs=['README.md'])
  p.write_text(json.dumps(d));self.reject('progress/lifecycle mismatch')
 def test_duplicate_yaml_key(self):
  p=self.root/'graph/questions/Q-0.md';p.write_text('---\nid: Q-0\nid: Q-1\n---\nDuplicate-key fixture.');self.reject('duplicate key')
 def evidence_fixture(self):
  def put(path,d,body):
   base=dict(schema_version='0.1',title='Synthetic validator fixture',created_at='2026-10-08',updated_at='2026-10-08',source_refs=['README.md'],relations=[]);base.update(d)
   p=self.root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('---\n'+json.dumps(base)+'\n---\n'+body)
  run=self.root/'research/RP002A/runs/synthetic';run.mkdir(parents=True);(run/'out.txt').write_text('fixture')
  import hashlib
  (run/'manifest.json').write_text(json.dumps(dict(configuration={'fixture':True},seeds=[0],environment={'test':True},outputs={'out.txt':hashlib.sha256(b'fixture').hexdigest()})))
  put('graph/claims/C-FIXTURE.md',dict(id='C-FIXTURE',type='Claim',status='SUPPORTED',claim_kind='empirical',statement='Synthetic test only',scope='Validator fixture',assumption_refs=[],does_not_imply='No research result',limitations='Temporary fixture',change_conditions='Validator test'),'## Justification\nSynthetic R-FIXTURE supports this fixture.')
  put('graph/tests/TST-FIXTURE.md',dict(id='TST-FIXTURE',type='Test',package_ref='RP-002A',protocol_ref='research/RP002A/PROTOCOL_DRAFT.md',target_refs=['C-FIXTURE']),'Temporary fixture.')
  put('graph/results/R-FIXTURE.md',dict(id='R-FIXTURE',type='Result',status='VALID',package_ref='RP-002A',test_ref='TST-FIXTURE',run_ref='research/RP002A/runs/synthetic',artifact_refs=['research/RP002A/runs/synthetic/out.txt'],observations='Synthetic test only',relations=[{'relation':'supports','target':'C-FIXTURE'}]),'The supports relation to C-FIXTURE is synthetic, used only in this temporary test directory.')
  return run
 def test_checksum_tampering(self):
  run=self.evidence_fixture();v.validate(self.root);(run/'out.txt').write_text('tampered');self.reject('checksum mismatch')
 def test_invalidated_only_support(self):
  self.evidence_fixture();self.change('graph/results/R-FIXTURE.md',lambda d:d.update(status='INVALIDATED',invalidation_reason='Synthetic invalidation',invalidation_decision_ref='D-0003'));self.reject('valid supporting evidence missing')
 def test_test_package_mismatch(self):
  self.evidence_fixture();self.change('graph/tests/TST-FIXTURE.md',lambda d:d.update(package_ref='RP-003'));self.reject('Test/package mismatch')
 def test_supersession_cycle(self):
  for source,target in [('0001','0002'),('0002','0001')]:
   p=self.root/f'graph/decisions/D-{source}.md';d,body=v.read_record(p);d['relations']=[{'relation':'supersedes','target':'D-'+target}];p.write_text('---\n'+json.dumps(d)+'\n---\n'+body+'\nSupersedes D-'+target+' in this synthetic cycle fixture.')
  self.reject('Supersession cycle')
 def test_committed_run_manifest_immutable(self):
  import subprocess
  run=self.evidence_fixture()
  subprocess.run(['git','init','-q'],cwd=self.root,check=True,capture_output=True)
  subprocess.run(['git','add','research/RP002A/runs/synthetic'],cwd=self.root,check=True,capture_output=True)
  subprocess.run(['git','-c','user.name=Validator fixture','-c','user.email=fixture@example.invalid','commit','-qm','Fixture only'],cwd=self.root,check=True,capture_output=True)
  v.validate(self.root)
  p=run/'manifest.json';d=json.loads(p.read_text());d['seeds']=[999];p.write_text(json.dumps(d));self.reject('immutable run changed')
if __name__=='__main__':unittest.main()
