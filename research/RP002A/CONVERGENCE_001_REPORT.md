# RP002A exploratory convergence-stage review

Date: 2026-10-09. Run: `convergence-20261008-001` (the predeclared run ID retains its original proposal date). Completed once; no retries, extensions or confirmatory evidence.

## Approval and provenance

The user approved this separately proposed stage by replying “devam” to the explicit 20-unit, 40-fit, 15-minute freeze/execution request. `CONVERGENCE_PLAN.json` was frozen and passed CI before `docs/research/CONVERGENCE_APPROVAL.json` anchored the exact plan and source. The execution source was `6fa2c6a009eb704192fa6a49218c4f54f3629aed`; plan SHA-256 was `1dfdabfbf39d2890bd7853b2018b1e8e9765460d13052606a8d4ea2cda18bdc4`.

Python 3.9.6, NumPy 2.0.2 and PyTorch 2.8.0 on macOS arm64 CPU, two threads. Elapsed stage wall time: 82.630 seconds, within the declared 900-second deadline. All 20 world/replicate units, 40 learned-model fits and 80 model assessment records completed. E1 had 10 independent replicates; E0/E2 had five each. Each used fresh 256/128/128 training/validation/assessment episodes of 129 observations. Assessment data were excluded from checkpoint selection.

[Raw immutable artifacts](https://github.com/omasim/Autorite/tree/main/research/RP002A/runs/convergence-20261008-001) preserve datasets, seeds, checkpoints, traces, probabilities, losses, per-replicate records, summaries and environment. The manifest lists 322 hashed outputs; it is an additional file. No realized latent-state array was supplied to a predictor.

## Artifact review

The audit checks all output hashes and file coverage, the approval/source/plan binding, observed-data replay from the seed schedule, B0/B3 reference replay, saved B1/B2 checkpoint predictions, categorical losses and paired replicate summaries. Checks passed. Replaying checkpoints evaluates saved models without further training; tolerance is explicit and does not claim bit-identical optimization across platforms. CI also checks that committed run bytes and file sets remain unchanged.

## Descriptive assessment contrasts

Difference is alternative minus reference natural-log loss; negative values favor the alternative on these exploratory assessment samples. Each observation in the summary is one independent training-replicate mean. Timepoints and episodes are not extra training replicates. SD is a descriptive sample SD, not a confidence interval or power guarantee.

| Contrast | Replicates | Mean difference (nats) | Sample SD | Leave-one-out SD range |
|---|---:|---:|---:|---:|
| E1:B1-B0 | 10 | -0.026256 | 0.001303 | 0.001017–0.001374 |
| E1:B2-B0 | 10 | -0.028592 | 0.003443 | 0.002728–0.003650 |
| E0:B1-B0 | 5 | +0.008435 | 0.002125 | 0.000902–0.002441 |
| E0:B2-B0 | 5 | +0.020301 | 0.003707 | 0.001096–0.004250 |
| E2:B1-B0 | 5 | +0.000841 | 0.000359 | 0.000239–0.000415 |
| E2:B2-B0 | 5 | +0.000143 | 0.000173 | 0.000057–0.000200 |
| E1:B2-B1 | 10 | -0.002336 | 0.002340 | 0.001984–0.002482 |

E1 B1/B2 assessment losses were lower than B0 in this stage. The B2-minus-B1 mean is much smaller than the previously proposed 0.01-nat effect threshold. E0 learned models remained above the current-observation table; E2 differences were small. These observations are limited to the declared generators, data sizes, implementations and training budgets. They are not confirmatory benefit/equivalence decisions, novelty evidence or proof that recurrence is necessary. No inferential intervals or p-values were generated.

## Convergence diagnostics

A best-near-cap flag means all 50 epochs completed and the selected best epoch was in the final ten. A late-improvement flag means validation loss fell by more than 0.001 nats over the final five recorded epochs. These were declared before outcomes; they are descriptive warnings, not convergence tests.

| World | Learned fits | Reached 50 epochs | Best near cap | Late improvement |
|---|---:|---:|---:|---:|
| E0 | 10 | 10 | 10 | 10 |
| E1 | 20 | 20 | 20 | 16 |
| E2 | 10 | 3 | 3 | 0 |

Overall, 33/40 fits reached the cap and selected their best checkpoint near it; 26/40 continued improving late. The stage therefore does **not** establish settled optimization. The CPU time allowance was not exhausted; the separate fixed epoch cap was binding for many fits. It was not extended after observing these outcomes.

## Disposition and next design work

The approved exploratory stage is complete. The unchanged baseline and numerical confirmatory proposal remain distinct; no scientific Claim was promoted and no Cycle obligation was resolved (0/13).

The measured SDs describe this budget and data size only. Do not automatically transfer them to the proposed 4096-training-episode confirmation setting or select a confirmatory replicate count from them. Small samples and changes in optimization/data can change variability.

Before confirmation, propose a separately frozen convergence plan addressing the binding epoch cap, with fresh seeds and validation-based choices, rather than revisiting these assessment samples. Keep the information-matched references and the weak ideal window-eight/full-history gap visible. Then justify the final optimization budget, variance assumptions, effect/equivalence margin, uncertainty calibration, sample counts and complete analysis implementation. This report authorizes no additional run or discretionary tuning.
