"""RP004 disclosed controls. UNKNOWN is None, never a negative lineage fact."""
KINDS = {"root", "continue", "copy", "fork", "merge"}
QUERIES = {"same_state": 2, "ancestor": 2, "shared_root": 2,
           "parents": 1, "birth_kind": 1, "alive": 1}


def construct(events):
    """Execute a finite construction log; only existing live entities can be used."""
    nodes = {}
    if not isinstance(events, list) or not events:
        raise ValueError("nonempty event list required")
    for event in events:
        if not isinstance(event, dict) or set(event) != {"kind", "parents", "outputs"}:
            raise ValueError("event fields")
        kind, parents, outputs = event["kind"], event["parents"], event["outputs"]
        if not isinstance(kind, str) or kind not in KINDS:
            raise ValueError("event kind")
        if not isinstance(parents, list) or any(not isinstance(p, str) for p in parents):
            raise ValueError("parent list")
        if len(set(parents)) != len(parents):
            raise ValueError("duplicate parents")
        required_parents = 0 if kind == "root" else 2 if kind == "merge" else 1
        if len(parents) != required_parents:
            raise ValueError("parent cardinality")
        if any(p not in nodes or not nodes[p]["alive"] for p in parents):
            raise ValueError("missing, future or consumed parent")
        if not isinstance(outputs, list) or len(outputs) != (2 if kind == "fork" else 1):
            raise ValueError("output cardinality")
        fresh = set()
        for output in outputs:
            if not isinstance(output, dict) or set(output) != {"id", "state"}:
                raise ValueError("output fields")
            ident, state = output["id"], output["state"]
            if not isinstance(ident, str) or not ident or ident in nodes or ident in fresh:
                raise ValueError("entity must be fresh")
            if not isinstance(state, str) or not state:
                raise ValueError("nonempty opaque state required")
            if kind in {"copy", "fork"} and state != nodes[parents[0]]["state"]:
                raise ValueError("copy and fork preserve state")
            fresh.add(ident)
        if len(nodes) + len(fresh) > 12:
            raise ValueError("12-entity construction limit")
        for output in outputs:
            nodes[output["id"]] = {"state": output["state"], "parents": sorted(parents),
                                   "kind": kind, "alive": True}
        if kind in {"continue", "fork", "merge"}:
            for p in parents:
                nodes[p]["alive"] = False
    return nodes


def validate_query(query, nodes):
    if not isinstance(query, dict) or set(query) != {"kind", "args"}:
        raise ValueError("query fields")
    kind, args = query["kind"], query["args"]
    if not isinstance(kind, str) or kind not in QUERIES:
        raise ValueError("query kind")
    if not isinstance(args, list) or len(args) != QUERIES[kind]:
        raise ValueError("query arity")
    if any(not isinstance(a, str) or a not in nodes for a in args):
        raise ValueError("query entity")
    return kind, args


def ancestors(nodes, ident):
    found, stack = set(), list(nodes[ident]["parents"])
    while stack:
        item = stack.pop()
        if item not in found:
            found.add(item)
            stack.extend(nodes[item]["parents"])
    return found


def roots(nodes, ident):
    return {n for n in ancestors(nodes, ident) | {ident} if not nodes[n]["parents"]}


def truth(nodes, query):
    """Answers from the complete executed construction, without a projection."""
    kind, args = validate_query(query, nodes)
    a = args[0]
    if kind == "same_state":
        return nodes[a]["state"] == nodes[args[1]]["state"]
    if kind == "ancestor":
        return a in ancestors(nodes, args[1])
    if kind == "shared_root":
        return bool(roots(nodes, a) & roots(nodes, args[1]))
    if kind == "parents":
        return list(nodes[a]["parents"])
    if kind == "birth_kind":
        return nodes[a]["kind"]
    return nodes[a]["alive"]


def project(nodes, representation):
    if representation not in {"R0", "R1", "R2", "R3"}:
        raise ValueError("representation")
    encoded = {}
    for ident in sorted(nodes):
        node = nodes[ident]
        item = {"state": node["state"]}
        if representation == "R1":
            item["parents"] = node["parents"][:1]
        if representation in {"R2", "R3"}:
            item["parents"] = list(node["parents"])
        if representation == "R3":
            item["kind"] = node["kind"]
        encoded[ident] = item
    return {"representation": representation, "nodes": encoded}


def answer(encoded, query):
    """Conservative decoder. Unknown does not by itself prove information loss."""
    nodes, rep = encoded["nodes"], encoded["representation"]
    kind, args = validate_query(query, nodes)
    a = args[0]
    if kind == "same_state":
        return nodes[a]["state"] == nodes[args[1]]["state"]
    if kind == "ancestor" and a == args[1]:
        return False  # Strict ancestry in every admissible acyclic construction.
    if kind == "shared_root" and a == args[1]:
        return True
    if rep == "R0":
        return None
    if kind == "ancestor":
        present = a in ancestors(nodes, args[1])
        return present if rep != "R1" or present else None
    if kind == "shared_root":
        present = bool(roots(nodes, a) & roots(nodes, args[1]))
        return present if rep != "R1" or present else None
    if kind == "parents":
        return list(nodes[a]["parents"]) if rep != "R1" or not nodes[a]["parents"] else None
    if kind == "birth_kind":
        return nodes[a]["kind"] if rep == "R3" else "root" if not nodes[a]["parents"] else None
    # A leaf is necessarily live. Internal vertices require operation types.
    children = [n for n in nodes.values() if a in n["parents"]]
    if rep == "R1":
        return None  # An omitted merge edge may hide a consumer of even a leaf.
    if rep == "R2":
        return True if not children else None
    return not any(n["kind"] in {"continue", "fork", "merge"} for n in children)


def score(expected, observed):
    if observed is None:
        return "unknown"
    # bool is an int subclass: reject type-coerced answers as well as wrong values.
    return "correct" if type(expected) is type(observed) and expected == observed else "wrong"


def check_fixtures(config):
    cases = config["cases"]
    if [c["id"] for c in cases] != ["G0", "G1", "G2", "G3", "G4", "C4"]:
        raise ValueError("fixed case inventory")
    graphs, totals = {}, {key: 0 for key in ("correct", "unknown", "wrong")}
    for case in cases:
        graph = construct(case["events"])
        if set(graph) != {"a", "b", "c"}:
            raise ValueError("fixed aligned entity universe")
        graphs[case["id"]] = graph
        for control in case["controls"]:
            expected = truth(graph, control["query"])
            if score(expected, control["expected"]) != "correct":
                raise ValueError(case["id"] + " corrupted truth control")
            if set(control["answers"]) != {"R0", "R1", "R2", "R3"}:
                raise ValueError("four representation controls required")
            for rep, declared in control["answers"].items():
                observed = answer(project(graph, rep), control["query"])
                if type(observed) is not type(declared) or observed != declared:
                    raise ValueError(case["id"] + " corrupted decoder control " + rep)
                totals[score(expected, observed)] += 1
    for witness in config["collision_controls"]:
        left, right = (graphs[c] for c in witness["cases"])
        rep, query = witness["representation"], witness["query"]
        if project(left, rep) != project(right, rep):
            raise ValueError("collision projections differ")
        if truth(left, query) == truth(right, query):
            raise ValueError("collision answers do not differ")
    if totals["wrong"]:
        raise ValueError("unsound decoder")
    return {"cases": len(cases), "cells": sum(totals.values()),
            "collision_controls": len(config["collision_controls"]), **totals}
