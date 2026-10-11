# RP003 — Audited finite preservation enumeration

2026-10-11. Run **audit-20261011-001: COMPLETE**. Test TST-RP003001; audited Result R-RP003001. This is a deterministic mathematical audit of known distinctions, not a statistical confirmation or novelty claim. The operational protocol and baseline are unchanged.

## Execution and validation

The implementation and pre-execution internal review were committed as `3b432e39fe07c1fee37f2987d3d0ea45703dfcd1` before observing enumeration outputs. The input snapshot records SHA-256 of nine source files and the environment before output generation. All 11,100 ordered paths were saved: 100 with two states, 1,000 with three and 10,000 with four. Repeated states and all declared transitions are included.

Independent replay checked every row using integer quarter-units and ordinal decoding, without importing the rational evaluator. All measurements, eligible antecedent counts, failure counts and first witnesses match. P0–P3 calibration also passed independently. Five output hashes match the final manifest. A repository checker repeats full saved-data replay and provenance validation; this rechecks evidence without collecting a new research run.

Execution used Python 3.12.14 on macOS, one process and no network. Enumeration, replay and calibration completed in 0.366 seconds of monotonic time; peak process resident memory was 28,917,760 bytes (27.58 MiB). Both are below the declared 60-second and 128-MiB ceilings. The system-default Python 3.9.6 was rejected by the preflight version gate before a run directory or output existed; the supported bundled interpreter executed the single recorded run. This is an environment selection, not a changed protocol or outcome-dependent retry. No protocol deviation or incomplete research run is recorded.

## Counts by criterion

Each denominator counts paths satisfying the antecedent, not every enumerated path. Counts include ordered label/coordinate combinations and repetitions; they are not empirical prevalence estimates, independent samples or probabilities.

| Implication | Eligible antecedent paths | Counterexamples |
| --- | ---: | ---: |
| Exact-feature local → endpoint | 1,550 | 0 |
| Exact-feature local → every prefix | 1,550 | 0 |
| Exact-feature endpoint → every prefix | 5,550 | 4,000 |
| Tolerance local → endpoint | 5,396 | 848 |
| Tolerance local → every prefix | 5,396 | 1,136 |
| Tolerance endpoint → every prefix | 8,436 | 2,848 |
| Total variation ≤ 1 → tolerance at every prefix | 1,876 | 0 |

All required positive controls passed. A tolerance counterexample is an expected negative implication, not a failed control. The counts are for keys {A,B}, coordinates {0,1/2,1,3/2,2}, lengths 2–4, inclusive epsilon = B = 1 and unrestricted listed transitions only.

## First witnesses and minimality

The first witness to both tolerance-local implications is zero-based ordinal 113: `(A,0) → (A,1/2) → (A,3/2)`. The steps are 1/2 and 1, while endpoint displacement and maximum initial-state excursion are 3/2. Thus every local step passes and both global judgments fail.

The first tolerance-endpoint-to-prefix witness is ordinal 130: `(A,0) → (A,3/2) → (A,0)`. Endpoint displacement is zero; maximum excursion is 3/2. Its local tolerance is **false**: this witness tests endpoint sufficiency alone, not sufficiency of endpoint plus passing local steps. The independent, disclosed P2 calibration illustrates a returning path whose local steps do pass.

The first exact-feature-endpoint-to-prefix witness is ordinal 150: `(A,0) → (B,0) → (A,0)`. The endpoint key returns, but the intermediate key changes. No coordinate excursion is involved; exact-feature and metric judgments remain separate.

All first witnesses have three states. Complete order replay verifies there was no earlier witness within the enumerated grid and lengths. A two-state path compares the same pair for the relevant local/endpoint/prefix checks, explaining the elementary minimum of three observed states for these failures. This does not minimize rational displacement, infer unobserved states or prove arbitrary-domain classification.

## Criterion signatures and required path information

For a fixed exact feature, adjacent equality propagates by transitivity; endpoint equality alone can hide temporary feature changes. For fixed metric tolerance, passing local judgments requires the largest adjacent difference, endpoint judgment requires the endpoint displacement, and prefix judgment requires the largest excursion from the initial coordinate. The total variation sums all observed adjacent changes. These measurements answer different questions and cannot be substituted for one another.

If only endpoints are retained, temporary feature changes and coordinate excursions are lost. Retaining only a Boolean “all steps pass” loses cumulative drift. A reference-to-start maximum excursion suffices for the present prefix tolerance judgment; a running total variation supplies the stronger sufficient budget check. Retaining the ordered states enables independent verification of these summaries. This is an information requirement for these particular predicates, not a claim that full history is universally necessary.

Zero failures in the finite enumeration do not prove a general implication. Separate elementary arguments in the protocol justify the exact-feature transitivity and variation-bound implications: repeated equality, and the triangle inequality for each prefix. Those arguments are not machine-checked proofs or new mathematical results. Variation ≤ epsilon is sufficient but not necessary: `(A,0) → (A,1) → (A,0)` stays within the prefix tolerance while accumulating variation 2.

## Interpretation review and remaining work

Internal post-execution review checked completeness, independent replay, the pre-outcome commit, resource limits, calibration, antecedent denominators, witness premises and the distinction between enumerated evidence and general arguments. It accepts this evidence as a VALID scoped audit. It does not promote a broad Claim, resolve Q-0 or establish a metaphysical identity theory, empirical identity criterion, lineage result, arbitrary relation classification or general preservation theory. The targeted prior-art review remains explicitly non-exhaustive.

RP003 is ACTIVE. A separate package-disposition review must assess the finite commitment and any remaining work before closing it. Cycle 01 stays ACTIVE with 1/13 obligations resolved (7.7%); this run alone does not advance the ring.

## Reproducibility and artifacts

Read the [pre-outcome protocol](https://autorite.net/sources/rp003-operational-protocol/), [prior-art review](https://autorite.net/sources/rp003-prior-art/) and [pre-execution implementation review](https://autorite.net/sources/rp003-execution-review/).

Original artifacts are preserved in [the run directory](https://github.com/omasim/Autorite/tree/main/research/RP003/runs/audit-20261011-001): [manifest](https://github.com/omasim/Autorite/blob/main/research/RP003/runs/audit-20261011-001/manifest.json), [all saved paths](https://github.com/omasim/Autorite/blob/main/research/RP003/runs/audit-20261011-001/paths.jsonl), [counts and first witnesses](https://github.com/omasim/Autorite/blob/main/research/RP003/runs/audit-20261011-001/summary.json), [independent replay](https://github.com/omasim/Autorite/blob/main/research/RP003/runs/audit-20261011-001/replay.json), [timing](https://github.com/omasim/Autorite/blob/main/research/RP003/runs/audit-20261011-001/timing.json) and [pre-output input snapshot](https://github.com/omasim/Autorite/blob/main/research/RP003/runs/audit-20261011-001/frozen-inputs.json).

Verify preserved artifacts with `python3 scripts/check-rp003-audit.py`. Reproduction of new evidence requires a new declared run ID and new frozen configuration; the runner refuses the existing directory. Never overwrite this run.
