"""Measure the maximum declared non-witness evidence shape without answers.

This constructs schema-shaped placeholders for the 55-case design's truth,
projection, pair, and certificate inventories. Every answer/vector slot holds
the same explicit NONANSWER placeholder. No candidate events, inputs, query
answers, or classifications are created.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import resource
import sys


ROOT = Path(__file__).resolve().parents[1]
MASKS = tuple(format(i, "03b") for i in range(8))
NONANSWER = "UNCOMPUTED_PLACEHOLDER"
STRATA = ((4, 17), (5, 38))


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def query_count(entities: int, family: str) -> int:
    pairwise = 3 * entities * entities
    unary = 3 * entities if family == "FULL" else entities
    return pairwise + unary


def build_shape(guard):
    truth, projections, pairs, certificates = [], [], [], []
    case_shapes = []
    for n, cases in STRATA:
        labels = [f"S{n}-{i:02d}" for i in range(cases)]
        inventory = []
        for kind in ("same_state", "ancestor", "shared_root"):
            inventory.extend({"kind": kind, "args": [f"e{x}", f"e{y}"]}
                             for x in range(n) for y in range(n))
        for kind in ("parents", "birth_kind", "alive"):
            inventory.extend({"kind": kind, "args": [f"e{x}"]} for x in range(n))
        for case in labels:
            case_shapes.append({"id": case, "entities": [f"e{x}" for x in range(n)],
                                "events": [{"kind": "placeholder", "parents": [],
                                            "outputs": [{"id": f"e{x}", "state": NONANSWER}]}
                                           for x in range(n)]})
            for query in inventory:
                guard()
                truth.append({"ordinal": len(truth), "case": case,
                              "query": query, "truth": NONANSWER})
            for mask in MASKS:
                fields = {}
                if mask[0] == "1":
                    fields["state"] = {f"e{x}": NONANSWER for x in range(n)}
                if mask[1] == "1":
                    fields["parents"] = {f"e{x}": [] for x in range(n)}
                if mask[2] == "1":
                    fields["birth_kind"] = {f"e{x}": NONANSWER for x in range(n)}
                projections.append({"ordinal": len(projections), "mask": mask, "case": case,
                                    "projection": {"entities": [f"e{x}" for x in range(n)],
                                                   "fields": fields}})
        for mask in MASKS:
            for left in range(cases):
                for right in range(left + 1, cases):
                    pairs.append({"ordinal": len(pairs), "mask": mask,
                                  "cases": [labels[left], labels[right]],
                                  "projections_equal": True,
                                  "checked_queries": {"FULL": query_count(n, "FULL"),
                                                      "TOPOLOGY_STATE": query_count(n, "TOPOLOGY_STATE")},
                                  "conflict_index": {
                                      "FULL": {"count": 0, "first_ordinal": None},
                                      "TOPOLOGY_STATE": {"count": 0, "first_ordinal": None}}})
        for mask in MASKS:
            for family in ("FULL", "TOPOLOGY_STATE"):
                vector = [NONANSWER] * query_count(n, family)
                partitions = [{"projection": {"entities": [f"e{x}" for x in range(n)],
                                                "fields": {"state": {f"e{x}": NONANSWER for x in range(n)}}},
                               "cases": [case], "common_truth_vector": vector}
                              for case in labels]
                proper = [sub for sub in MASKS if sub != mask and
                          all(a == "0" or b == "1" for a, b in zip(sub, mask))]
                certificates.append({"ordinal": len(certificates), "mask": mask, "family": family,
                                     "sufficient": True, "inclusion_minimal": False,
                                     "partitions": partitions,
                                     "proper_submasks": [
                                         {"mask": sub, "sufficient": True,
                                          "conflict_index": {"count": 0, "first_ordinal": None}}
                                         for sub in proper]})
    return {"case_shapes": case_shapes, "truth": truth, "projections": projections,
            "pairs": pairs, "certificates": certificates}


def main() -> None:
    resources = load("finite_lineage_memory_shape_resources", ROOT / "research/RP006/resources.py")
    guard = resources.Guard(seconds=30, memory_bytes=128 * 1024 * 1024)
    shape = build_shape(guard)
    measurements = guard()
    counts = {name: len(shape[name]) for name in ("case_shapes", "truth", "projections", "pairs", "certificates")}
    expected = {"case_shapes": 55, "truth": 4_440, "projections": 440,
                "pairs": 6_712, "certificates": 32}
    if counts != expected:
        raise RuntimeError(f"Declared shape count mismatch: {counts}")
    print(json.dumps({"status": "PASS", "purpose": "ANSWER_FREE_NON_WITNESS_MEMORY_SHAPE",
                      "candidate_inputs_read": False, "candidate_answers_generated": False,
                      "counts": counts, "peak_rss_bytes": measurements["peak_process_rss_bytes"],
                      "rss_limit_bytes": 128 * 1024 * 1024}, sort_keys=True))


if __name__ == "__main__":
    main()
