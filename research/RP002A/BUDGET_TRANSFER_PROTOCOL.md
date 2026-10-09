# RP002A target-data-size feasibility pilot protocol

Date: 2026-10-09. Version/seed namespace: `budget-transfer-proposal-0.1`. **Frozen, separately authorized and completed once.** Numerical specification: `BUDGET_TRANSFER_PLAN.json`. Run ID: `budget-transfer-20261009-001`.

## Purpose

Measure runtime and validation-trace behavior at the intended confirmatory data sizes before selecting an optimization/variance design. The earlier 256-training-episode stages leave this transfer untested. This is a small engineering feasibility pilot, not confirmation or an estimate of between-training variability.

## Fixed proposed scope

| Item | Proposed choice |
|---|---|
| Worlds / independent units | One fresh replicate in each of E0, E1 and E2; three units |
| Models | Existing B0 counts, B1 window-eight MLP, B2 12-state GRU, B3 observed-history filter |
| Learned-model fits | Six total: B1 and B2 per world |
| Episodes per unit | 4096 training, 1024 checkpoint-selection validation, 2048 independent assessment |
| Episode length | 129 observations, 128 prediction pairs |
| Optimization | Existing Adam 0.001, batch size 32, gradient clip 1; cap 300 epochs, patience 20 |
| Checkpoint selection | Minimum validation loss; assessment read only after selection |
| Execution order | World lexicographic, B1 then B2 |
| Machine | Python 3.9.6, NumPy 2.0.2, PyTorch 2.8.0; macOS arm64 CPU, two threads |
| Stage allowance | 3600 seconds; cooperative checks before phases/batches and after validation |
| Attempts | One fixed run ID, no retries or extension |

These data counts match the existing numerical confirmation proposal, but the exploratory stage keeps its own seeds, artifacts and purpose. Models, laws, information access, learning rate and metric remain fixed. Never warm-start from or reuse archived samples/checkpoints. The new namespace declares 21 seeds: training/validation/assessment data and separate initialization/batch order for each learned model, independently for each world. The plan checker verifies disjointness from executed stages and the declared confirmation schedule.

At most 1800 learned-model epochs are allowed. Training size rises sixteenfold and validation size eightfold relative to stage 002, while the fit count falls from 40 to six. Scaling the prior 383.749-second wall time by 16 × 6/40 gives roughly 921 seconds. This is a rough planning illustration, not a benchmark or guarantee: actual stopping, validation cost, memory pressure and per-world behavior can differ. The fixed 3600-second allowance is a conservative bounded choice; it cannot be extended after observing performance.

## Outputs and interpretation

Retain datasets, hashes, seed schedule, environment/source, selected checkpoints, validation traces, epochs completed, best epoch, stop reason, per-fit/total wall times and peak process resident memory with explicit platform units. Report the existing final-30-cap, final-20 decline and secondary final-five diagnostics. Cap warnings remain warnings even when declines are small; early stopping is not proof of convergence.

For B0–B3, report one assessment episode-mean loss per world/model and the seven existing paired differences. There is **one training replicate per world**: do not calculate sample SD, leave-one-out replicate SD, inferential intervals, p-values, power, equivalence or confirmatory sample counts. Episodes/timepoints are not extra independently trained replicates. No cross-world pool or scientific Claim is allowed. Assessment losses cannot select or tune a follow-up budget.

A successful pilot means only that all three units completed within this declared allowance and were audited. If any fit has a warning, optimization remains unresolved. If none has a warning, report absence of the declared warnings rather than proven convergence. Measured per-world runtime may inform explicit resource sensitivity tables for future replicate counts; it cannot guarantee the complete confirmatory workload or validate the currently proposed five replicates.

## Execution and failure boundary

`python3 scripts/check-budget-transfer-plan.py` checks the proposal and seeds without creating observations or training. The pilot entry point is now implemented: `python3 scripts/rp002a-convergence.py --stage 3` prints the plan only. `--execute --run-id budget-transfer-20261009-001` rejects execution before creating artifacts until its separately bound approval exists and the plan is frozen. The stage selector preserves the old default and previous artifact formats. Neither bootstrap nor stage-001/002 approval can authorize this pilot.

Bind any later approval to the exact frozen plan and unchanged baseline hashes, reviewed source commit, fixed run ID and pinned environment. Execute only from clean reviewed source. Preserve completed/partial files, traceback and manifest on failure or timeout; an incomplete stage has no complete-stage aggregate. Never replace seeds, retry, add fits or extend epochs/time without a separately reviewed future scope. Existing run directories remain immutable.

The broader confirmation design still needs an optimization rationale, variance assumptions, substantive margins, sample counts, calibrated uncertainty and a complete analysis implementation. Cycle 01 remains PLANNED at 0/13; no scientific status changes with this proposal.

## Execution preparation review — 2026-10-09

The pilot requires its own `docs/research/BUDGET_TRANSFER_APPROVAL.json`, bound to the frozen plan hash, unchanged baseline hash, exact reviewed source commit and fixed run ID. Earlier bootstrap and convergence approvals cannot open this gate. Altered plan payloads, changed source, dirty checkouts, wrong environments and overwriting an existing run are rejected.

A complete pilot summary contains 12 world/model assessment records and seven paired single-replicate contrasts, with n=1 explicit and no SD, leave-one-out SD, inferential interval or decision. An incomplete or duplicated set of records, or a nonfinite loss, is rejected. Failure preservation includes completed data, traceback and manifest without a complete summary.

The manifest records lifetime peak resident memory of the running process, including imports and all fits. It retains the raw `RUSAGE_SELF.ru_maxrss` value, platform unit and normalized bytes. This is not incremental allocation, per-model memory or an operating-system memory limit. The current [Apple kernel manual](https://github.com/apple/darwin-xnu/blob/main/bsd/man/man2/getrusage.2) specifies bytes; the [Linux manual](https://www.man7.org/linux/man-pages/man2/getrusage.2.html) specifies KiB. Unknown unit conventions are rejected rather than guessed.

`scripts/check-convergence.py` now audits this pilot mode alongside the immutable earlier stages: source/approval/plan binding, file hashes and sets, observed-data replay, reference and saved learned-checkpoint predictions, trace flags/stop reasons, no-variance summaries and recorded memory-unit conversion. It performs no optimization. Memory conversion can be checked, but a past peak-memory measurement cannot be recreated by prediction replay.

Fifty-seven software tests pass, including the single-replicate/no-variance contract, incompatible-mode rejection, authorization separation, memory-unit normalization and synthetic partial-failure preservation. Existing stage-001/002 outputs still replay. At the preparation review, the numerical plan was unchanged and unfrozen/unauthorized; no feasibility-pilot observations or fits had been generated.

Concrete one-run scope for later approval: three independent units, six learned fits, 4096/1024/2048 episodes per unit, cap 300 epochs and patience 20, two CPU threads and a cooperative 3600-second allowance. No retries, discretionary extension, confirmation, Claim promotion or Cycle resolution.

## Completed disposition — 2026-10-09

The separately bound one-run approval was recorded and the frozen pilot completed in 348.175 seconds. All six fits stopped by patience with no predeclared warning. Fifty outputs and saved predictions replay. See `BUDGET_TRANSFER_REPORT.md` for runtime, lifetime peak memory and single-replicate diagnostics. No further execution, inferential conclusion, Claim or Cycle resolution is authorized. All predeclared rules above remain unchanged.
