# RP002A longer-budget convergence proposal

Date: 2026-10-09. Version/seed namespace: `convergence-long-budget-proposal-0.1`. **Approved, frozen and completed once.** The declarations below retain the pre-outcome proposal. See `CONVERGENCE_002_REPORT.md` for the 2026-10-09 disposition. Numerical specification: `CONVERGENCE_002_PLAN.json`.

## Reason for a separate stage

The audited first convergence stage completed 40 learned-model fits in 82.630 seconds. Thirty-three reached 50 epochs and selected their best checkpoint in the final ten; 26 improved by more than 0.001 nats in their final five recorded epochs. This motivates reviewing a longer optimization budget. These observations do not establish underfitting, eventual convergence or a required final epoch count.

Retain the existing E0/E1/E2 generator laws, B0/B1/B2/B3 definitions, architectures, Adam learning rate, batching, clipping, loss and information access. Keep 256 training, 128 validation and 128 assessment episodes of 129 observations per independent unit. Only the optimization budget and declared diagnostic windows change, alongside a fresh run identity and seed namespace. No archived dataset, initialization or checkpoint is reused. The previous outputs and frozen plan remain immutable.

## Fixed proposed scope

| Item | Completed stage 001 | Proposed stage 002 |
|---|---:|---:|
| Independent units | E0: 5 / E1: 10 / E2: 5 | Same counts, fresh samples |
| Learned-model fits | 40 | 40 |
| Maximum epochs per fit | 50 | 300 |
| Consecutive epochs without validation improvement | 5 | 20 |
| Best-checkpoint cap window | Final 10 epochs | Final 30 epochs |
| Late-validation diagnostic window | Final 5 epochs | Final 20 epochs |
| Late-improvement threshold | 0.001 nats | 0.001 nats |
| Cooperative stage deadline | 900 seconds | 1800 seconds |

Proposed run ID: `convergence-20261009-002`. Execution order remains replicate index ascending, world lexicographic, B1 then B2. Environment remains Python 3.9.6, NumPy 2.0.2, PyTorch 2.8.0, macOS arm64 CPU, two threads. At most 12,000 learned-model epochs are allowed (40 × 300); early stopping can shorten this.

The 300-epoch ceiling is a bounded sixfold budget probe, not an empirically established convergence requirement. Scaling the prior total wall time by six gives roughly 496 seconds; this is a rough planning calculation, not a benchmark, guarantee or hard upper bound. The fixed 1800-second allowance permits overhead variation. Check the deadline before phases and batches and after validation; an in-progress operation may finish after the boundary. Never extend the cap or deadline after seeing outcomes.

## Selection, assessment and descriptive diagnostics

Optimize on training data only. Select the minimum validation-loss checkpoint; stop after 20 consecutive epochs without strict validation improvement. Validation is repeatedly used for selection and cannot serve as independent scientific evidence. Assessment episodes remain unseen until checkpoint selection; they cannot trigger changes to epochs, patience, learning rate, architecture, seeds or sample count.

Report every trace, checkpoint, best epoch, final validation loss, elapsed time and stop reason. A near-cap flag means a fit completed all 300 epochs and selected its best checkpoint in epochs 271–300. A late-improvement flag means the final 20 recorded validation losses declined from first to last by more than 0.001 nats; traces shorter than 20 epochs have insufficient length for that flag. Neither absent flags nor early stopping prove convergence.

For continuity, additionally show the last-five-epoch change using the old 0.001-nat threshold, explicitly labelled as a secondary descriptive diagnostic. Primary windows differ between stages; their flag rates are not directly comparable. Inspect validation traces by world/model, rather than pooling away unstable fits. Declare optimization still unresolved if any fit is flagged or incomplete; if none is flagged, report only that no predeclared budget-sensitivity warning was detected. Do not label that a convergence proof.

Assessment summaries use one independently trained replicate mean per unit: model losses, paired within-replicate contrasts, sample SD and leave-one-out SD range. Reuse the seven contrast labels and no inferential decisions. Differences between stages are unpaired descriptive observations with fresh data and seeds; never combine their samples or select a favorable stage. No p-values, equivalence calls, power guarantees, confirmatory sample-count decisions, Claims or Cycle resolutions.

## Randomness and audit

Derive the 140 seeds from the new opaque namespace with the existing SHA-256 function. Verify distinctness within this stage and disjointness from executed pilot/stage seeds and the declared confirmatory schedule before any execution. Hash separation is not a proof of probabilistic independence.

`python3 scripts/check-convergence-proposal.py` validates the configuration hash, bounded change set and seed separation without training, generating observations or creating a run directory. CI runs the same check. The stage-specific entry point is now prepared: `python3 scripts/rp002a-convergence.py --stage 2` prints the plan without creating data. Adding `--execute --run-id convergence-20261009-002` refuses before creating artifacts while the plan remains unfrozen/unauthorized. The default entry point still addresses stage 001.

The stage-002 entry point, stage-specific artifact auditor and secondary five-epoch diagnostic are implemented and pass software checks. Bind approval to the frozen plan hash, unchanged baseline hash, fixed run ID and exact reviewed source commit. Stage-001 and bootstrap approvals cannot authorize this stage. Review the implementation and immutable preservation checks before requesting that one-run approval.

## Failure and later decisions

One attempt only after separate approval. Preserve partial datasets, traces/checkpoints when available, failure traceback and manifest; no retries, replacement seeds, extra fits or automatic extension. An incomplete stage has no complete across-replicate aggregate.

Review actual runtime, validation warnings and replicate variability before any further proposal. If the new budget is still binding, record that result and prepare a separately reviewed deviation rather than extending this run. Even an unflagged result leaves the 4096-training-episode confirmatory setting unvalidated: this stage holds the smaller data size fixed to isolate the budget question. Confirmatory optimization, variance assumptions, margins, sample counts and analysis remain separate design obligations. Cycle 01 stays PLANNED at 0/13.

## Execution preparation review — 2026-10-09

The two stages resolve distinct plan and approval paths. Stage 002 requires `docs/research/CONVERGENCE_002_APPROVAL.json`; the earlier record does not open this gate. Approval binds the exact on-disk plan, baseline and reviewed source; a substituted payload, dirty checkout, changed source or wrong environment is rejected. The fixed run directory cannot be overwritten.

The auditor replays seeds, observed data, B0/B3 and saved learned checkpoints without training. It checks primary and secondary trace diagnostics, stop reasons, replicate-level summaries and immutable Git bytes. Stage-001 output format is preserved and its 322 recorded outputs still replay successfully. Fifty software tests pass; authorization tests use synthetic fixtures and create no research outcomes.

The numerical proposal is unchanged: 20 units, 40 learned fits, at most 300 epochs each, patience 20 and a cooperative 1800-second stage allowance. The proposed CPU environment has not changed. The plan and baseline hashes must be captured when the separately approved one-run scope is frozen. At this preparation review, no stage-002 approval record or run existed.

## Recorded disposition — 2026-10-09

The separately approved run completed once in 383.749 seconds. `docs/research/CONVERGENCE_002_APPROVAL.json` records approval; `CONVERGENCE_002_REPORT.md` reports audited outcomes. Twelve fits retain near-cap warnings, so optimization remains unresolved. No further run is authorized.
