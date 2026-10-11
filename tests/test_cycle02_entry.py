import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('entry', ROOT / 'scripts/check-cycle02-entry.py')
entry = importlib.util.module_from_spec(spec)
spec.loader.exec_module(entry)


class EntryControls(unittest.TestCase):
    def setUp(self):
        self.plan = json.loads((ROOT / 'research/RP006/ENTRY_PLAN.json').read_text())

    def test_no_execution_from_entry(self):
        plan = copy.deepcopy(self.plan)
        plan['execution_authorized'] = True
        with self.assertRaisesRegex(ValueError, 'grants no execution'):
            entry.validate(plan)

    def test_case_identifier_side_channel(self):
        plan = copy.deepcopy(self.plan)
        plan['projection_keys'].append('case_id')
        with self.assertRaisesRegex(ValueError, 'side information'):
            entry.validate(plan)

    def test_partial_parent_mask_not_in_class(self):
        plan = copy.deepcopy(self.plan)
        plan['masks'][2]['retained_fields'] = ['first_parent']
        with self.assertRaisesRegex(ValueError, 'whole-field masks'):
            entry.validate(plan)


if __name__ == '__main__':
    unittest.main()
