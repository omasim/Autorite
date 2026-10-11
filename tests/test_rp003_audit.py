import io
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research/RP003"))
from audit import enumerate_paths
from replay import independent_measure, replay


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((ROOT / "research/RP003/AUDIT_CONFIG.json").read_text())
        # Engineering tests use a small disclosed control domain, not the research grid.
        mini = dict(self.config, keys=["A"], coordinates=["0", "1/2"], lengths=[2])
        self.stream = io.StringIO()
        self.summary = enumerate_paths(mini, self.stream)

    def test_control_domain_includes_repetition_and_order(self):
        rows = [json.loads(s) for s in self.stream.getvalue().splitlines()]
        self.assertEqual(self.summary["path_count"], 4)
        self.assertEqual([r["ordinal"] for r in rows], list(range(4)))
        self.assertEqual([s["x"] for s in rows[2]["states"]], ["1/2", "0"])

    def test_independent_fixture_arithmetic(self):
        cases = json.loads((ROOT / "research/RP003/FIXTURES.json").read_text())["cases"]
        for case in cases:
            self.assertEqual(independent_measure(case["states"]), case["expected"])

    def test_measurement_corruption_rejected(self):
        row = json.loads(self.stream.getvalue().splitlines()[0])
        row["measurements"]["max_excursion"] = "1"
        with self.assertRaisesRegex(ValueError, "Measurement mismatch"):
            replay(io.StringIO(json.dumps(row) + "\n"), self.config)

    def test_coverage_corruption_rejected(self):
        row = json.loads(self.stream.getvalue().splitlines()[0])
        row["ordinal"] = 1
        with self.assertRaisesRegex(ValueError, "Coverage/order"):
            replay(io.StringIO(json.dumps(row) + "\n"), self.config)

    def test_truncated_output_rejected(self):
        row = self.stream.getvalue().splitlines()[0]
        with self.assertRaisesRegex(ValueError, "Incomplete enumeration"):
            replay(io.StringIO(row + "\n"), self.config)

    def test_resource_guard_stops_generator(self):
        def fail():
            raise RuntimeError("budget")
        with self.assertRaisesRegex(RuntimeError, "budget"):
            enumerate_paths(self.config, io.StringIO(), fail)
