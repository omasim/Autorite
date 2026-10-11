# RP005A — Operational constraints and viable futures protocol v0.1

2026-10-11. Preparation supplement under PC03 to frozen `baseline/v0.1/RP005A_PROTOCOL.md`. RP-005A remains PLANNED; Q-2 remains ACTIVE. The four disclosed fixtures and their expected behavior are engineering calibration. No recorded research execution, Test, Result or Cycle resolution is created here.

## Subject, transformations and question

Can an edge-removal rule change a reward-based, horizon-limited first decision so that more declared future targets remain viable? Separate that policy question from the structural inclusion Reach_EK(x) subseteq Reach_E(x). Restrictions alter admissible edges, never nodes, transition rewards, targets or starting state.

Each fixture is a directed acyclic graph with at most 12 opaque named nodes and 32 unique edges. Each edge is a deterministic, unit-transition-cost action with an integer reward in [-100,100]. Rewards are preferences, not remaining resources or target values. Targets are a nonempty fixed list of terminal nodes; there are five in every disclosed fixture. The source is s. No stochastic transition, learning, hidden state, target importance weight or empirical population is modeled.

The finite restriction K is a predeclared list of distinct existing edges to remove: E_K = E minus K. The rule is supplied by the fixture designer using full graph knowledge. Rule discovery, policy learning and the cost of discovering/enforcing K are outside this audit. No claim that an uninformed agent could infer the protective restriction is made.

## Structural statement and its independent check

Every E_K path is an E path because each of its edges belongs to E. Thus pure removal cannot create a new reachable node from a fixed source. Zero-length paths count in both graphs, including terminal/self reachability. The same inclusion holds when both paths have the same transition budget. This elementary argument is background, not a new theorem or a simulated benefit result.

The future recorded audit must independently reconstruct Boolean transitive closure for both graphs and compare every source/destination pair: 35 source nodes across four fixtures, 313 ordered pairs. Save one inclusion record per source with both reachable-node lists, not just an aggregate pass count. The preparation implementation uses frontier expansion; its unit control compares a separately constructed Boolean matrix closure. Independent run replay remains to be implemented.

## Planners, horizons and one-action execution

Profiles are greedy H=1, short H=2 and sufficient-for-these-fixtures H=4. Both arms use the same exact truncated reward maximizer; the only intervention is the available edge set. Every outgoing action is applicable unless deleted by K.

Define J_0(x)=0. For a terminal/dead-end node J_h(x)=0. Otherwise J_h(x)=max over outgoing (x,y) of [reward(x,y)+J_(h-1)(y)]. Choose the first action with maximal reward(x,y)+J_(H-1)(y). Exact ties choose the lexicographically smallest destination ID; input node/edge list order does not matter. This label-sensitive rule is part of the contract, not invariant under arbitrary renaming. There is no voluntary stop at a nonterminal, discount, terminal heuristic or viability lookahead added to the reward objective. A terminal stays put with an empty action-score list.

Execute exactly that first action, not the whole optimizing plan or a repeated receding-horizon rollout. Measure remaining opportunities at its destination. If no action exists, the source is the endpoint. The future viability budget B=3 transitions is identical across arms/profiles, independent of H. H=4 sees every complete path from s in these fixtures; it does not imply a sufficient horizon on arbitrary graphs. Keeping planner horizon and future budget distinct prevents a change in evaluation budget from masquerading as policy benefit.

## Fixed-denominator measures and exact paired decisions

A target is viable from x in graph F if at least one F path of length at most B reaches it, including a zero-length path. This is bounded existential target reachability, not a viability kernel, robust safety, indefinite survival, realized target visitation or a promise that one trajectory can visit all terminal alternatives.

Let C_F(x,B)=number of declared targets reachable within B, divided by the original |T|=5. Use the identical original target list and denominator for both arms and all horizons; never discard targets made unreachable by K.

For the unrestricted endpoint x_E and restricted endpoint x_K:

- Primary: constraint-relative coverage C_E(x_E,3) versus C_EK(x_K,3). Each arm is judged under its own admissible graph, with the same targets and resource budget.
- Secondary: underlying coverage C_E(x_E,3) versus C_E(x_K,3). This compares the selected endpoints in the same original graph.
- Paired primary difference: Delta=C_EK(x_K,3)-C_E(x_E,3), classified positive/zero/negative by exact rational arithmetic. Secondary difference S=C_E(x_K,3)-C_E(x_E,3) isolates endpoint selection. Deletion term L=C_EK(x_K,3)-C_E(x_K,3) is nonpositive; Delta=S+L.

Save target IDs, counts, denominator, every candidate action score, endpoints, restriction lists and exact difference numerators/denominators. Secondary counterfactual coverage can include paths forbidden to the restricted arm; it is not restricted feasibility. Start-state raw and target reachability must also be retained so structural losses remain visible beside a possible policy gain. No pooling away adverse regimes, beneficial-only filter or normalized denominator based on surviving targets is permitted.

There is no sampling, seed schedule, learned fit, uncertainty interval or statistical test. The 12 paired comparisons are the entire specified case/profile inventory, not independent random units. Equalities and sign decisions are exact for those engineered cases, with no general benefit frequency or confidence claim.

## Disclosed fixtures and expected controls

All graphs have target list t1–t5. See the machine-readable fixture for the complete edge/reward inventory. V0, V2 and C0 share the same original graph: s→a gives reward 2, s→b gives 1; a leads to t1–t3 and b to t4–t5 with zero further reward. V1 replaces those branches with a short good route and a delayed-cost route.

| Fixture | Predeclared restriction | Expected behavior at H=1 / 2 / 4 |
| --- | --- | --- |
| V0: no trap, unnecessary restriction | Remove s→b | Both arms choose a and retain 3/5 future targets at every H; paired primary/secondary differences are zero. Root structural target reachability falls from 5 to 3 despite no policy benefit. |
| V1: attractive delayed-cost branch | Remove s→b | Good branch s→a→u→t1–t3 has rewards 2,1,0. Other branch s→b→d→e→t4–t5 has rewards 8,0,-20,0. H=1/2 choose b without restriction (2/5) and a with it (3/5). H=4 already chooses a in both arms; expected benefit vanishes. |
| V2: useful path removed | Remove s→a | Unrestricted arm chooses a (3/5); restricted arm chooses b (2/5), at every H. Both primary and secondary differences are -1/5. |
| C0: downstream deletion control | Remove s→b and a→t3 | Both choose a. Primary coverage falls 3/5→2/5; secondary remains 3/5. Selection term is zero and deletion term -1/5. This auxiliary measurement control is not a fourth baseline regime. |

These expectations are intentionally disclosed before the later audit. They are not independent discoveries or evidence that targeted restrictions usually help. There are four fixtures, three profiles and two arms: 24 planner/coverage rows and 12 paired comparisons. There are no random graph families or post-outcome reward/horizon sweeps.

## Reproducibility, stopping and next execution gate

Preparation uses Python's standard library and exact integer/rational arithmetic. Run `python3 scripts/check-rp005a-preparation.py` and `python3 -m unittest discover -s tests -p 'test_rp005a_planning.py'`. Checks create no run or research records. Fixtures reject duplicate/unknown nodes or edges, cyclic graphs, nonterminal targets, invalid rewards and restrictions that add edges or remove nonexistent ones.

The later bounded audit requires Python >=3.11, one deterministic attempt, no network during execution, a 60-second monotonic wall budget and 128 MiB peak RSS. These are execution caps, not statistical resource equivalence or a benchmark against another planner implementation. On failure, stop and preserve partial output/failure metadata; no automatic retry, missing-row imputation or changed parameters. A revised attempt needs a separately reviewed scope and new directory.

Before that attempt, commit an explicit implementation review, exact source/input hashes and frozen run configuration. Implement independent replay without importing the producer's planner, reachability, scoring or fixture-check functions: exhaustive reward-path enumeration and separately constructed reachability/shortest-distance tables must reproduce all action scores, target sets, pair signs and structural inclusions, checking complete serialized inventory and output hashes. Save every row and source certificate in a new immutable run. No current preparation output may substitute for that review, freeze or recorded audit.

## Interpretation limits

Deleting edges cannot expand raw reachability. A positive paired coverage difference can come from changing a myopic reward-driven choice, offset by lost paths. The reward/target mismatch, full-information designer, forced action, exact small DAGs, one-action evaluation, label-sensitive ties and fixed budget constrain interpretation. The sufficient profile can remove the apparent need for restriction; V2 and C0 retain harmful outcomes. No novelty, arbitrary-domain theorem, control-stability guarantee, ethical prescription, learned-policy advantage or broad Claim follows.

[Targeted prior-art review](https://autorite.net/sources/rp005a-prior-art/) · [Preparation review](https://autorite.net/sources/rp005a-execution-review/) · [Fixtures and expected controls](https://github.com/omasim/Autorite/blob/main/research/RP005A/RP005A_FIXTURES.json) · [Control implementation](https://github.com/omasim/Autorite/blob/main/research/RP005A/planning.py)
