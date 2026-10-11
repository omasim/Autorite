# RP005A — Targeted prior-art collision review

Reviewed 2026-10-11 during protocol preparation. This is a bounded primary-source check, not an exhaustive search or novelty clearance. No research outcome or broad Claim is promoted.

## Discrete graph planning and finite-horizon optimization

Steven M. LaValle, *Planning Algorithms*, Cambridge University Press, 2006. Inspected the author-hosted HTML [section 2.1.1, Problem Formulation](https://lavalle.pl/planning/node37.html) and [section 2.3.1, Optimal Fixed-Length Plans](https://lavalle.pl/planning/node53.html), including their definitions and overview paragraphs. The backward/forward algorithm subsections and complete book were not audited.

The formulation uses a state space, applicable actions, a transition function, an initial state and a goal set, and describes a directed transition-graph representation. The optimal-planning overview contrasts enumerating action sequences with dynamic programming. RP005A's finite graph and exact truncated reward recursion therefore use established machinery. Exhaustive enumeration is a feasible independent check here because the graphs are deliberately tiny; it is not a new scalable planning algorithm.

Collision boundary: the edge-removal inclusion is elementary path containment. Our one-action future-target coverage is a chosen diagnostic, not a claim that the planner maximizes target coverage or solves every planning objective. No novelty follows from a disclosed delayed-cost counterexample.

## Constraints, predicted costs and a limited moving horizon

J. Mattingley, Y. Wang and S. Boyd, *Receding Horizon Control: Automatic Generation of High-Speed Solvers*, IEEE Control Systems Magazine 31(3):52–65, June 2011. Inspected the author-hosted [publication metadata and abstract](https://web.stanford.edu/~boyd/papers/code_gen_rhc.html). The full paper, numerical examples and solver performance results were not inspected.

The abstract describes repeatedly optimizing predicted future costs and constraints over a moving horizon to choose control actions. Thus combining constraints with limited-horizon optimization is established background. RP005A studies one synthetic first decision rather than repeated MPC, and imports no stability, recursive feasibility or runtime guarantee. Its supplied restriction rule and reward/coverage mismatch must remain explicit.

## Scope left open

Our assessment: a deliberately supplied rule can remove an attractive branch, but its information and design cost are outside the comparison. Bounded target reachability here is not an audited viability-kernel algorithm, robust-control model or safety-shielding benchmark. No claim that the two inspected sources exhaust those literatures is made; comparison with learned restrictions, uncertain dynamics, multi-step policies and richer viability methods requires a separate scoped review before any such claims.

RP-005A remains PLANNED. Existing sources contextualize the machinery; they do not establish Autorite's broader conceptual program or a universal restriction benefit.
