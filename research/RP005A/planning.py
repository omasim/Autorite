"""Disclosed RP005A preparation controls; no run or research Result is produced."""
from fractions import Fraction
from functools import lru_cache


def validate_case(case):
    if not isinstance(case, dict) or set(case) != {
        "id", "regime", "nodes", "start", "targets", "edges", "removed", "expected"
    }:
        raise ValueError("case fields")
    if any(not isinstance(case[k], str) or not case[k] for k in ("id", "regime", "start")):
        raise ValueError("case identity")
    nodes = case["nodes"]
    if (not isinstance(nodes, list) or not 1 <= len(nodes) <= 12
            or any(not isinstance(n, str) or not n for n in nodes)
            or len(set(nodes)) != len(nodes) or case["start"] not in nodes):
        raise ValueError("node universe")
    targets = case["targets"]
    if (not isinstance(targets, list) or not targets
            or any(not isinstance(t, str) or t not in nodes for t in targets)
            or len(set(targets)) != len(targets)):
        raise ValueError("fixed target universe")
    edges = case["edges"]
    if not isinstance(edges, list) or len(edges) > 32:
        raise ValueError("edge inventory")
    pairs, adjacency = set(), {n: [] for n in nodes}
    for edge in edges:
        if not isinstance(edge, dict) or set(edge) != {"from", "to", "reward"}:
            raise ValueError("edge fields")
        a, b, reward = edge["from"], edge["to"], edge["reward"]
        if (not isinstance(a, str) or not isinstance(b, str)
                or a not in adjacency or b not in adjacency or a == b):
            raise ValueError("edge endpoints")
        if type(reward) is not int or abs(reward) > 100:
            raise ValueError("bounded integer reward")
        if (a, b) in pairs:
            raise ValueError("duplicate edge")
        pairs.add((a, b))
        adjacency[a].append(b)
    if any(adjacency[t] for t in targets):
        raise ValueError("targets must be terminal")
    visiting, finished = set(), set()

    def visit(node):
        if node in visiting:
            raise ValueError("acyclic graph required")
        if node in finished:
            return
        visiting.add(node)
        for child in adjacency[node]:
            visit(child)
        visiting.remove(node)
        finished.add(node)

    for node in nodes:
        visit(node)
    removed = case["removed"]
    if not isinstance(removed, list):
        raise ValueError("restriction list")
    removed_pairs = set()
    for pair in removed:
        if (not isinstance(pair, list) or len(pair) != 2
                or any(not isinstance(n, str) for n in pair)
                or tuple(pair) not in pairs or tuple(pair) in removed_pairs):
            raise ValueError("restriction must delete distinct existing edges")
        removed_pairs.add(tuple(pair))
    return case


def edge_map(case, restricted=False):
    validate_case(case)
    excluded = {tuple(p) for p in case["removed"]} if restricted else set()
    return {(e["from"], e["to"]): e["reward"] for e in case["edges"]
            if (e["from"], e["to"]) not in excluded}


def reachable(nodes, edges, start, budget=None):
    """Zero-length paths count; budget counts unit-cost transitions, not rewards."""
    if start not in nodes or (budget is not None and (type(budget) is not int or budget < 0)):
        raise ValueError("reachability arguments")
    seen, frontier = {start}, {start}
    steps = 0
    while frontier and (budget is None or steps < budget):
        following = {b for a, b in edges if a in frontier} - seen
        seen |= following
        frontier = following
        steps += 1
    return seen


def choose(nodes, edges, start, horizon):
    """Exact truncated reward maximization; no voluntary stop at a nonterminal."""
    if start not in nodes or type(horizon) is not int or not 1 <= horizon <= 4:
        raise ValueError("planner arguments")
    adjacency = {n: [] for n in nodes}
    for (a, b), reward in edges.items():
        adjacency[a].append((b, reward))

    @lru_cache(None)
    def value(node, remaining):
        if remaining == 0 or not adjacency[node]:
            return 0
        return max(reward + value(child, remaining - 1)
                   for child, reward in adjacency[node])

    scores = sorted((child, reward + value(child, horizon - 1))
                    for child, reward in adjacency[start])
    if not scores:
        return start, []
    best = max(score for _, score in scores)
    return next(child for child, score in scores if score == best), scores


def evaluate(case, horizon, restricted, future_budget):
    """Execute one action; score future target options, never realized visitation."""
    own, underlying = edge_map(case, restricted), edge_map(case)
    endpoint, scores = choose(case["nodes"], own, case["start"], horizon)
    targets = set(case["targets"])
    primary = sorted(targets & reachable(case["nodes"], own, endpoint, future_budget))
    secondary = sorted(targets & reachable(case["nodes"], underlying, endpoint, future_budget))
    return {"endpoint": endpoint, "action_scores": scores, "primary_targets": primary,
            "secondary_targets": secondary, "denominator": len(targets),
            "primary_count": len(primary), "secondary_count": len(secondary)}


def paired(case, horizon, future_budget):
    baseline = evaluate(case, horizon, False, future_budget)
    restricted = evaluate(case, horizon, True, future_budget)
    denominator = len(case["targets"])
    selection = Fraction(restricted["secondary_count"] - baseline["secondary_count"], denominator)
    deletion = Fraction(restricted["primary_count"] - restricted["secondary_count"], denominator)
    delta = Fraction(restricted["primary_count"] - baseline["primary_count"], denominator)
    assert delta == selection + deletion and deletion <= 0
    return baseline, restricted, delta, selection, deletion


def check_fixtures(config):
    if set(config) != {"version", "stage", "horizons", "future_budget", "cases"}:
        raise ValueError("configuration fields")
    if (config["version"] != "0.1" or config["stage"] != "disclosed-preparation"
            or config["horizons"] != [1, 2, 4]
            or any(type(h) is not int for h in config["horizons"])
            or type(config["future_budget"]) is not int
            or config["future_budget"] != 3):
        raise ValueError("preparation contract")
    if [c["id"] for c in config["cases"]] != ["V0", "V1", "V2", "C0"]:
        raise ValueError("case inventory")
    rows, inclusion_sources = 0, 0
    for case in config["cases"]:
        underlying, restricted = edge_map(case), edge_map(case, True)
        for node in case["nodes"]:
            assert reachable(case["nodes"], restricted, node) <= reachable(case["nodes"], underlying, node)
            inclusion_sources += 1
        expected = case["expected"]
        if not isinstance(expected, list) or len(expected) != 3:
            raise ValueError("expected comparison inventory")
        for horizon, control in zip(config["horizons"], expected):
            if set(control) != {"horizon", "baseline_endpoint", "restricted_endpoint",
                               "baseline_primary", "restricted_primary", "restricted_secondary"}:
                raise ValueError("control fields")
            if type(control["horizon"]) is not int or control["horizon"] != horizon:
                raise ValueError("control horizon")
            for key in ("baseline_primary", "restricted_primary", "restricted_secondary"):
                if type(control[key]) is not int:
                    raise ValueError("control count type")
            a, b, _, _, _ = paired(case, horizon, config["future_budget"])
            assert a["endpoint"] == control["baseline_endpoint"]
            assert b["endpoint"] == control["restricted_endpoint"]
            assert a["primary_count"] == a["secondary_count"] == control["baseline_primary"]
            assert b["primary_count"] == control["restricted_primary"]
            assert b["secondary_count"] == control["restricted_secondary"]
            assert a["denominator"] == b["denominator"] == 5
            rows += 2
    return {"cases": 4, "planner_rows": rows, "paired_controls": rows // 2,
            "inclusion_sources": inclusion_sources}
