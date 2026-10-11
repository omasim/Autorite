# RP003 — Operational protocol v0.1

Prepared 2026-10-11. **Preparation and known-answer calibration only; no research run or Result is recorded.** This supplement operationalizes the frozen [baseline protocol](https://github.com/omasim/Autorite/blob/main/baseline/v0.1/RP003_PROTOCOL.md) and PC01 without changing them. The package remains PLANNED; Q-0 remains ACTIVE. Expected outcomes below are disclosed before execution because these examples are constructed to illustrate known distinctions.

## Question and scope

When do judgments about adjacent states justify a judgment about the endpoints or the whole path? The subject is a finite ordered sequence of synthetic states, not a person, organism or metaphysical identity. The selected feature and tolerance determine what “preservation” means. Equality of that feature is not equality of the whole subject.

## State, transformations and composition

A state is `(key, x)`, where key is A or B and x is an exact rational coordinate. A path contains at least two states. Transitions may translate x by a rational increment and may replace key. All listed transitions are admissible; admissibility is separate from preservation. Composition concatenates transitions sharing the same intermediate state. Translations add; relabeling retains the final assigned key. No cost, probability, elapsed time, lineage or unobserved intermediate state is inferred. A two-state critical jump is a single observed transition, not a claim about an interpolated trajectory.

The subject/type, admissible transformations, chosen features, tolerances and observation granularity form the criterion signature. Changing any of them requires a new protocol version, rather than pooling judgments across signatures.

## Predicates and path measures

Use inclusive tolerance epsilon = 1 and variation budget B = 1, in synthetic coordinate units. Neither is fitted to observations. Fractions are evaluated exactly; no floating-point slack is allowed.

| Judgment | Definition for path s0, …, sn |
| --- | --- |
| Exact-feature local | Every adjacent pair has equal key |
| Exact-feature endpoint | key(s0) = key(sn) |
| Exact-feature prefix | Every key(si) = key(s0), including i = 0 |
| Tolerance local | Every adjacent absolute coordinate difference is at most epsilon |
| Tolerance endpoint | Absolute difference between xn and x0 is at most epsilon |
| Tolerance prefix | Every absolute difference between xi and x0 is at most epsilon |
| Variation budget | Sum of adjacent absolute coordinate differences is at most B |

Record each judgment separately, with maximum adjacent difference, endpoint displacement, maximum displacement from the initial state and total variation. Do not replace the tolerance relation by its transitive closure. In particular, a valid local tolerance judgment is not automatically a valid global judgment.

Equality of keys is the transitive positive control: local equality implies equality at every prefix and at the endpoint by induction along a finite path. This is an elementary mathematical argument, not a new discovery or a machine-checked proof. For rational coordinates, the triangle inequality bounds endpoint displacement by total variation. A variation budget B ≤ epsilon therefore suffices for all prefixes to remain within epsilon. It is a sufficient condition, not a necessary one. These arguments do not assert that an arbitrary preservation predicate is transitive.

## Deterministic P0–P3 fixtures

The executable fixture file is [FIXTURES.json](https://github.com/omasim/Autorite/blob/main/research/RP003/FIXTURES.json). Each tuple below lists key and rational coordinate.

| Case | Ordered states | Exact local / endpoint / prefix | Tolerance local / endpoint / prefix | Total variation / budget |
| --- | --- | --- | --- | --- |
| P0 transitive chain | (A,0), (A,1/2), (A,1) | true / true / true | true / true / true | 1 / true |
| P1 monotonic drift | (A,0), (A,3/4), (A,3/2) | true / true / true | true / false / false | 3/2 / false |
| P2 out-and-back loop | (A,0), (A,3/4), (A,3/2), (A,3/4), (A,0) | true / true / true | true / true / false | 3 / false |
| P3 critical jump | (A,0), (B,3/2) | false / false / false | false / false / false | 3/2 / false |

P1 supplies a three-state tolerance witness. No two-state path can have local tolerance true and endpoint tolerance false, since the two tests then inspect the same pair. “Minimal” here means fewest observed states for this implication; it does not minimize displacement over the rational numbers. P2 shows why endpoint return cannot certify every prefix. P3 ensures the checker can reject an individual violating transition and a changed exact feature.

## Planned bounded enumeration

After this supplement and its implementation are committed and reviewed, the next stage will enumerate every ordered path of 2, 3 or 4 states drawn from `{A,B} × {0,1/2,1,3/2,2}`. Repetition is allowed; all adjacent transitions are admissible. There are exactly 100 + 1,000 + 10,000 = 11,100 paths. The five-state P2 fixture is checked separately, outside this enumeration. P1 and P2 contain 3/4, outside the enumeration grid; they remain independent calibration cases.

For each predicate signature, count local-to-endpoint and local-to-prefix failures, endpoint-to-prefix failures and any violation of the sufficient variation bound. Search order is increasing state count, then lexicographic state order (key A before B, coordinate increasing). Retain the first witness for each implication and its exact measurements. Verify each witness independently from its saved states and relation definition, including every antecedent and failed consequent. Minimality is only within the stated grid, ordering and path lengths; do not claim all-domain minimality from enumeration.

This stage is a deterministic mathematical audit, not a statistical confirmation or a novelty test. No sampling, seed, fitted parameter, p-value or confidence interval is applicable. Finite counts describe the listed domain only. General implications need their own explicit mathematical argument; passing this grid does not prove them on arbitrary state spaces.

## Reproducibility and acceptance

Preparation command: `python3 scripts/check-rp003-preparation.py`. It checks the four known-answer fixtures and protocol references; it does not run the planned enumeration. Unit checks cover inclusive boundaries, exact rational arithmetic, invalid inputs, separation of endpoint/prefix/variation and corrupted calibration expectations.

Before a research run, freeze the full Git commit and SHA-256 of this protocol, fixtures, implementation and collision review in a new run manifest. Record Python version, OS, command, start/end times, elapsed monotonic time and the deterministic “seed: not applicable” statement. Use Python 3.11 or later, standard library only, one process; ceiling 60 seconds and 128 MiB for the enumeration, no network. Stop on any invalid state, failed control, arithmetic error, witness replay discrepancy or exceeded budget. Preserve all partial artifacts as INCOMPLETE; never overwrite a run or emit a VALID Result on failure.

Acceptance requires all four calibration signatures and exact measures to match, all 11,100 enumerated paths to be accounted for, independent witness replay, the two positive-control implications and the variation sufficient condition to have zero counterexamples, and hashes of all outputs to match. A negative tolerance implication is an expected outcome, not a failed control. A witness or count alone does not close the package: interpretation review must assess criterion signatures, path information requirements and limitations. Any protocol change after inspecting enumeration outcomes is disclosed as a deviation and requires a fresh version/run.

## Prior art and interpretation lock

The [collision review](https://autorite.net/sources/rp003-prior-art/) identifies prior work on tolerance relations and invariance. We claim no novelty for transitivity, non-transitive metric tolerance, triangle inequalities or induction. A potential contribution is a traceable criterion-by-criterion research record; its value and generality remain to be assessed. No metaphysical identity theory, general lineage result, empirical human judgment, broad Claim or Cycle resolution follows from these preparations.
