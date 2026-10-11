import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("rp004", ROOT / "research/RP004/lineage.py")
rp004 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rp004)
CONFIG = json.loads((ROOT / "research/RP004/RP004_FIXTURES.json").read_text())


def q(kind, *args):
    return {"kind": kind, "args": list(args)}


class LineageTests(unittest.TestCase):
    def test_copy_survives_fork_consumes_without_state_difference(self):
        copy_graph = rp004.construct(CONFIG["cases"][1]["events"])
        fork_graph = rp004.construct(CONFIG["cases"][2]["events"])
        self.assertEqual(rp004.project(copy_graph, "R2"), rp004.project(fork_graph, "R2"))
        self.assertTrue(rp004.truth(copy_graph, q("alive", "a")))
        self.assertFalse(rp004.truth(fork_graph, q("alive", "a")))
        for graph in (copy_graph, fork_graph):
            self.assertTrue(rp004.truth(graph, q("same_state", "b", "c")))
            self.assertFalse(rp004.truth(graph, q("ancestor", "b", "c")))

    def test_merge_retains_both_roots_single_parent_cannot_deny_second(self):
        graph = rp004.construct(CONFIG["cases"][4]["events"])
        self.assertEqual(rp004.roots(graph, "c"), {"a", "b"})
        self.assertIsNone(rp004.answer(rp004.project(graph, "R1"), q("ancestor", "b", "c")))
        self.assertTrue(rp004.answer(rp004.project(graph, "R2"), q("ancestor", "b", "c")))
        self.assertFalse(rp004.truth(graph, q("ancestor", "a", "b")))

    def test_independent_duplicates_and_strict_self_ancestry(self):
        graph = rp004.construct(CONFIG["cases"][3]["events"])
        self.assertTrue(rp004.truth(graph, q("same_state", "a", "b")))
        self.assertFalse(rp004.truth(graph, q("shared_root", "a", "b")))
        for rep in ("R0", "R1", "R2", "R3"):
            self.assertFalse(rp004.answer(rp004.project(graph, rep), q("ancestor", "a", "a")))
            self.assertTrue(rp004.answer(rp004.project(graph, rep), q("shared_root", "a", "a")))

    def test_forward_reference_consumption_and_duplicate_output_rejected(self):
        bad = copy.deepcopy(CONFIG["cases"][0]["events"])
        bad[1]["parents"] = ["c"]
        with self.assertRaises(ValueError):
            rp004.construct(bad)
        bad = copy.deepcopy(CONFIG["cases"][0]["events"])
        bad[2]["parents"] = ["a"]
        with self.assertRaises(ValueError):
            rp004.construct(bad)
        bad = copy.deepcopy(CONFIG["cases"][2]["events"])
        bad[1]["outputs"][1]["id"] = "b"
        with self.assertRaises(ValueError):
            rp004.construct(bad)

    def test_duplicate_merge_parent_and_copy_state_mutation_rejected(self):
        bad = copy.deepcopy(CONFIG["cases"][4]["events"])
        bad[2]["parents"] = ["a", "a"]
        with self.assertRaises(ValueError):
            rp004.construct(bad)
        bad = copy.deepcopy(CONFIG["cases"][1]["events"])
        bad[1]["outputs"][0]["state"] = "B"
        with self.assertRaises(ValueError):
            rp004.construct(bad)

    def test_parent_order_fork_order_and_opaque_renaming(self):
        for case in CONFIG["cases"]:
            graph = rp004.construct(case["events"])
            events = copy.deepcopy(case["events"])
            rename = {"a": "z9", "b": "x7", "c": "v2"}
            for event in events:
                event["parents"] = [rename[p] for p in reversed(event["parents"])]
                event["outputs"].reverse()
                for output in event["outputs"]:
                    output["id"] = rename[output["id"]]
            changed = rp004.construct(events)
            for control in case["controls"]:
                query = control["query"]
                new_query = {"kind": query["kind"], "args": [rename[a] for a in query["args"]]}
                expected = rp004.truth(graph, query)
                if query["kind"] == "parents":
                    expected = sorted(rename[p] for p in expected)
                self.assertEqual(rp004.truth(changed, new_query), expected)
                self.assertEqual(rp004.answer(rp004.project(changed, "R3"), new_query), expected)
            # R1 tie-breaking is intentionally label-sensitive, not a preferred lineage.
            if case["id"] == "G4":
                self.assertEqual(rp004.project(changed, "R1")["nodes"]["v2"]["parents"], ["x7"])

    def test_state_change_supported_without_false_lineage_change(self):
        events = copy.deepcopy(CONFIG["cases"][0]["events"])
        events[-1]["outputs"][0]["state"] = "B"
        graph = rp004.construct(events)
        for rep in ("R0", "R1", "R2", "R3"):
            self.assertFalse(rp004.answer(rp004.project(graph, rep), q("same_state", "a", "c")))
        self.assertTrue(rp004.truth(graph, q("ancestor", "a", "c")))

    def test_projection_does_not_leak_types_or_mutate_ground_truth(self):
        graph = rp004.construct(CONFIG["cases"][4]["events"])
        for rep in ("R0", "R1", "R2"):
            encoded = rp004.project(graph, rep)
            self.assertNotIn("kind", encoded["nodes"]["c"])
            self.assertNotIn("alive", encoded["nodes"]["a"])
        encoded["nodes"]["c"]["parents"].clear()
        self.assertEqual(graph["c"]["parents"], ["a", "b"])

    def test_corrupt_controls_and_invalid_queries_rejected(self):
        self.assertEqual(rp004.check_fixtures(CONFIG)["cells"], 216)
        bad = copy.deepcopy(CONFIG)
        bad["cases"][4]["controls"][2]["expected"] = False
        with self.assertRaisesRegex(ValueError, "G4"):
            rp004.check_fixtures(bad)
        bad = copy.deepcopy(CONFIG)
        bad["cases"][4]["controls"][2]["answers"]["R1"] = False
        with self.assertRaisesRegex(ValueError, "R1"):
            rp004.check_fixtures(bad)
        graph = rp004.construct(CONFIG["cases"][0]["events"])
        for query in (q("ancestor", "a"), q("alive", "absent"), q("identity", "a")):
            with self.assertRaises(ValueError):
                rp004.truth(graph, query)
        self.assertEqual(rp004.score(True, 1), "wrong")
        self.assertEqual(rp004.score(False, None), "unknown")
