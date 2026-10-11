import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("graph_review", Path(__file__).resolve().parents[1] / "scripts/check-cycle01-graph-review.py")
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)


class GraphReviewTests(unittest.TestCase):
    def fixtures(self):
        records = {
            "Q-A": {"id": "Q-A", "type": "Question", "status": "ACTIVE", "relations": []},
            "Q-B": {"id": "Q-B", "type": "Question", "status": "OPEN", "relations": []},
            "RP-A": {"id": "RP-A", "type": "ResearchPackage", "question_refs": ["Q-A"], "relations": []},
            "TST-A": {"id": "TST-A", "type": "Test", "target_refs": ["Q-A"], "package_ref": "RP-A", "protocol_ref": "protocol.md", "relations": [{"relation": "tests", "target": "Q-A"}]},
            "TST-B": {"id": "TST-B", "type": "Test", "target_refs": ["Q-A"], "package_ref": "RP-A", "protocol_ref": "first.md", "relations": []},
            "R-A": {"id": "R-A", "type": "Result", "status": "VALID", "package_ref": "RP-A", "test_ref": "TST-A", "run_ref": "run", "artifact_refs": ["run/manifest.json"], "relations": []},
        }
        return records

    def snapshot(self, records):
        return review.make_snapshot(records, {}, {"obligations": []}, "a" * 40, "b" * 64)

    def test_reference_trace_is_not_inferred_support(self):
        snap = self.snapshot(self.fixtures())
        self.assertEqual(snap["forward_question_trace"][0]["results_via_test_ref"], ["R-A"])
        self.assertEqual(snap["forward_question_trace"][0]["declared_informs"], [])
        self.assertEqual(len(snap["declared_relations"]), 1)
        self.assertTrue(snap["no_automatic_transitive_inference"])

    def test_unexecuted_test_and_untargeted_question_remain_visible(self):
        snap = self.snapshot(self.fixtures())
        self.assertEqual(snap["forward_question_trace"][0]["tests"], ["TST-A", "TST-B"])
        self.assertEqual(snap["forward_question_trace"][1]["results_via_test_ref"], [])
        self.assertEqual(len(snap["backward_result_trace"]), 1)

    def test_missing_reference_rejected(self):
        records = self.fixtures(); records["R-A"]["test_ref"] = "TST-MISSING"
        with self.assertRaisesRegex(ValueError, "Unknown typed reference"):
            self.snapshot(records)

    def test_cross_package_result_rejected(self):
        records = self.fixtures(); records["RP-B"] = {"id": "RP-B", "type": "ResearchPackage", "relations": []}
        records["R-A"]["package_ref"] = "RP-B"
        with self.assertRaisesRegex(ValueError, "Result/Test/package mismatch"):
            self.snapshot(records)

    def test_order_independent_and_incoming_index_complete(self):
        records = self.fixtures(); first = self.snapshot(records); second = self.snapshot(dict(reversed(list(records.items()))))
        self.assertEqual(first, second)
        self.assertEqual(first["incoming_index"]["TST-A"]["typed_references"], [{"source": "R-A", "field": "test_ref", "target": "TST-A"}])

    def test_saved_snapshot_tampering_and_numeric_type_rejected(self):
        expected = self.snapshot(self.fixtures()); saved = dict(expected)
        saved["no_automatic_transitive_inference"] = 1
        with self.assertRaisesRegex(ValueError, "differs from committed source"):
            review.verify_snapshot(saved, expected)
        saved = dict(expected); saved["forward_question_trace"] = []
        with self.assertRaisesRegex(ValueError, "differs from committed source"):
            review.verify_snapshot(saved, expected)


if __name__ == "__main__":
    unittest.main()
