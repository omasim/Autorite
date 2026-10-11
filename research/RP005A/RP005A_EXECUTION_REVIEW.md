# RP005A — Pre-execution implementation review

2026-10-11. Explicit internal self-review of the saved-output implementation. The user requested continuation into recorded experiment code and independent verification. The operational protocol, disclosed fixture expectations and frozen baseline remain unchanged. This stage implements and reviews the audit; it does not execute a research run.

## Registered inventory and measurements

Configuration v0.1 fixes V0, V1, V2 and auxiliary C0; horizons 1,2,4; unrestricted/restricted arms; five target IDs; and a separate three-transition future budget. Test TST-RP005A001 registers the scoped inquiry into Q-2, with no epistemic Test status or Result.

The 24 planner rows are ordered by case inventory, horizon, then arm. Every row saves source, target universe, removed edges, endpoint, each candidate destination and exact truncated reward score, the primary/underlying target sets, counts and the original denominator. The 12 paired records save both planner ordinals, endpoints, exact reduced primary/selection/deletion fractions and the primary sign. Negative and zero comparisons are retained.

The 35 structural records use case inventory then lexically sorted source nodes. They save full and restricted reachable-node/target sets, lost nodes/targets, and inclusion checks for both unbounded reachability and the fixed future budget. Each family checks all 313 ordered source/destination pairs. The source s record retains the original loss of options beside any endpoint-selection gain.

The producer uses the reviewed dynamic-programming planner and frontier reachability. Independent replay imports none of its planner, scoring, graph-validation or reachability functions. It independently validates the edge/target contract and uses indegree elimination to reject cycles; the producer uses recursive cycle detection. Replay enumerates all permitted reward paths to recover every candidate score, and computes all-pairs unit-transition shortest distances to reconstruct both raw and budget-bounded reachability. No disclosed expected answer or regime label is fed into its calculations.

## Verification before a research attempt

Fourteen additional engineering tests operate on the previously disclosed controls and temporary synthetic artifacts, not a repository research run. They compare complete in-memory serialization and independently reconstructed values; corrupt targets, scores, denominator, budget, fraction reduction, paired references, raw/budget certificates and numeric types; reject missing/extra/duplicate/reordered records, duplicate JSON keys and nonfinite values; and exercise independent graph validation.

Separate tests check source-hash drift, committed-freeze requirements, actual authorization-note presence, fresh-directory refusal, and preservation of failure metadata before any target output. An incomplete artifact never supports a VALID Result. These tests are software verification of deliberately disclosed cases; their in-memory computations and temporary artifacts are not an independently discovered benefit or general frequency estimate.

## Source/input freeze and invocation

The [source freeze](https://autorite.net/sources/rp005a-source-freeze/) records one reviewed implementation commit, all 16 exact input SHA-256 hashes and the immutable numerical configuration. Its JSON sidecar is committed before execution. The sidecar and rendered freeze note are provenance records outside their own 16-file input inventory, avoiding a self-referential commit/hash.

The runner requires Python >=3.11, a clean tracked checkout, a committed freeze sidecar and all input bytes matching both the named commit and the recorded hashes. It refuses an existing run directory. A genuine execution instruction must be recorded in the required `--authorization-note` parameter; neither software checks nor Test registration manufacture that authorization.

The reserved first-attempt ID is audit-20261011-001. The date in this predeclared identifier marks its registration; started_at/ended_at record actual UTC execution times. After this preparation is merged and a recorded attempt is requested, invoke:

```text
python3 scripts/run-rp005a-audit.py --run-id audit-20261011-001 --authorization-note "Actual user execution instruction and date"
```

The quoted note is a placeholder for the real instruction, not an existing authorization to execute in this preparation stage. Independent verification uses `python3 scripts/check-rp005a-audit.py`; before a run it verifies the 16-file freeze only.

## Resources, artifacts and failure handling

One process, one deterministic attempt, no random seeds and no network in the audit. A 60-second alarm and monotonic guards cover generation plus independent replay; process peak RSS must stay at or below 128 MiB. Guards run before target output, between rows/certificates and inside independent enumeration/distance calculations, plus a final resource check. The standard-library process avoids loading the prior learning packages.

Persist the committed source/input snapshot before computing the target corpus. Eight completed-run files are declared: manifest, frozen-inputs, planner, pairs, structural, summary, replay and timing. The manifest binds the seven output hashes, complete file inventory, source-freeze hash, exact configuration, environment and actual authorization note. It does not hash itself. Later schema validation compares full run bytes with their first committed snapshot.

On exception, preserve partial files and failure.txt, set timing to INCOMPLETE and hash every preserved output. Final resource failure retains its earlier failure reason. Never overwrite, auto-retry, impute omitted comparisons or label the artifact COMPLETE. A revised attempt needs a new reviewed configuration/identity; original evidence remains. A VALID Result can be created only after complete provenance, output hashes, resource checks and full independent replay pass.

## Interpretation and present status

The exact primary difference decomposes into endpoint selection plus nonpositive edge-deletion loss. It describes only these supplied rules, small graphs, reward objective, forced action, horizons and future budget. It is neither empirical confirmation nor a proof that restrictions usually help. Secondary underlying coverage remains counterfactual when it uses forbidden paths. The separate structural inclusion cannot be reinterpreted as policy benefit.

RP-005A remains PLANNED and Q-2 ACTIVE. TST-RP005A001 is registered; there is no recorded RP005A attempt or Result. RP002A/RP003/RP004 remain CLOSED. Cycle 01 remains ACTIVE at 3/13 (23.1%). Next is the single bounded recorded audit after this reviewed freeze is committed; no obligation is resolved by implementation readiness.
