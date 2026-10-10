# RP002A first confirmation attempt — incomplete

Report date: 2026-10-10 (Europe/Istanbul). Run `confirmatory-20261009-001` was attempted once under the frozen protocol. It is **incomplete**, with no full-family inference or confirmatory decision.

## Disposition

The first three requested steps completed: fixed synthetic statistical calibration, a fresh target-size variance assessment and a pre-outcome frozen count/analysis/budget. The fourth step was executed once, then stopped following a wall-time incident. **36/60 independent units and 73/120 saved learned-fit traces** exist. E0 completed 20 units, E1 completed 16, E2 completed none. An additional E1 unit retains data, its B0 table and one completed learned checkpoint/trace; it has no assessment aggregate. The interrupted model has no completed trace/checkpoint.

`failure.txt` records the SIGINT/KeyboardInterrupt and the immutable manifest hashes all 295 preserved outputs. There is no `summary.json`, no complete seven-comparison decision family and no VALID Result. Partial assessment values are not pooled, extrapolated or presented as confirmatory evidence. No retry, extension, replacement seeds or alternative analysis is performed or authorized.

## Clock incident and stopping rule

The frozen allowance was 14400 seconds/four hours. An external UTC observation at launch was 2026-10-09 20:20:23 UTC. At 2026-10-10 07:11:46 UTC, before the stop, more than ten hours of civil time had elapsed. After process exit, the external clock read 2026-10-10 09:08:55 UTC. These are observations surrounding tool calls, not instrumented exact process timestamps; they establish the four-hour overrun but do not establish an exact suspension interval or signal-delivery timestamp.

The original manifest records 5099.254370500 seconds (84.99 minutes) under `elapsed_wall_seconds`. The original implementation used **`time.monotonic()`**, not suspension-inclusive wall time. That immutable field is mislabeled for this incident and is preserved as historical evidence, not retrospectively rewritten. On this host Python reports `mach_absolute_time()` for its monotonic clock. Host suspension is consistent with the discrepancy; external clock discontinuity is not independently ruled out. Either explanation prevents treating the recorded 85-minute interval as a verified four-hour civil-time gate.

The process was stopped conservatively under the declared wall-time limit. A completed benchmark was not manufactured from fewer units. [Python's clock documentation](https://docs.python.org/3.9/library/time.html#time.monotonic) describes how `get_clock_info()` exposes the underlying implementation; [Apple's public kernel clock definitions](https://github.com/apple/darwin-xnu/blob/main/osfmk/mach/mach_time.h) distinguish the clock that advances during sleep. These sources explain the mechanism; they do not prove this host's exact sleep history.

## Preserved artifact audit

All 295 output hashes and manifest/source/approval/seed provenance verify. The auditor regenerates the completed units' datasets and replays B0/B3 reference predictions, selected B1/B2 checkpoint predictions, original-precision losses, secondary diagnostics and trace summaries **without optimization or statistical aggregation**. The incomplete unit's datasets/B0 table regenerate and its saved checkpoint loads with finite weights; there is no saved assessment against which to replay that incomplete checkpoint's predictions.

The run retains 144 model assessment records across 36 complete units, exact compressed data, saved weights/traces and per-unit metrics. These are preserved diagnostic artifacts, not a reduced confirmatory sample. Lifetime peak resident memory recorded by the process is 312066048 bytes (297.61 MiB), raw macOS `RUSAGE_SELF.ru_maxrss` in bytes, including imports and all fits. The historical peak cannot be recreated by replay.

- Execution source: `b2ee2548b8c6206b807af9de311b01c180b9ce29`.
- Frozen configuration SHA256: `a84c08db5b7891aac7eb6be5bc8f00e7980904441dec516df438f089a4acc7c9`.
- Source-bound approval SHA256: `c4eb36c6ebfcca5b7440020ed617fe97377f3f9339875a31a3159b8770d088a6`.
- Manifest SHA256: `d4106db6cfab999ad5e5e27a0b666c91d480e2b12c4c3625bf7f4ea8dfdd83d6`.
- Environment: Python 3.9.6, NumPy 2.0.2, PyTorch 2.8.0, SciPy 1.13.1; macOS arm64 CPU, two threads.
- Test `TST-RP002A001` remains registered. No VALID Result or broad Claim is created.

## Completed prerequisites remain separate

Synthetic calibration completed 90 predeclared cells/1.8 million trials and qualified counts 20,30,50 under its simulation gate. Simulated coverage is not actual-loss or distribution-free coverage. The fresh variance stage completed five independent training replicates per world and 30 learned fits. Only its SDs entered the fixed selection rule, which chose 20 confirmation replicates per world. Their means stay descriptive; their samples are never substituted for missing confirmation units.

The frozen design kept 4096 training, 1024 validation and 2048 assessment episodes per unit, 129 observations/128 pairs, 300-epoch cap/patience 20, seven twofold-inflated Student-t Bonferroni intervals and .01-nat fixture-specific margins. That design is preserved even though this attempt is incomplete. Earlier proposal and run bytes remain unchanged.

## Repair and remaining gate

The current source uses a dual wall/monotonic guard at stage/model/batch checks. Expiry of either clock stops a future authorized attempt, so a forward civil-clock jump is handled conservatively and a backward jump cannot extend the monotonic allowance. Future manifests also hash explicit UTC/two-clock timing records. Tests exercise a paused monotonic clock with advancing wall time, a backward wall adjustment and interruption before an optimizer step. No new observations or training are run by these checks.

This implementation repair is not approval for another experiment. The existing source-bound approval and unique run directory cannot silently authorize a changed-source retry. A new run would require a separately reviewed plan, fresh namespace and source-bound authorization. RP002A and Cycle 01 remain ACTIVE; 0/13 obligations are resolved. No universal memory, necessity of recurrence, foundational theory or Cycle closure follows from this partial record.

[Raw preserved attempt](https://github.com/omasim/Autorite/tree/main/research/RP002A/runs/confirmatory-20261009-001) · [Interruption observations](https://github.com/omasim/Autorite/blob/main/research/RP002A/confirmation/INTERRUPTION_REVIEW.json) · [Frozen protocol](https://github.com/omasim/Autorite/blob/main/research/RP002A/CONFIRMATORY_PROTOCOL.md) · [Calibration review](https://github.com/omasim/Autorite/blob/main/research/RP002A/CALIBRATION_REPORT.md) · [Variance review](https://github.com/omasim/Autorite/blob/main/research/RP002A/TARGET_VARIANCE_REPORT.md)
