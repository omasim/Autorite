# RP005A — Preparation review and next execution stage

2026-10-11. Explicit internal self-review of operational protocol v0.1. This is preparation review, not package disposition, external peer review or a recorded research audit.

## Contract and readiness assessment

The supplement preserves the frozen edge-removal inclusion, V0–V2 regimes, three planner profiles, primary constraint-relative measure and secondary underlying measure. It fills PC03 with exact source/targets/actions, graph admissibility, unit resource budget, horizons, tie-breaking and a bounded existential viability criterion. It changes no baseline definition.

Five targets and their original denominator remain fixed across both arms. Primary comparison uses each arm's admissible graph; secondary holds the underlying graph fixed. The exact decomposition separates endpoint selection from deleted future paths. C0 exposes downstream coverage loss even when the selected endpoint is unchanged. A higher ratio cannot be manufactured by removing targets from the denominator.

The restriction designer uses full graph knowledge. Reward maximization differs from future-target coverage, and the planner must take an action at a nonterminal. These are deliberate synthetic mechanisms, not hidden fairness assumptions or learned-policy evidence. H=4 is sufficient only for these short DAGs. One executed action and three future transitions are distinct from planning horizon and from indefinite viability.

All expected choices and coverage counts are disclosed in the fixtures. Preparation checks cover four graphs, 24 planner rows, 12 paired comparisons and structural inclusion from 35 sources. Twelve software tests include independent exhaustive reward-plan enumeration and a separately constructed Boolean closure, tie order, delayed penalties, resource bounds, forced negative actions, target/graph validation and corrupted expected controls. These checks establish software behavior on engineered controls, not independent scientific discoveries. No run is created.

The targeted prior-art review acknowledges standard discrete planning/dynamic programming and finite-horizon constrained control, with exact inspection boundaries. No novel constraint algorithm, viability-kernel computation or stability result is claimed.

## Remaining before recorded execution

Build a bounded saved-output audit, frozen configuration/source/input inventory and independent serialized replay. Review that implementation before running. Replay must reconstruct from raw graph data without importing the producer's planner/reachability/scoring helpers; independently enumerate plans and compute resource-bounded target distances. Verify all candidate scores, complete coverage, exact paired decompositions, structural certificates and hash inventories. A pass count alone is insufficient.

The execution contract proposes one deterministic 60-second/128-MiB attempt with Python >=3.11 and no audit network. Preserve failures; do not silently retry or change rewards/targets/horizons after observing outcomes. Preparation is sufficient to build that audit, not a claim that its execution gate is already complete.

## Current status and checks

`python3 scripts/check-rp005a-preparation.py`, the twelve adversarial/independent software controls, frozen baseline integrity, typed schema and English document/link checks are required before publication; CI repeats the repository suite.

RP-005A remains PLANNED and Q-2 remains ACTIVE. No RP005A Test, Result or Claim exists. RP002A, RP003 and RP004 remain CLOSED under D-0004/D-0005/D-0006. Cycle 01 remains ACTIVE at 3/13 resolved (23.1%); protocol preparation resolves no obligation. DAM X still requires supplied source documents. Next is implementation and review of the finite reproducibility audit, not a new execution in this preparation stage.

[Operational protocol](https://autorite.net/sources/rp005a-operational-protocol/) · [Prior-art review](https://autorite.net/sources/rp005a-prior-art/)
