"""Producer of the predeclared RP005A saved-output audit."""
import json
from collections import Counter
from research.RP005A.planning import edge_map, evaluate, paired, reachable


def ratio(value):
    return {"numerator": value.numerator, "denominator": value.denominator}


def direction(value):
    return "positive" if value > 0 else "negative" if value < 0 else "zero"


def make_planner_row(case, horizon, arm, config, ordinal):
    selected = arm == "restricted"
    result = evaluate(case, horizon, selected, config["future_budget"])
    result["action_scores"] = [{"destination": child, "score": score}
                               for child, score in result["action_scores"]]
    return {"ordinal": ordinal, "case": case["id"], "horizon": horizon, "arm": arm,
            "source": case["start"], "targets": sorted(case["targets"]),
            "future_budget": config["future_budget"],
            "removed_edges": sorted(case["removed"]) if selected else [], **result}


def iter_planner(fixtures, config, guard=lambda: None):
    guard()
    count = 0
    for case in fixtures["cases"]:
        for horizon in config["horizons"]:
            for arm in config["arms"]:
                guard()
                yield make_planner_row(case, horizon, arm, config, count)
                count += 1
    if count != config["expected_planner_rows"]:
        raise ValueError("Planner inventory mismatch")


def make_pair_row(case, horizon, config, ordinal):
    a, b, delta, selection, deletion = paired(case, horizon, config["future_budget"])
    return {"ordinal": ordinal, "case": case["id"], "horizon": horizon,
            "planner_ordinals": [2 * ordinal, 2 * ordinal + 1],
            "baseline_endpoint": a["endpoint"], "restricted_endpoint": b["endpoint"],
            "denominator": len(case["targets"]), "primary_difference": ratio(delta),
            "selection_difference": ratio(selection), "deletion_difference": ratio(deletion),
            "direction": direction(delta)}


def iter_pairs(fixtures, config, guard=lambda: None):
    guard()
    count = 0
    for case in fixtures["cases"]:
        for horizon in config["horizons"]:
            guard()
            yield make_pair_row(case, horizon, config, count)
            count += 1
    if count != config["expected_pair_rows"]:
        raise ValueError("Pair inventory mismatch")


def make_structural_row(case, source, config, ordinal):
    original, removed = edge_map(case), edge_map(case, True)
    targets = set(case["targets"])
    a = reachable(case["nodes"], original, source)
    b = reachable(case["nodes"], removed, source)
    c = reachable(case["nodes"], original, source, config["future_budget"])
    d = reachable(case["nodes"], removed, source, config["future_budget"])
    if not b <= a or not d <= c:
        raise ValueError("Edge-removal inclusion fails")
    return {"ordinal": ordinal, "case": case["id"], "source": source,
            "ordered_pairs_checked": len(case["nodes"]),
            "underlying_reachable": sorted(a), "restricted_reachable": sorted(b),
            "underlying_targets": sorted(a & targets), "restricted_targets": sorted(b & targets),
            "lost_nodes": sorted(a - b), "lost_targets": sorted((a - b) & targets),
            "inclusion": True, "future_budget": config["future_budget"],
            "underlying_budget_reachable": sorted(c), "restricted_budget_reachable": sorted(d),
            "budget_inclusion": True}


def iter_structural(fixtures, config, guard=lambda: None):
    guard()
    count = 0
    for case in fixtures["cases"]:
        for source in sorted(case["nodes"]):
            guard()
            yield make_structural_row(case, source, config, count)
            count += 1
    if count != config["expected_structural_sources"]:
        raise ValueError("Structural source inventory mismatch")


def summarize(planner, pairs, structural, config):
    return {"planner_rows": len(planner), "paired_comparisons": len(pairs),
            "structural_sources": len(structural),
            "ordered_pairs_per_inclusion_family": sum(r["ordered_pairs_checked"] for r in structural),
            "all_raw_inclusions": all(r["inclusion"] for r in structural),
            "all_budget_inclusions": all(r["budget_inclusion"] for r in structural),
            "pairs_by_case": {case: {sign: Counter(r["direction"] for r in pairs
                                                     if r["case"] == case)[sign]
                                     for sign in ("positive", "zero", "negative")}
                              for case in config["case_ids"]}}


def write_jsonl(stream, row):
    stream.write(json.dumps(row, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n")
