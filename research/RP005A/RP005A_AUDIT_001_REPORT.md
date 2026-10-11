# RP005A — Audited restrictions and horizon-limited planning

2026-10-11. Run `audit-20261011-001` is COMPLETE. Test TST-RP005A001 has scoped Result R-RP005A001 (VALID). RP005A is ACTIVE pending package interpretation and disposition; Q-2 remains ACTIVE. Cycle 01 remains ACTIVE at 3/13 (23.1%).

## What was audited

Four predeclared directed acyclic graphs, V0/V1/V2 and auxiliary C0, were evaluated at planning horizons H=1,2,4 under unrestricted and restricted edge sets. The exact truncated reward planner executes one first action. From its selected endpoint, primary coverage counts terminal targets reachable in that arm's graph within a separate future budget B=3 transitions. Both arms retain the same five targets and denominator; zero-length paths count. This is an existential option count, not actual visitation, a trajectory visiting all targets, a viability kernel or indefinite safety.

The implementation and all sixteen inputs were pinned before execution to [fe796a089df3e53101c20a20358391e84f59fc13](https://github.com/omasim/Autorite/commit/fe796a089df3e53101c20a20358391e84f59fc13). A source/input snapshot was written before calculating the saved corpus. The user requested continuation after the proposed single recorded audit; the actual instruction is retained in the manifest. The prior preparation already disclosed the expected controls. This audit records and independently verifies those finite constructions, rather than discovering an independent statistical effect.

## All paired outcomes

Coverage is a count out of the fixed five-target universe. Each row below binds two saved planner rows. Differences are exact fractions; +1/5 is a twenty-percentage-point coverage increase, not a twenty-percent relative gain.

| Case | H | Unrestricted endpoint | Restricted endpoint | Unrestricted coverage | Restricted coverage | Primary difference | Selection difference | Deletion difference |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |
| V0 | 1 | a | a | 3/5 | 3/5 | 0 | 0 | 0 |
| V0 | 2 | a | a | 3/5 | 3/5 | 0 | 0 | 0 |
| V0 | 4 | a | a | 3/5 | 3/5 | 0 | 0 | 0 |
| V1 | 1 | b | a | 2/5 | 3/5 | +1/5 | +1/5 | 0 |
| V1 | 2 | b | a | 2/5 | 3/5 | +1/5 | +1/5 | 0 |
| V1 | 4 | a | a | 3/5 | 3/5 | 0 | 0 | 0 |
| V2 | 1 | a | b | 3/5 | 2/5 | -1/5 | -1/5 | 0 |
| V2 | 2 | a | b | 3/5 | 2/5 | -1/5 | -1/5 | 0 |
| V2 | 4 | a | b | 3/5 | 2/5 | -1/5 | -1/5 | 0 |
| C0 | 1 | a | a | 3/5 | 2/5 | -1/5 | 0 | -1/5 |
| C0 | 2 | a | a | 3/5 | 2/5 | -1/5 | 0 | -1/5 |
| C0 | 4 | a | a | 3/5 | 2/5 | -1/5 | 0 | -1/5 |

V0 removes an unselected branch: no endpoint or primary coverage change. V1 removes the attractive delayed-cost branch; H=1/2 selects a better-covered endpoint, while H=4 already avoids the trap. V2 removes the useful branch and forces the less-covered endpoint. C0 retains the same selected endpoint but deletes one of its future targets; a smaller denominator would hide this loss. All zeros and negatives remain in the record.

There are two positive, four zero and six negative paired comparisons. Counts summarize this deliberately designed corpus and correlated horizon evaluations, not restriction-benefit frequencies, independent replicates or uncertainty estimates.

## Endpoint selection and structural loss

Write C_E(x,B) for the fraction of the fixed targets reachable from x in graph E within B transitions. With restricted edges E_K contained in E, unrestricted endpoint x_E and restricted endpoint x_K:

```text
Delta = C_EK(x_K,B) - C_E(x_E,B)
S     = C_E(x_K,B)  - C_E(x_E,B)
L     = C_EK(x_K,B) - C_E(x_K,B) <= 0
Delta = S + L
```

The independent replay verifies this exact decomposition for every pair. S is a counterfactual endpoint-selection comparison on the original graph; it may use paths forbidden in the restricted arm. It is not the restricted arm's feasible future. V1's gain is selection, never the creation of a new structural option. C0 isolates deleted future paths at the unchanged endpoint.

All 35 source records independently pass unrestricted/restricted inclusion, both without a budget and at B=3. Each family checks 313 ordered source/destination pairs. Pure edge removal cannot produce a path absent in the original graph: each retained path is already an original path with the same transition cost. The certificates verify this property on the supplied corpus; the path argument supplies its stated general graph condition.

| Case | Original source s targets, no budget | Restricted source s targets, no budget | Lost targets |
| --- | ---: | ---: | --- |
| V0 | 5/5 | 3/5 | t4,t5 |
| V1 | 5/5 | 3/5 | t4,t5 |
| V2 | 5/5 | 2/5 | t1,t2,t3 |
| C0 | 5/5 | 2/5 | t3,t4,t5 |

These source-level losses are separate from the post-action primary measure. In V1, t4/t5 require four transitions from s, so the original and restricted source-level B=3 target counts are both 3/5. From selected b they require three; post-action coverage is consequently 2/5. The budget origin must stay explicit.

## Independent replay, provenance and resources

The independent verifier imports no producer planner, graph validator, scoring or reachability code. It independently rejects malformed graphs and cycles by indegree elimination, enumerates permitted reward paths to reconstruct all candidate scores, and computes all-pairs unit-transition shortest distances for reachability. It verifies exact types, complete inventory and ordering, target sets, all 24 planner rows, 12 pairs, 35 structural records, each difference and the summary. Seven output hashes and sixteen input hashes match.

One process, no random seed and no network in the audit. Python 3.12.14; 0.024353542 monotonic seconds, with 29,442,048 bytes peak resident memory (28.08 MiB), within the predeclared 60-second / 128-MiB limits. No failure or retry occurred. The eight-file run was committed before outcome interpretation and is immutable; the runner refuses an existing directory.

- [Manifest](https://github.com/omasim/Autorite/blob/main/research/RP005A/runs/audit-20261011-001/manifest.json) and [frozen input snapshot](https://github.com/omasim/Autorite/blob/main/research/RP005A/runs/audit-20261011-001/frozen-inputs.json).
- [All planner rows](https://github.com/omasim/Autorite/blob/main/research/RP005A/runs/audit-20261011-001/planner.jsonl), [all pairs](https://github.com/omasim/Autorite/blob/main/research/RP005A/runs/audit-20261011-001/pairs.jsonl) and [all structural certificates](https://github.com/omasim/Autorite/blob/main/research/RP005A/runs/audit-20261011-001/structural.jsonl).
- [Summary](https://github.com/omasim/Autorite/blob/main/research/RP005A/runs/audit-20261011-001/summary.json), [independent replay](https://github.com/omasim/Autorite/blob/main/research/RP005A/runs/audit-20261011-001/replay.json) and [timing](https://github.com/omasim/Autorite/blob/main/research/RP005A/runs/audit-20261011-001/timing.json).

Verification: `python3 scripts/check-rp005a-audit.py` reads preserved evidence without creating a replacement run. The [Test registration](https://github.com/omasim/Autorite/blob/main/research/RP005A/audit-001/RECORD.md) remains a pre-execution snapshot; the separate [Result](https://github.com/omasim/Autorite/blob/main/research/RP005A/audit-001/result/RECORD.md) records the outcome.

## Explicit internal outcome review

The scoped evidence is accepted as VALID after full coverage, frozen source/input provenance, complete output hashes, resources and independent full-value replay pass. No protocol, fixture, budget, target, objective, horizon, restriction or expectation changed after observation. VALID concerns this audited finite corpus and its record.

The designer knows the complete graph and supplied rewards; learning or enforcing restrictions is not modeled. Reward maximization differs from target coverage. Horizons 1/2/4 and lexical labels affect choices; H=4 is sufficient for these fixtures only. Tiny deterministic DAGs do not establish performance on arbitrary graphs, stochastic systems, uncertainty or real actors. The audit supplies no optimal restriction rule, general benefit frequency, novelty claim, confidence interval or proof that restrictions are usually needed.

RP005A is ACTIVE pending separate package interpretation/disposition. Q-2 remains ACTIVE; no broad Claim or Cycle obligation is resolved. Next: review the scoped commitment, exclusions and reopening conditions before deciding package disposition. Read the [preserved operational protocol](https://autorite.net/sources/rp005a-operational-protocol/), [pre-execution review](https://autorite.net/sources/rp005a-audit-execution-review/) and [source freeze](https://autorite.net/sources/rp005a-source-freeze/).
