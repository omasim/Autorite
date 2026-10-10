# RP002A second fixed-budget confirmatory benchmark

Report date: 2026-10-10 (Europe/Istanbul). Predeclared run ID: `confirmatory-20261010-002`. One completed frozen attempt; conditional normal-theory inference for three finite synthetic generators.

## Disposition

All **60 independent units and 120 learned-model fits** completed in 12297.895 seconds (205.0 minutes), within the declared four-hour allowance. Each world has 20 independent training/validation/assessment and initialization/order draws. The seven predeclared decisions are: 2 benefit, 4 equivalence and 1 indeterminate. No replicate, model or contrast is discarded.

These decisions apply to the specified fixed-budget algorithms and generator settings, conditional on the stated independence/normal-theory assumptions. Synthetic calibration stress tests do not establish actual-loss or distribution-free coverage. The .01-nat thresholds are fixture-specific engineering tolerances. This experiment does not establish optimal training, necessity of recurrent memory, universal memory or a foundational theory. No broad scientific Claim or Cycle closure is inferred from a completed benchmark.

## Disclosed retry and elapsed clocks

The first attempt is INCOMPLETE and remains preserved in its separate report. This fresh attempt was explicitly authorized on 2026-10-10. Its complete data and seed namespace are independent; first-attempt partial outcomes were accessible but did not select or change the design. No stages or attempts are pooled. The dual-clock guard and temporary idle-sleep assertion were declared before this attempt. The host log records Clamshell Sleep at 12:57:07 +0300 and a return to FullWake at 14:36:43 +0300; idle-sleep prevention cannot prevent lid-triggered sleep. Civil elapsed time includes this interruption. See `research/RP002A/confirmation-002/EXECUTION_REVIEW.json` for the retained timing/host review.

## Primary family

Alternative-minus-reference episode-mean natural-log loss; lower is better. Equal training-replicate weight; episodes/timepoints are not additional training replicates. Each row uses n=20 and the frozen twofold-inflated Student-t Bonferroni interval for seven comparisons at familywise alpha .05. Benefit requires the entire interval strictly below -.01. Equivalence requires the entire interval strictly inside [-.01,+.01]. All other cases are indeterminate.

| Contrast | Mean difference | Sample SD | Adjusted interval lower | Adjusted interval upper | Primary kind | Decision |
|---|---:|---:|---:|---:|---|---|
| E1:B1-B0 | -0.039216147 | 0.000399970 | -0.039755200 | -0.038677094 | benefit | benefit |
| E1:B2-B0 | -0.039926938 | 0.000403366 | -0.040470568 | -0.039383309 | benefit | benefit |
| E0:B1-B0 | 0.000045841 | 0.000031122 | 0.000003896 | 0.000087786 | equivalence | equivalent |
| E0:B2-B0 | 0.000021099 | 0.000022656 | -0.000009435 | 0.000051633 | equivalence | equivalent |
| E2:B1-B0 | 0.000113419 | 0.000030304 | 0.000072577 | 0.000154261 | equivalence | equivalent |
| E2:B2-B0 | 0.000028149 | 0.000021223 | -0.000000454 | 0.000056752 | equivalence | equivalent |
| E1:B2-B1 | -0.000710791 | 0.000105713 | -0.000853265 | -0.000568318 | benefit | indeterminate |

E1:B2−B1 is an implementation-benefit comparison under the .01 margin, never a recurrence-necessity test. If its benefit criterion is not met, that is its declared indeterminate outcome; no post-outcome switch to an equivalence claim is made. The prior ideal window-eight/full-history gap (~.000012 nats) remains far below this engineering margin. E0/E2 equivalence decisions concern predictive log loss for the fixed algorithms, not equality of representations or absence of all historical effects.

## Assessment losses and secondary diagnostics

The following losses are descriptive averages over equally weighted replicate means. B3 knows the generator law and conditions only on observed history, without privileged realized hidden states.

| World | B0 | B1 | B2 | B3 | Training replicates |
|---|---:|---:|---:|---:|---:|
| E0 | 0.325257305 | 0.325303147 | 0.325278405 | 0.325251027 | 20 |
| E1 | 0.947784092 | 0.908567945 | 0.907857153 | 0.907782559 | 20 |
| E2 | 1.039787912 | 1.039901330 | 1.039816061 | 1.039783702 | 20 |

Secondary metrics are descriptive, with no further inferential decisions. The table averages the per-replicate values equally. Conditioning refers to the **current observation** being erasure or visible; an empty stratum remains null. Multiclass Brier is the sum of squared probability errors, averaged over timepoints. Ten fixed top-label confidence bins retain counts, mean confidence and accuracy in each raw unit file; their timepoints do not create extra training replicates.

| World | Model | Brier | Erasure-current log loss | Visible-current log loss | Mean gap to B3 | Clipped-target fraction |
|---|---|---:|---:|---:|---:|---:|
| E0 | B0 | 0.180123261 | null | 0.325257305 | 0.000006278 | 0.000000000 |
| E0 | B1 | 0.180136778 | null | 0.325303147 | 0.000052119 | 0.000000000 |
| E0 | B2 | 0.180130335 | null | 0.325278405 | 0.000027377 | 0.000000000 |
| E0 | B3 | 0.180122375 | null | 0.325251027 | 0.000000000 | 0.000000000 |
| E1 | B0 | 0.585062895 | 1.039916312 | 0.855719016 | 0.040001532 | 0.000000000 |
| E1 | B1 | 0.566807435 | 0.960949691 | 0.856224665 | 0.000785385 | 0.000000000 |
| E1 | B2 | 0.566409392 | 0.959968428 | 0.855784116 | 0.000074594 | 0.000000000 |
| E1 | B3 | 0.566366024 | 0.959893425 | 0.855709966 | 0.000000000 | 0.000000000 |
| E2 | B0 | 0.625048007 | 1.039918139 | 1.039656855 | 0.000004210 | 0.000000000 |
| E2 | B1 | 0.625122548 | 1.040021082 | 1.039780752 | 0.000117629 | 0.000000000 |
| E2 | B2 | 0.625066478 | 1.039941778 | 1.039689520 | 0.000032359 | 0.000000000 |
| E2 | B3 | 0.625045395 | 1.039917763 | 1.039648805 | 0.000000000 | 0.000000000 |

Raw secondary files also retain unclipped log loss when every selected target probability is positive; otherwise null. No worlds, seeds or stages are pooled for primary inference. Old pilot/convergence/variance assessment outcomes are not included in these confirmatory means.

## Training and resource diagnostics

There are **0** unit/model records with a predeclared near-cap or late-improvement warning. Every trace is retained. Warnings limit settled-optimization assertions but do not change the definition of the predeclared fixed-budget algorithm or remove a replicate. Earlier exploratory warnings remain part of their original runs.

| World | Model | Mean epochs | Maximum epochs | Epoch-cap fits | Warning fits |
|---|---|---:|---:|---:|---:|
| E0 | B1 | 85.5 | 105 | 0 | 0 |
| E0 | B2 | 113.8 | 135 | 0 | 0 |
| E1 | B1 | 96.6 | 169 | 0 | 0 |
| E1 | B2 | 71.4 | 106 | 0 | 0 |
| E2 | B1 | 34.2 | 44 | 0 | 0 |
| E2 | B2 | 58.4 | 154 | 0 | 0 |

Started UTC: 2026-10-10T09:50:58.876384+00:00. Finished UTC: 2026-10-10T13:15:56.770902+00:00. Civil elapsed: 12297.895 seconds; monotonic elapsed: 6426.015 seconds. Both stayed below the 14400-second allowance.

Lifetime peak resident memory was 290865152 bytes (277.39 MiB), raw macOS `RUSAGE_SELF.ru_maxrss` in bytes. This includes imports and all fits of this process, not incremental allocation, per-model memory or system-wide use. The auditor checks recorded unit conversion; it cannot recreate the past peak. Local timings are not a guarantee for other machines.

## Frozen design and provenance

Models and generator laws are unchanged from the preserved operational proposal. Every unit used 4096 training, 1024 validation and 2048 independent assessment episodes, 129 observations/128 prediction pairs. B1 has window eight/579 parameters; B2 has GRU state 12/651 parameters. Capacity is approximately matched, not identical. Training used Adam .001, batch 32, clip 1, cap 300 epochs, patience 20 and minimum-validation checkpoint. Assessment never selected a checkpoint or tuned a budget/margin.

Synthetic calibration qualified counts 20,30,50 before target-size variance training. Five fresh variance replicates per world supplied only SDs to the fixed upper-SD planning rule; it selected 20. This selection is not a power claim or actual-loss normality proof. The historical `CONFIG_PROPOSAL.json` remains unchanged; the new frozen supplement is `CONFIRMATORY_002_CONFIG.json`.

- Execution source: `a8739ca4521c1bc90aad221938f7c2575721a3bf`.
- Frozen configuration SHA256: `4b3fa9f9e77983057c71fdd83ff08cc0218bac7c63fd993370ea7fb56a8f0942`.
- Source-bound approval SHA256: `03dae188e5559586c3735bd539b00d3b31ba2363102a10032b695cf9d81f73b1`.
- Manifest SHA256: `2d6ed61b5f5c50627879530f22758bdf1f75bd2ad86fcbd58ad77e1396e63939`.
- Environment: Python 3.9.6, NumPy 2.0.2, PyTorch 2.8.0, SciPy 1.13.1, macOS arm64 CPU, two threads.
- Fresh namespace `confirmation-2.0`; no prior samples/weights reused, one separately authorized technical retry after the preserved incomplete first attempt; no further retry, extension, optional stopping or post-outcome method choice.
- 484 hashed outputs plus manifest: complete lossless data, selected weights, validation traces, original-precision probabilities/losses, per-unit secondary diagnostics and analysis.

The auditor regenerates data/seeds, checks B0/B3 references, replays saved learned-checkpoint predictions, losses, secondary metrics, trace summaries and all seven intervals/decisions without optimization. Immutable files are checked against their first committed bytes. The pre-outcome Test is `TST-RP002A002`; the verified Result record preserves the scope and assumption limits, without automatically promoting a broad Claim.

[All raw run artifacts](https://github.com/omasim/Autorite/tree/main/research/RP002A/runs/confirmatory-20261010-002) · [Frozen protocol](https://github.com/omasim/Autorite/blob/main/research/RP002A/CONFIRMATORY_002_PROTOCOL.md) · [Calibration review](https://github.com/omasim/Autorite/blob/main/research/RP002A/CALIBRATION_REPORT.md) · [Variance review](https://github.com/omasim/Autorite/blob/main/research/RP002A/TARGET_VARIANCE_REPORT.md)

## Remaining work

Independent evidence review, interpretation relative to the broader research questions and the remaining Cycle packages are open. There is no automatic resolution of the 13 Cycle obligations or permission for another model run. The benchmark describes these three generator settings and algorithms under the specified inference assumptions; it supplies no universal theory or recurrence-necessity conclusion.
