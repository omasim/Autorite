"""Independent replay with integer quarter-units, without the research evaluator."""
import json
from math import gcd

PAIRS = [
    ("exact_local_endpoint", "exact_local", "exact_endpoint"),
    ("exact_local_prefix", "exact_local", "exact_prefix"),
    ("exact_endpoint_prefix", "exact_endpoint", "exact_prefix"),
    ("tolerance_local_endpoint", "tolerance_local", "tolerance_endpoint"),
    ("tolerance_local_prefix", "tolerance_local", "tolerance_prefix"),
    ("tolerance_endpoint_prefix", "tolerance_endpoint", "tolerance_prefix"),
    ("variation_prefix", "variation_budget", "tolerance_prefix"),
]


def quarter(value):
    parts = value.split("/")
    numerator = int(parts[0])
    denominator = int(parts[1]) if len(parts) == 2 else 1
    if len(parts) > 2 or denominator <= 0 or 4 % denominator:
        raise ValueError("Not an exact quarter-unit coordinate")
    return numerator * (4 // denominator)


def rational(q):
    divisor = gcd(q, 4)
    return str(q // divisor) if divisor == 4 else f"{q // divisor}/{4 // divisor}"


def independent_measure(states):
    xs = [quarter(s["x"]) for s in states]
    keys = [s["key"] for s in states]
    distances = [abs(xs[i] - xs[i-1]) for i in range(1, len(xs))]
    prefixes = [abs(x - xs[0]) for x in xs]
    return {
        "exact_local": sum(keys[i] != keys[i-1] for i in range(1, len(keys))) == 0,
        "exact_endpoint": keys[0] == keys[-1],
        "exact_prefix": set(keys) == {keys[0]},
        "tolerance_local": sum(d > 4 for d in distances) == 0,
        "tolerance_endpoint": abs(xs[-1] - xs[0]) <= 4,
        "tolerance_prefix": sum(d > 4 for d in prefixes) == 0,
        "variation_budget": sum(distances) <= 4,
        "max_step": rational(max(distances)),
        "endpoint_displacement": rational(abs(xs[-1] - xs[0])),
        "max_excursion": rational(max(prefixes)),
        "total_variation": rational(sum(distances)),
    }


def check_config(config):
    expected = {"protocol_version": "0.1", "run_id": "audit-20261011-001", "keys": ["A", "B"],
                "coordinates": ["0", "1/2", "1", "3/2", "2"], "lengths": [2, 3, 4],
                "epsilon": "1", "budget": "1", "expected_path_count": 11100,
                "wall_seconds": 60, "memory_bytes": 134217728,
                "seeds": "not applicable: deterministic exhaustive enumeration"}
    if config != expected:
        raise ValueError("Configuration differs from frozen protocol")


def replay(stream, config, guard=lambda: None):
    check_config(config)
    domain = [(k, x) for k in ("A", "B") for x in ("0", "1/2", "1", "3/2", "2")]
    counters = {name: {"antecedent_count": 0, "counterexamples": 0, "first_witness": None} for name, _, _ in PAIRS}
    by_length = {str(n): 0 for n in (2, 3, 4)}
    index = 0
    for line in stream:
        if index % 128 == 0:
            guard()
        if index >= 11100:
            raise ValueError("Extra path")
        row = json.loads(line)
        if index < 100:
            length, rank = 2, index
        elif index < 1100:
            length, rank = 3, index - 100
        else:
            length, rank = 4, index - 1100
        digits = []
        for _ in range(length):
            rank, digit = divmod(rank, 10)
            digits.insert(0, digit)
        expected_states = [{"key": domain[d][0], "x": domain[d][1]} for d in digits]
        if set(row) != {"ordinal", "states", "measurements"} or row["ordinal"] != index or row["states"] != expected_states:
            raise ValueError(f"Coverage/order mismatch at {index}")
        m = independent_measure(row["states"])
        if row["measurements"] != m:
            raise ValueError(f"Measurement mismatch at {index}")
        for name, a, b in PAIRS:
            counter = counters[name]
            counter["antecedent_count"] += int(m[a])
            if m[a] and not m[b]:
                counter["counterexamples"] += 1
                if counter["first_witness"] is None:
                    counter["first_witness"] = row
        by_length[str(length)] += 1
        index += 1
    guard()
    if index != 11100:
        raise ValueError("Incomplete enumeration")
    for name in ("exact_local_endpoint", "exact_local_prefix", "variation_prefix"):
        if counters[name]["counterexamples"]:
            raise ValueError(f"Failed positive control: {name}")
    return {"path_count": index, "by_length": by_length, "signatures": counters}
