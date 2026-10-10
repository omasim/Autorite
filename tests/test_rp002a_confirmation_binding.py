import json,unittest
from unittest.mock import patch
from packages.rp002a import pipeline as p

class ConfirmationBindingTests(unittest.TestCase):
 def test_custom_configuration_cannot_replace_an_exploratory_stage(self):
  with self.assertRaises(ValueError):p.load('variance','research/RP002A/CONFIRMATORY_002_CONFIG.json')
 def test_configuration_cannot_escape_repository(self):
  with self.assertRaises(ValueError):p.load('confirmation','/tmp/unreviewed-confirmation.json')
 def test_second_attempt_requires_its_own_approval(self):
  path,plan,_=p.load('confirmation','research/RP002A/CONFIRMATORY_002_CONFIG.json')
  # An old approval must never substitute for the explicitly bound new one.
  original=p.Path.is_file
  with patch.object(p.Path,'is_file',lambda f:False if f.name=='CONFIRMATION_002_APPROVAL.json' else original(f)):
   with self.assertRaises(PermissionError):p.authorization('confirmation',path,plan)
 def test_all_previously_executed_seed_namespaces_are_disjoint(self):
  _,plan,base=p.load('confirmation','research/RP002A/CONFIRMATORY_002_CONFIG.json')
  new=set(p.seeds(plan['version'],plan['replicates'],base).values())
  self.assertEqual(len(new),420)
  for f in (p.ROOT/'research/RP002A/runs').glob('*/manifest.json'):
   if f.parent.name!=plan['run_id']:self.assertFalse(new&set(json.loads(f.read_text()).get('seeds',{}).values()))
