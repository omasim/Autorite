"""Bounded enumeration; freeze before collecting research outputs."""
import itertools
import json
from preservation import measure

IMPLICATIONS = {
    "exact_local_endpoint": ("exact_local", "exact_endpoint"),
    "exact_local_prefix": ("exact_local", "exact_prefix"),
    "exact_endpoint_prefix": ("exact_endpoint", "exact_prefix"),
    "tolerance_local_endpoint": ("tolerance_local", "tolerance_endpoint"),
    "tolerance_local_prefix": ("tolerance_local", "tolerance_prefix"),
    "tolerance_endpoint_prefix": ("tolerance_endpoint", "tolerance_prefix"),
    "variation_prefix": ("variation_budget", "tolerance_prefix"),
}


def enumerate_paths(config, stream, guard=lambda: None):
    domain = [{"key": k, "x": x} for k in config["keys"] for x in config["coordinates"]]
    counts = {str(n): 0 for n in config["lengths"]}
    signatures = {k: {"antecedent_count": 0, "counterexamples": 0, "first_witness": None} for k in IMPLICATIONS}
    ordinal = 0
    guard()
    for length in config["lengths"]:
        for items in itertools.product(domain, repeat=length):
            if ordinal % 128 == 0:
                guard()
            states = list(items)
            m = measure(states, config["epsilon"], config["budget"])
            row = {"ordinal": ordinal, "states": states, "measurements": m}
            stream.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
            for name, (a, b) in IMPLICATIONS.items():
                if m[a]:
                    signatures[name]["antecedent_count"] += 1
                    if not m[b]:
                        signatures[name]["counterexamples"] += 1
                        if signatures[name]["first_witness"] is None:
                            signatures[name]["first_witness"] = row
            counts[str(length)] += 1
            ordinal += 1
    guard()
    return {"path_count": ordinal, "by_length": counts, "signatures": signatures}
