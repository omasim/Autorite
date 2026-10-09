# RP002A target-data-size feasibility pilot proposal

Date: 2026-10-09. Version/seed namespace: `budget-transfer-proposal-0.1`. **Unfrozen, unauthorized and unexecuted.** Numerical specification: `BUDGET_TRANSFER_PLAN.json`. Proposed run ID: `budget-transfer-20261009-001`.

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

`python3 scripts/check-budget-transfer-plan.py` checks the proposal and seeds without creating observations or training. The existing convergence runner does not authorize this different mode or a single-replicate summary. Implement and review a separate one-run gate and auditor, including the no-SD output contract and memory-unit recording, before requesting approval to freeze and execute. Neither bootstrap nor stage-001/002 approval can authorize this pilot.

Bind any later approval to the exact frozen plan and unchanged baseline hashes, reviewed source commit, fixed run ID and pinned environment. Execute only from clean reviewed source. Preserve completed/partial files, traceback and manifest on failure or timeout; an incomplete stage has no complete-stage aggregate. Never replace seeds, retry, add fits or extend epochs/time without a separately reviewed future scope. Existing run directories remain immutable.

The broader confirmation design still needs an optimization rationale, variance assumptions, substantive margins, sample counts, calibrated uncertainty and a complete analysis implementation. Cycle 01 remains PLANNED at 0/13; no scientific status changes with this proposal.
