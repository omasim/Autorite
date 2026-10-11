import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("rp005a", ROOT / "research/RP005A/planning.py")
rp005a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rp005a)
CONFIG = json.loads((ROOT / "research/RP005A/RP005A_FIXTURES.json").read_text())


def enumerate_plans(case, restricted, horizon):
    """Separate path enumeration, without the producer's DP or edge-map helper."""
    deleted = {tuple(p) for p in case["removed"]} if restricted else set()
    edges = [e for e in case["edges"] if (e["from"], e["to"]) not in deleted]

    def paths(node, remaining):
        outgoing = [e for e in edges if e["from"] == node]
        if not remaining or not outgoing:
            return [(0, [node])]
        return [(e["reward"] + score, [node] + route) for e in outgoing
                for score, route in paths(e["to"], remaining - 1)]

    plans = paths(case["start"], horizon)
    score = max(p[0] for p in plans)
    first = min(route[1] if len(route) > 1 else route[0]
                for total, route in plans if total == score)
    scores = sorted((child, max(total for total, route in plans
                                if len(route) > 1 and route[1] == child))
                    for child in {route[1] for _, route in plans if len(route) > 1})
    return first, scores


class PlanningPreparationTests(unittest.TestCase):
    def test_disclosed_inventory(self):
        self.assertEqual(rp005a.check_fixtures(CONFIG), {
            "cases": 4, "planner_rows": 24, "paired_controls": 12, "inclusion_sources": 35})

    def test_dp_matches_independent_exhaustive_plans(self):
        for case in CONFIG["cases"]:
            for restricted in (False, True):
                for horizon in CONFIG["horizons"]:
                    result = rp005a.evaluate(case, horizon, restricted, 3)
                    endpoint, scores = enumerate_plans(case, restricted, horizon)
                    self.assertEqual(result["endpoint"], endpoint)
                    self.assertEqual(result["action_scores"], scores)

    def test_structural_inclusion_matches_independent_boolean_closure(self):
        for case in CONFIG["cases"]:
            closures = []
            nodes = case["nodes"]
            for restricted in (False, True):
                deleted = {tuple(p) for p in case["removed"]} if restricted else set()
                matrix = [[a == b for b in nodes] for a in nodes]
                for e in case["edges"]:
                    if (e["from"], e["to"]) not in deleted:
                        matrix[nodes.index(e["from"])][nodes.index(e["to"])] = True
                for k in range(len(nodes)):
                    for i in range(len(nodes)):
                        for j in range(len(nodes)):
                            matrix[i][j] |= matrix[i][k] and matrix[k][j]
                for i, node in enumerate(nodes):
                    truth = {n for j, n in enumerate(nodes) if matrix[i][j]}
                    self.assertEqual(rp005a.reachable(nodes, rp005a.edge_map(case, restricted), node), truth)
                closures.append(matrix)
            self.assertTrue(all(not closures[1][i][j] or closures[0][i][j]
                                for i in range(len(nodes)) for j in range(len(nodes))))

    def test_delayed_cost_enters_only_sufficient_horizon(self):
        case = CONFIG["cases"][1]
        self.assertEqual([rp005a.evaluate(case, h, False, 3)["endpoint"] for h in [1, 2, 4]],
                         ["b", "b", "a"])
        self.assertEqual([rp005a.paired(case, h, 3)[2] for h in [1, 2, 4]],
                         [rp005a.Fraction(1, 5), rp005a.Fraction(1, 5), 0])

    def test_downstream_deletion_cannot_be_hidden_by_denominator(self):
        case = CONFIG["cases"][3]
        a, b, delta, selection, deletion = rp005a.paired(case, 1, 3)
        self.assertEqual(a["denominator"], b["denominator"])
        self.assertEqual((delta, selection, deletion), (rp005a.Fraction(-1, 5), 0, rp005a.Fraction(-1, 5)))
        self.assertEqual(b["secondary_targets"], ["t1", "t2", "t3"])
        self.assertEqual(b["primary_targets"], ["t1", "t2"])

    def test_budget_zero_includes_self_and_cannot_reach_other_targets(self):
        case = CONFIG["cases"][1]
        edges = rp005a.edge_map(case)
        self.assertEqual(rp005a.reachable(case["nodes"], edges, "t1", 0), {"t1"})
        self.assertEqual(rp005a.reachable(case["nodes"], edges, "b", 2), {"b", "d", "e"})
        self.assertEqual(rp005a.reachable(case["nodes"], edges, "b", 3) & set(case["targets"]), {"t4", "t5"})
        for fixture in CONFIG["cases"]:
            for restricted in (False, True):
                deleted = {tuple(p) for p in fixture["removed"]} if restricted else set()
                raw = [e for e in fixture["edges"] if (e["from"], e["to"]) not in deleted]

                def path_nodes(node, remaining):
                    result = {node}
                    if remaining:
                        for edge in raw:
                            if edge["from"] == node:
                                result |= path_nodes(edge["to"], remaining - 1)
                    return result

                for node in fixture["nodes"]:
                    for budget in range(4):
                        self.assertEqual(rp005a.reachable(fixture["nodes"], rp005a.edge_map(fixture, restricted),
                                                         node, budget), path_nodes(node, budget))

    def test_tie_break_lexical_independent_of_input_order(self):
        edges = {("s", "b"): 1, ("s", "a"): 1}
        self.assertEqual(rp005a.choose(["s", "b", "a"], edges, "s", 1)[0], "a")
        self.assertEqual(rp005a.choose(["s", "a", "b"], dict(reversed(list(edges.items()))), "s", 1)[0], "a")

    def test_forced_negative_edge_and_terminal_stay(self):
        self.assertEqual(rp005a.choose(["s", "a"], {("s", "a"): -4}, "s", 4)[0], "a")
        self.assertEqual(rp005a.choose(["s"], {}, "s", 4), ("s", []))

    def test_bad_restrictions_duplicates_or_added_edges_rejected(self):
        for removed in [[["a", "b"]], [["s", "b"], ["s", "b"]], [["s", "missing"]]]:
            case = copy.deepcopy(CONFIG["cases"][0])
            case["removed"] = removed
            with self.assertRaises(ValueError):
                rp005a.validate_case(case)

    def test_bad_graph_nodes_edges_rewards_and_cycle_rejected(self):
        for mutation in ("node", "duplicate", "missing", "bool", "cycle", "target"):
            case = copy.deepcopy(CONFIG["cases"][0])
            if mutation == "node": case["nodes"].append("s")
            if mutation == "duplicate": case["edges"].append(case["edges"][0])
            if mutation == "missing": case["edges"][0]["to"] = "missing"
            if mutation == "bool": case["edges"][0]["reward"] = True
            if mutation == "cycle": case["edges"].append({"from": "a", "to": "s", "reward": 0})
            if mutation == "target": case["edges"].append({"from": "t1", "to": "b", "reward": 0})
            with self.assertRaises(ValueError):
                rp005a.validate_case(case)

    def test_empty_or_duplicated_targets_rejected(self):
        for targets in ([], ["t1", "t1"], ["missing"]):
            case = copy.deepcopy(CONFIG["cases"][0])
            case["targets"] = targets
            with self.assertRaises(ValueError):
                rp005a.validate_case(case)

    def test_invalid_horizon_budget_and_changed_expected_control_rejected(self):
        case = CONFIG["cases"][0]
        for h in (0, -1, 5, True, 1.5):
            with self.assertRaises(ValueError):
                rp005a.choose(case["nodes"], rp005a.edge_map(case), "s", h)
        for b in (-1, True, 1.5):
            with self.assertRaises(ValueError):
                rp005a.reachable(case["nodes"], rp005a.edge_map(case), "s", b)
        bad = copy.deepcopy(CONFIG)
        bad["cases"][0]["expected"][0]["restricted_primary"] = 5
        with self.assertRaises(AssertionError):
            rp005a.check_fixtures(bad)
        bad = copy.deepcopy(CONFIG)
        bad["horizons"][0] = True
        with self.assertRaises(ValueError):
            rp005a.check_fixtures(bad)


if __name__ == "__main__":
    unittest.main()
