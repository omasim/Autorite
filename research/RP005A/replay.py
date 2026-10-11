"""Independent exhaustive reward paths and all-pairs distances; no producer imports."""
from fractions import Fraction
import json

EXPECTED_CONFIG = {
    "version": "0.1", "run_id": "audit-20261011-001",
    "case_ids": ["V0", "V1", "V2", "C0"], "node_counts": [8, 11, 8, 8],
    "targets": ["t1", "t2", "t3", "t4", "t5"], "horizons": [1, 2, 4],
    "arms": ["unrestricted", "restricted"], "future_budget": 3,
    "expected_planner_rows": 24, "expected_pair_rows": 12,
    "expected_structural_sources": 35, "expected_ordered_pairs": 313,
    "wall_seconds": 60, "memory_bytes": 134217728,
    "seeds": {"policy": "none; deterministic disclosed finite corpus"}}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def strict_loads(text):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("Duplicate JSON key")
            result[key] = value
        return result

    def reject_constant(value):
        raise ValueError("Nonfinite JSON value: " + value)
    return json.loads(text, object_pairs_hook=pairs, parse_constant=reject_constant)


def check_config(config):
    if canonical(config) != canonical(EXPECTED_CONFIG):
        raise ValueError("Frozen RP005A configuration mismatch")


def rebuild(case):
    if not isinstance(case, dict) or set(case) != {
            "id", "regime", "nodes", "start", "targets", "edges", "removed", "expected"}:
        raise ValueError("Independent case fields")
    if any(not isinstance(case[k], str) or not case[k] for k in ("id", "regime", "start")):
        raise ValueError("Independent case identity")
    nodes, targets = case["nodes"], case["targets"]
    if (not isinstance(nodes, list) or not 1 <= len(nodes) <= 12
            or any(not isinstance(n, str) or not n for n in nodes)
            or len(set(nodes)) != len(nodes) or case["start"] not in nodes):
        raise ValueError("Independent node universe")
    if (not isinstance(targets, list) or not targets
            or any(not isinstance(t, str) or t not in nodes for t in targets)
            or len(set(targets)) != len(targets)):
        raise ValueError("Independent fixed targets")
    if not isinstance(case["edges"], list) or len(case["edges"]) > 32:
        raise ValueError("Independent edge inventory")
    outgoing, indegree = {n: [] for n in nodes}, dict.fromkeys(nodes, 0)
    unique = set()
    for edge in case["edges"]:
        if not isinstance(edge, dict) or set(edge) != {"from", "to", "reward"}:
            raise ValueError("Independent edge fields")
        a, b, reward = edge["from"], edge["to"], edge["reward"]
        if (not isinstance(a, str) or not isinstance(b, str) or a not in outgoing
                or b not in outgoing or a == b or (a, b) in unique):
            raise ValueError("Independent edge endpoints")
        if type(reward) is not int or not -100 <= reward <= 100:
            raise ValueError("Independent integer reward")
        outgoing[a].append((b, reward))
        indegree[b] += 1
        unique.add((a, b))
    queue = [n for n in nodes if indegree[n] == 0]
    visited = 0
    while queue:
        item = queue.pop()
        visited += 1
        for child, _ in outgoing[item]:
            indegree[child] -= 1
            if indegree[child] == 0:
                queue.append(child)
    if visited != len(nodes):
        raise ValueError("Independent graph cycle")
    if any(outgoing[t] for t in targets):
        raise ValueError("Independent targets must be terminal")
    if not isinstance(case["removed"], list):
        raise ValueError("Independent restrictions")
    deleted = set()
    for pair in case["removed"]:
        if (not isinstance(pair, list) or len(pair) != 2
                or any(not isinstance(n, str) for n in pair)
                or tuple(pair) not in unique or tuple(pair) in deleted):
            raise ValueError("Independent edge-removal contract")
        deleted.add(tuple(pair))
    constrained = {a: [(b, r) for b, r in edges if (a, b) not in deleted]
                   for a, edges in outgoing.items()}
    return {"nodes": sorted(nodes), "targets": sorted(targets), "start": case["start"],
            "outgoing": outgoing, "constrained": constrained,
            "removed": sorted([list(p) for p in deleted])}


def distances(graph, guard=lambda: None):
    nodes = sorted(graph)
    distance = {(a, b): 0 if a == b else None for a in nodes for b in nodes}
    for a, edges in graph.items():
        for b, _ in edges:
            distance[a, b] = 1
    for middle in nodes:
        guard()
        for a in nodes:
            for b in nodes:
                left, right = distance[a, middle], distance[middle, b]
                if left is not None and right is not None:
                    candidate = left + right
                    if distance[a, b] is None or candidate < distance[a, b]:
                        distance[a, b] = candidate
    return distance


def all_plans(graph, start, horizon, guard=lambda: None):
    """Enumerate every allowed reward path, including forced negative continuations."""
    guard()
    if horizon == 0 or not graph[start]:
        return [(0, [start])]
    result = []
    for child, reward in graph[start]:
        for total, suffix in all_plans(graph, child, horizon - 1, guard):
            result.append((reward + total, [start] + suffix))
    return result


def planner_row(graph, case_id, horizon, arm, config, ordinal, guard=lambda: None):
    outgoing = graph["constrained"] if arm == "restricted" else graph["outgoing"]
    plans = all_plans(outgoing, graph["start"], horizon, guard)
    best = max(score for score, _ in plans)
    endpoint = min(path[1] if len(path) > 1 else path[0]
                   for score, path in plans if score == best)
    actions = sorted({path[1] for _, path in plans if len(path) > 1})
    scores = [{"destination": child, "score": max(total for total, path in plans
                if len(path) > 1 and path[1] == child)} for child in actions]
    own_distance, full_distance = distances(outgoing, guard), distances(graph["outgoing"], guard)
    budget = config["future_budget"]
    primary = [t for t in graph["targets"] if own_distance[endpoint, t] is not None
               and own_distance[endpoint, t] <= budget]
    secondary = [t for t in graph["targets"] if full_distance[endpoint, t] is not None
                 and full_distance[endpoint, t] <= budget]
    return {"ordinal": ordinal, "case": case_id, "horizon": horizon, "arm": arm,
            "source": graph["start"], "targets": graph["targets"], "future_budget": budget,
            "removed_edges": graph["removed"] if arm == "restricted" else [],
            "endpoint": endpoint, "action_scores": scores, "primary_targets": primary,
            "secondary_targets": secondary, "denominator": len(graph["targets"]),
            "primary_count": len(primary), "secondary_count": len(secondary)}


def pair_row(a, b, ordinal):
    denominator = a["denominator"]
    delta = Fraction(b["primary_count"] - a["primary_count"], denominator)
    selection = Fraction(b["secondary_count"] - a["secondary_count"], denominator)
    deletion = Fraction(b["primary_count"] - b["secondary_count"], denominator)
    if delta != selection + deletion or deletion > 0:
        raise ValueError("Independent paired decomposition")
    def encode(value):
        return {"numerator": value.numerator, "denominator": value.denominator}
    return {"ordinal": ordinal, "case": a["case"], "horizon": a["horizon"],
            "planner_ordinals": [a["ordinal"], b["ordinal"]],
            "baseline_endpoint": a["endpoint"], "restricted_endpoint": b["endpoint"],
            "denominator": denominator, "primary_difference": encode(delta),
            "selection_difference": encode(selection), "deletion_difference": encode(deletion),
            "direction": "positive" if delta > 0 else "negative" if delta < 0 else "zero"}


def structural_row(graph, case_id, source, config, ordinal, guard=lambda: None):
    full, constrained = distances(graph["outgoing"], guard), distances(graph["constrained"], guard)
    a = {n for n in graph["nodes"] if full[source, n] is not None}
    b = {n for n in graph["nodes"] if constrained[source, n] is not None}
    c = {n for n in a if full[source, n] <= config["future_budget"]}
    d = {n for n in b if constrained[source, n] <= config["future_budget"]}
    if not b.issubset(a) or not d.issubset(c):
        raise ValueError("Independent inclusion failure")
    targets = set(graph["targets"])
    return {"ordinal": ordinal, "case": case_id, "source": source,
            "ordered_pairs_checked": len(graph["nodes"]),
            "underlying_reachable": sorted(a), "restricted_reachable": sorted(b),
            "underlying_targets": sorted(a & targets), "restricted_targets": sorted(b & targets),
            "lost_nodes": sorted(a - b), "lost_targets": sorted((a - b) & targets),
            "inclusion": True, "future_budget": config["future_budget"],
            "underlying_budget_reachable": sorted(c), "restricted_budget_reachable": sorted(d),
            "budget_inclusion": True}


def verify_row(actual, expected):
    if canonical(actual) != canonical(expected):
        raise ValueError("Independent row mismatch at " + str(expected["ordinal"]))


def read_record(stream, label):
    try:
        return strict_loads(next(stream))
    except StopIteration:
        raise ValueError("Incomplete " + label + " inventory") from None


def ensure_end(stream, label):
    if next(stream, None) is not None:
        raise ValueError("Extra " + label + " record")


def replay(planner_stream, pair_stream, structural_stream, fixtures, config, guard=lambda: None):
    check_config(config)
    if (not isinstance(fixtures, dict) or set(fixtures) != {
            "version", "stage", "horizons", "future_budget", "cases"}
            or fixtures["version"] != "0.1" or fixtures["stage"] != "disclosed-preparation"
            or canonical(fixtures["horizons"]) != canonical(config["horizons"])
            or type(fixtures["future_budget"]) is not int or fixtures["future_budget"] != 3
            or [c["id"] for c in fixtures["cases"]] != config["case_ids"]):
        raise ValueError("Independent fixture inventory")
    guard()
    graphs = {case["id"]: rebuild(case) for case in fixtures["cases"]}
    if ([len(graphs[c]["nodes"]) for c in config["case_ids"]] != config["node_counts"]
            or any(g["targets"] != config["targets"] for g in graphs.values())):
        raise ValueError("Independent node/target inventory")
    planners, pairs, sources = iter(planner_stream), iter(pair_stream), iter(structural_stream)
    row_count, pair_count, source_count, ordered_pairs = 0, 0, 0, 0
    counts = {c: dict(positive=0, zero=0, negative=0) for c in config["case_ids"]}
    for case_id in config["case_ids"]:
        graph = graphs[case_id]
        for horizon in config["horizons"]:
            values = []
            for arm in config["arms"]:
                guard()
                expected = planner_row(graph, case_id, horizon, arm, config, row_count, guard)
                verify_row(read_record(planners, "planner"), expected)
                values.append(expected)
                row_count += 1
            expected_pair = pair_row(*values, pair_count)
            verify_row(read_record(pairs, "pair"), expected_pair)
            counts[case_id][expected_pair["direction"]] += 1
            pair_count += 1
        for source in graph["nodes"]:
            guard()
            expected = structural_row(graph, case_id, source, config, source_count, guard)
            verify_row(read_record(sources, "structural"), expected)
            source_count += 1
            ordered_pairs += len(graph["nodes"])
    for stream, label in ((planners, "planner"), (pairs, "pair"), (sources, "structural")):
        ensure_end(stream, label)
    if (row_count, pair_count, source_count, ordered_pairs) != (24, 12, 35, 313):
        raise ValueError("Independent complete coverage mismatch")
    guard()
    return {"planner_rows": row_count, "paired_comparisons": pair_count,
            "structural_sources": source_count, "ordered_pairs_per_inclusion_family": ordered_pairs,
            "all_raw_inclusions": True, "all_budget_inclusions": True, "pairs_by_case": counts}
