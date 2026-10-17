#!/usr/bin/env python3
"""Answer-free recheck of the finite-lineage template and overlap arithmetic.

Reads only the payload-free RP004 structure export. It does not load RP004
fixtures, query implementations, candidate files, or answer-bearing artifacts.
"""
from __future__ import annotations

import itertools
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPORT = ROOT / "research/preparation/FINITE_LINEAGE_RP004_STRUCTURE_EXPORT_V2.json"

TEMPLATES = {
    "F4-01": [("root", (), ("a",)), ("copy", ("a",), ("b",)), ("continue", ("b",), ("c",)), ("root", (), ("d",))],
    "F4-02": [("root", (), ("a",)), ("continue", ("a",), ("b",)), ("fork", ("b",), ("c", "d"))],
    "F4-03": [("root", (), ("a",)), ("copy", ("a",), ("b",)), ("root", (), ("c",)), ("merge", ("b", "c"), ("d",))],
    "F4-04": [("root", (), ("a",)), ("root", (), ("b",)), ("copy", ("b",), ("c",)), ("continue", ("a",), ("d",))],
    "F5-01": [("root", (), ("a",)), ("continue", ("a",), ("b",)), ("fork", ("b",), ("c", "d")), ("continue", ("c",), ("e",))],
    "F5-02": [("root", (), ("a",)), ("root", (), ("b",)), ("fork", ("a",), ("c", "d")), ("merge", ("b", "c"), ("e",))],
    "F5-03": [("root", (), ("a",)), ("copy", ("a",), ("b",)), ("root", (), ("c",)), ("continue", ("c",), ("d",)), ("merge", ("b", "d"), ("e",))],
    "F5-04": [("root", (), ("a",)), ("root", (), ("b",)), ("continue", ("b",), ("c",)), ("copy", ("c",), ("d",)), ("merge", ("a", "d"), ("e",))],
}

# The illustrative vectors are checked only for operation-preserved payload
# equality. They are not treated as case inputs and no queries are evaluated.
VECTORS = {
    "F4-01": "AABA",
    "F4-02": "ABBB",
    "F4-03": "AABB",
    "F4-04": "AAAA",
    "F5-01": "ABBBC",
    "F5-02": "ABAAB",
    "F5-03": "AABCA",
    "F5-04": "ABCCA",
}


def restricted_growth_strings(n: int, max_blocks: int = 3):
    """Yield canonical set partitions in lexicographic RGS order."""
    if n == 0:
        yield ()
        return
    values = [0] * n

    def visit(i: int, largest: int):
        if i == n:
            yield tuple(values)
            return
        for value in range(min(largest + 1, max_blocks - 1) + 1):
            values[i] = value
            yield from visit(i + 1, max(largest, value))

    values[0] = 0
    yield from visit(1, 0)


def template_entities(events):
    return [entity for _, _, outputs in events for entity in outputs]


def event_facts(events):
    facts = {}
    forks = []
    for index, (kind, parents, outputs) in enumerate(events):
        for entity in outputs:
            facts[entity] = {"kind": kind, "parents": tuple(parents), "event": index}
        if kind == "fork":
            forks.append(frozenset(outputs))
    return facts, forks


def forced_components(events, entities):
    parent = {x: x for x in entities}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for kind, parents, outputs in events:
        if kind in {"copy", "fork"}:
            for output in outputs:
                union(parents[0], output)
    groups = {}
    for entity in entities:
        groups.setdefault(find(entity), []).append(entity)
    return sorted((tuple(v) for v in groups.values()), key=lambda group: min(entities.index(x) for x in group))


def fixture_events(case):
    return [(e["kind"], tuple(e["parents"]), tuple(o["id"] for o in e["outputs"])) for e in case["events"]]


def mapping_matches(candidate, fixture, selected, relabel, mode):
    cfacts, cforks, cevents = candidate
    ffacts, fforks, fevents = fixture
    selected = tuple(selected)
    if mode in {"D", "L", "R"} and any(not set(cfacts[c]["parents"]).issubset(selected) for c in selected):
        return False
    # Every selected candidate entity has the same immediate-parent structure.
    for c in selected:
        f = relabel[c]
        cparents = {relabel[p] for p in cfacts[c]["parents"] if p in selected}
        if mode in {"D", "L", "R"} and tuple(sorted(cparents)) != tuple(sorted(ffacts[f]["parents"])):
            return False
        if mode in {"L", "R"} and cfacts[c]["kind"] != ffacts[f]["kind"]:
            return False
    if mode in {"L", "R"}:
        for group in cforks:
            present = group.intersection(selected)
            if len(present) > 0:
                mapped = frozenset(relabel[x] for x in present)
                if not any(mapped == group2 and len(group2) == len(present) for group2 in fforks):
                    return False
    if mode == "R":
        # Replayable event sublogs include every output of each represented op.
        for c in selected:
            event = cfacts[c]["event"]
            outputs = cevents[event][2]
            if set(outputs) - set(selected):
                return False
    if mode == "O":
        selected_events = sorted({cfacts[c]["event"] for c in selected})
        translated = []
        for event_index in selected_events:
            kind, parents, outputs = cevents[event_index]
            if not set(parents).issubset(selected) or not set(outputs).issubset(selected):
                return False
            translated.append((kind, tuple(relabel[x] for x in parents), tuple(relabel[x] for x in outputs)))
        if translated != fevents:
            return False
    return True


def overlap_sets(candidate_events, fixture_events_):
    c_entities = template_entities(candidate_events)
    c_facts, c_forks = event_facts(candidate_events)
    c_struct = (c_facts, c_forks, candidate_events)
    results = {mode: [] for mode in "DLRO"}
    for fixture_id, fevents in fixture_events_.items():
        f_entities = template_entities(fevents)
        ffacts, fforks = event_facts(fevents)
        f_struct = (ffacts, fforks, fevents)
        for selected in itertools.combinations(c_entities, len(f_entities)):
            if "D" in results and any(not set(c_facts[x]["parents"]).issubset(selected) for x in selected):
                continue
            for perm in itertools.permutations(f_entities):
                relabel = dict(zip(selected, perm))
                for mode in "DLRO":
                    if mapping_matches(c_struct, f_struct, selected, relabel, mode):
                        results[mode].append((fixture_id, selected))
    return {k: sorted(set(v)) for k, v in results.items()}


def main():
    export = json.loads(EXPORT.read_text())
    export_sha = hashlib.sha256(EXPORT.read_bytes()).hexdigest()
    assert export_sha == "b448013d9f849f51af1bf026c9bf7b666bd5110a32aa28315c84c1e2819ff1ea", export_sha
    fixtures = {case["id"]: fixture_events(case) for case in export["cases"]}
    structural_counts = {}
    partition_counts = {}
    for slot, events in TEMPLATES.items():
        entities = template_entities(events)
        facts, _ = event_facts(events)
        assert len(entities) == int(slot[1]) and len(set(entities)) == len(entities)
        seen = set()
        for kind, parents, outputs in events:
            assert all(p in seen for p in parents)
            assert all(o not in seen for o in outputs)
            if kind == "root":
                assert not parents and len(outputs) == 1
            elif kind in {"continue", "copy"}:
                assert len(parents) == len(outputs) == 1
            elif kind == "fork":
                assert len(parents) == 1 and len(outputs) == 2
            elif kind == "merge":
                assert len(parents) == 2 and len(outputs) == 1
            else:
                raise AssertionError(kind)
            seen.update(outputs)
        # Enforce copy/fork state preservation on the proposed illustrative vector.
        vector = VECTORS[slot]
        assert len(vector) == len(entities)
        values = dict(zip(entities, vector))
        for kind, parents, outputs in events:
            if kind in {"copy", "fork"}:
                assert all(values[o] == values[parents[0]] for o in outputs), (slot, kind)
        components = forced_components(events, entities)
        component_index = {entity: i for i, group in enumerate(components) for entity in group}
        admissible = set()
        for rgs in restricted_growth_strings(len(components), 3):
            labels = tuple(rgs[component_index[e]] for e in entities)
            admissible.add(labels)
        partition_counts[slot] = len(admissible)
    # Compare the structures after the partition and legality checks above.
    structural_counts = {slot: overlap_sets(events, fixtures) for slot, events in TEMPLATES.items()}
    expected = {
        "F4-01": {"D": [("C4", ("a", "b", "d")), ("G0", ("a", "b", "c"))], "L": [], "R": [], "O": []},
        "F4-02": {"D": [("G0", ("a", "b", "c")), ("G0", ("a", "b", "d"))], "L": [], "R": [], "O": []},
        "F4-03": {"D": [("C4", ("a", "b", "c"))], "L": [], "R": [], "O": []},
        "F4-04": {"D": [("C4", ("a", "b", "c")), ("C4", ("a", "b", "d"))], "L": [("C4", ("a", "b", "d"))], "R": [("C4", ("a", "b", "d"))], "O": [("C4", ("a", "b", "d"))]},
        "F5-01": {"D": [("G0", ("a", "b", "c")), ("G0", ("a", "b", "d"))], "L": [], "R": [], "O": []},
        "F5-02": {"D": [("C4", ("a", "b", "c")), ("C4", ("a", "b", "d")), ("G1", ("a", "c", "d")), ("G2", ("a", "c", "d"))], "L": [("G2", ("a", "c", "d"))], "R": [("G2", ("a", "c", "d"))], "O": [("G2", ("a", "c", "d"))]},
        "F5-03": {"D": [("C4", ("a", "b", "c")), ("C4", ("a", "c", "d"))], "L": [("C4", ("a", "c", "d"))], "R": [("C4", ("a", "c", "d"))], "O": []},
        "F5-04": {"D": [("C4", ("a", "b", "c")), ("G0", ("b", "c", "d"))], "L": [("C4", ("a", "b", "c"))], "R": [("C4", ("a", "b", "c"))], "O": []},
    }
    assert partition_counts == {"F4-01": 5, "F4-02": 2, "F4-03": 5, "F4-04": 5, "F5-01": 5, "F5-02": 5, "F5-03": 14, "F5-04": 14}, partition_counts
    # Canonicalize the computed result into the same compact ID-set table.
    for slot, modes in expected.items():
        actual = {mode: [(fid, ids) for fid, ids in structural_counts[slot][mode]] for mode in "DLRO"}
        assert actual == modes, (slot, actual, modes)
    f4, f5 = sum(partition_counts[k] for k in partition_counts if k.startswith("F4")), sum(partition_counts[k] for k in partition_counts if k.startswith("F5"))
    arithmetic = {"cases": f4 + f5, "full_truth_rows": f4 * 60 + f5 * 90, "projections": (f4 + f5) * 8, "pair_mask_rows": (f4 * (f4 - 1) // 2 + f5 * (f5 - 1) // 2) * 8, "certificates": 2 * 8 * 2}
    assert arithmetic == {"cases": 55, "full_truth_rows": 4440, "projections": 440, "pair_mask_rows": 6712, "certificates": 32}, arithmetic
    print(json.dumps({"fixture_export_sha256_expected": "b448013d9f849f51af1bf026c9bf7b666bd5110a32aa28315c84c1e2819ff1ea", "partition_counts": partition_counts, "overlap_rows": {slot: {mode: [[fid, list(ids)] for fid, ids in structural_counts[slot][mode]] for mode in "DLRO"} for slot in TEMPLATES}, "arithmetic": arithmetic, "candidate_answers_generated": False}, sort_keys=True))


if __name__ == "__main__":
    main()
