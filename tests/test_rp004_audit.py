import copy
import importlib.util
import io
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
RP004 = ROOT / 'research/RP004'
# Avoid colliding with RP003's modules in the same test process.
spec = importlib.util.spec_from_file_location('rp004_audit_replay', RP004 / 'replay.py')
replay = importlib.util.module_from_spec(spec)
spec.loader.exec_module(replay)
spec = importlib.util.spec_from_file_location('rp004_audit_lineage', RP004 / 'lineage.py')
lineage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lineage)
sys.modules['lineage'] = lineage
spec = importlib.util.spec_from_file_location('rp004_audit_producer', RP004 / 'audit.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
FIXTURES = json.loads((RP004 / 'RP004_FIXTURES.json').read_text())
CONFIG = json.loads((RP004 / 'RP004_AUDIT_CONFIG.json').read_text())


class AuditTests(unittest.TestCase):
    def test_independent_rebuild_matches_only_disclosed_controls(self):
        for case in FIXTURES['cases']:
            graph = replay.rebuild(case['events'])
            for control in case['controls']:
                self.assertEqual(replay.canonical(replay.evaluate(graph, control['query'])), replay.canonical(control['expected']))
                for rep, value in control['answers'].items():
                    self.assertEqual(replay.canonical(replay.decode(replay.encode(graph, rep), control['query'])), replay.canonical(value))

    def test_known_row_corruption_unknown_and_bool_coercion_rejected(self):
        case = FIXTURES['cases'][4]
        query = {'kind': 'ancestor', 'args': ['b', 'c']}
        graph = lineage.construct(case['events'])
        expected = replay.expected_row(replay.rebuild(case['events']), 'G4', query, 'R1', 0)
        actual = audit.make_row(graph, 'G4', query, 'R1', 0)
        replay.verify_row(actual, expected)
        for key, value in [('answer', False), ('truth', 1), ('ordinal', 1), ('score', 'correct')]:
            bad = copy.deepcopy(actual)
            bad[key] = value
            with self.assertRaises(ValueError):
                replay.verify_row(bad, expected)
        bad = copy.deepcopy(actual)
        bad['projection']['case_hint'] = 'G4'
        with self.assertRaises(ValueError):
            replay.verify_row(bad, expected)

    def test_coverage_rejects_truncation_and_duplicate_early_rows(self):
        with self.assertRaisesRegex(ValueError, 'Incomplete decoder'):
            replay.replay(io.StringIO(''), io.StringIO(''), FIXTURES, CONFIG)
        case = FIXTURES['cases'][0]
        graph = lineage.construct(case['events'])
        query = {'kind': 'same_state', 'args': ['a', 'a']}
        row = audit.make_row(graph, 'G0', query, 'R0', 0)
        with self.assertRaisesRegex(ValueError, 'Incomplete decoder'):
            replay.replay(io.StringIO(json.dumps(row)+'\n'), io.StringIO(''), FIXTURES, CONFIG)
        with self.assertRaisesRegex(ValueError, 'row mismatch'):
            replay.replay(io.StringIO((json.dumps(row)+'\n')*2), io.StringIO(''), FIXTURES, CONFIG)

    def test_frozen_configuration_inventory_and_numeric_types(self):
        replay.check_config(CONFIG)
        for key, value in [('expected_decoder_rows', 860), ('wall_seconds', 60.0), ('entities', ['a', 'c', 'b'])]:
            bad = copy.deepcopy(CONFIG)
            bad[key] = value
            with self.assertRaises(ValueError):
                replay.check_config(bad)
        bad = copy.deepcopy(FIXTURES)
        bad['cases'][0]['id'] = 'unexpected'
        with self.assertRaisesRegex(ValueError, 'case inventory'):
            replay.replay([], [], bad, CONFIG)

    def test_independent_consumption_duplicate_parent_and_cycle_rejected(self):
        bad = copy.deepcopy(FIXTURES['cases'][0]['events'])
        bad[-1]['parents'] = ['a']
        with self.assertRaises(ValueError):
            replay.rebuild(bad)
        bad = copy.deepcopy(FIXTURES['cases'][4]['events'])
        bad[-1]['parents'] = ['a', 'a']
        with self.assertRaises(ValueError):
            replay.rebuild(bad)
        with self.assertRaisesRegex(ValueError, 'cycle'):
            replay.closure({'a': {'b'}, 'b': {'a'}})

    def test_resource_guard_stops_before_any_target_output(self):
        def stop():
            raise RuntimeError('guard')
        for function in (audit.iter_rows, audit.iter_collisions):
            with self.assertRaisesRegex(RuntimeError, 'guard'):
                next(function(FIXTURES, CONFIG, stop))
        with self.assertRaisesRegex(ValueError, 'Extra collision'):
            replay.ensure_end(iter(['{}']), 'collision')
