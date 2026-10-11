"""Exact finite-path judgments for RP003; no research-run side effects."""
from fractions import Fraction


def measure(states, epsilon="1", budget="1"):
    if not isinstance(states, list) or len(states) < 2:
        raise ValueError("A path needs at least two observed states")
    for s in states:
        if not isinstance(s, dict) or set(s) != {"key", "x"} or s["key"] not in ("A", "B"):
            raise ValueError("Invalid typed state")
        if not isinstance(s["x"], str):
            raise ValueError("Coordinates must be exact rational strings")
    xs = [Fraction(s["x"]) for s in states]
    epsilon, budget = Fraction(epsilon), Fraction(budget)
    if epsilon < 0 or budget < 0:
        raise ValueError("Negative tolerance or budget")
    steps = [abs(b - a) for a, b in zip(xs, xs[1:])]
    excursion = max(abs(x - xs[0]) for x in xs)
    variation = sum(steps, Fraction(0))
    return {
        "exact_local": all(a["key"] == b["key"] for a, b in zip(states, states[1:])),
        "exact_endpoint": states[0]["key"] == states[-1]["key"],
        "exact_prefix": all(s["key"] == states[0]["key"] for s in states),
        "tolerance_local": max(steps) <= epsilon,
        "tolerance_endpoint": abs(xs[-1] - xs[0]) <= epsilon,
        "tolerance_prefix": excursion <= epsilon,
        "variation_budget": variation <= budget,
        "max_step": str(max(steps)),
        "endpoint_displacement": str(abs(xs[-1] - xs[0])),
        "max_excursion": str(excursion),
        "total_variation": str(variation),
    }


def check_fixtures(config):
    if config["epsilon"] != "1" or config["budget"] != "1":
        raise ValueError("Protocol v0.1 fixes epsilon and budget at 1")
    if [c["id"] for c in config["cases"]] != ["P0", "P1", "P2", "P3"]:
        raise ValueError("Expected each frozen case once, in order")
    for case in config["cases"]:
        actual = measure(case["states"], config["epsilon"], config["budget"])
        if actual != case["expected"]:
            raise ValueError(f"Calibration mismatch: {case['id']}")
    return len(config["cases"])
