import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("rp003", ROOT / "research/RP003/preservation.py")
rp003 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rp003)


def path(*xs):
    return [{"key": "A", "x": x} for x in xs]


class PreservationTests(unittest.TestCase):
    def test_inclusive_boundary_and_exact_arithmetic(self):
        result = rp003.measure(path("0", "1/3", "1"))
        self.assertTrue(result["tolerance_prefix"])
        self.assertTrue(result["variation_budget"])
        self.assertEqual(result["total_variation"], "1")
        self.assertFalse(rp003.measure(path("0", "10000000000000001/10000000000000000"))["tolerance_endpoint"])

    def test_return_does_not_certify_prefix_or_variation(self):
        result = rp003.measure(path("0", "1", "2", "1", "0"))
        self.assertTrue(result["tolerance_local"])
        self.assertTrue(result["tolerance_endpoint"])
        self.assertFalse(result["tolerance_prefix"])
        self.assertFalse(result["variation_budget"])
        self.assertEqual(result["total_variation"], "4")

    def test_prefix_bound_is_not_variation_bound(self):
        result = rp003.measure(path("0", "1", "0"))
        self.assertTrue(result["tolerance_prefix"])
        self.assertFalse(result["variation_budget"])

    def test_relabel_return_separates_exact_endpoint_from_path(self):
        result = rp003.measure([{"key": "A", "x": "0"}, {"key": "B", "x": "0"}, {"key": "A", "x": "0"}])
        self.assertTrue(result["exact_endpoint"])
        self.assertFalse(result["exact_local"])
        self.assertFalse(result["exact_prefix"])
        self.assertTrue(result["tolerance_local"])

    def test_reject_invalid_states_and_parameters(self):
        for states in ([], path("0"), [{"key": "C", "x": "0"}] * 2, [{"key": "A", "x": 0.5}] * 2, path("0", "1/0")):
            with self.subTest(states=states), self.assertRaises((ValueError, ZeroDivisionError)):
                rp003.measure(states)
        with self.assertRaises(ValueError):
            rp003.measure(path("0", "1"), epsilon="-1")

    def test_corrupted_expectation_is_rejected(self):
        config = json.loads((ROOT / "research/RP003/FIXTURES.json").read_text())
        self.assertEqual(rp003.check_fixtures(config), 4)
        bad = copy.deepcopy(config)
        bad["cases"][1]["expected"]["tolerance_endpoint"] = True
        with self.assertRaisesRegex(ValueError, "P1"):
            rp003.check_fixtures(bad)
