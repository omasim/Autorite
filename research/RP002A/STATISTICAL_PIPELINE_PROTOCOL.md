# RP002A statistical pipeline protocol

Date: 2026-10-09. Version: `statistical-pipeline-1.0`. Numerical specification: `STATISTICAL_PIPELINE_PLAN.json`. Frozen before new outputs. The user's explicit instruction to perform steps 1, 2, 3 and 4 authorizes the bounded stages below; each execution still receives its own exact source/plan/baseline approval record. This supersedes prior *authorization limits for future work*, never historical outcomes or baseline definitions.

## Scope and stages

1. `calibration-20261009-001`: synthetic analysis stress tests, at most 900 seconds; no learned models or RP002A generator observations.
2. `target-variance-20261009-001`: five fresh independent replicates in each E0/E1/E2, 15 units and 30 learned fits, at most 5400 seconds. This stage measures target-size variability; its means cannot tune models, effects or margins.
3. Derive a separate frozen `CONFIRMATORY_CONFIG.json` by the rule below, bind the calibration/variance outputs and approval to exact source, and preserve the historical `CONFIG_PROPOSAL.json` unchanged.
4. `confirmatory-20261009-001`: one fresh independent confirmatory execution, n=20, 30 or 50 per world, at most 14400 seconds on two CPU threads. No retry, extension, seed replacement, optional stopping or post-outcome model selection.

If a prerequisite stage fails or has no eligible candidate, preserve its partial outputs and stop dependent work. An incomplete confirmation has no complete-stage aggregate or hypothesis decisions. User authorization does not waive an unmet scientific gate.

## Synthetic analysis calibration

Use independent simulation trials; 20,000 trials per cell. Grid: n=5,10,20,30,50; centered unit-variance normal, Gamma(shape=2) and Student-t(df=5) effects; inter-contrast shared-component variance fractions rho=0,.5; proportions 0,.5,1 of replicate-mean variance due to independent conditional episode averaging. Seven contrasts are evaluated together. Synthetic distributions represent assumptions, not estimates of actual loss distributions. Randomness uses a fresh SHA256 `calibration-1.0` namespace; seeds and trial diagnostics are retained.

The preselected primary candidate is a **twofold-inflated paired replicate-mean Student-t interval**, with seven two-sided Bonferroni intervals at familywise alpha=.05. Inflation is fixed before simulation to stress a conservative normal-theory procedure; it is not a fitted correction or distribution-free guarantee. Also report uninflated Student-t coverage. The [Student-t distribution and inverse CDF](https://docs.scipy.org/doc/scipy-1.13.1/reference/generated/scipy.stats.t.html) are computed with pinned SciPy 1.13.1. The ordinary mean-interval basis is documented by [NIST](https://itl.nist.gov/div898/handbook/eda/section3/eda352.htm).

For each cell retain simultaneous coverage failures, false benefit at the -0.01 boundary, false equivalence at either +/-0.01 boundary, zero-effect equivalence rate and widths. Decision illustration uses SD=.01 and margin=.01; scale/translation of standardized trials yields those boundaries. Report Monte Carlo error. A count is eligible only if n>=20 and every predeclared cell at that n has a Clopper-Pearson upper coverage-failure bound <=.05. Bounds use .05/90 for simultaneous Monte Carlo statements across all 90 cells. This validates performance only in the declared synthetic fixtures; actual-loss coverage remains conditional on distributional assumptions.

Benchmark current nested and whole-cluster percentile methods separately: 100 trials, 2,000 bootstrap draws, eight synthetic episodes, n=5,20,50, the three laws and within-mean fractions 0,1, no shared inter-contrast component. The exact existing nested resampling kernel is used, including independent inner draws for each selected occurrence. This eight-episode fixture makes a bounded computational comparison; it does not pretend to be the 2048-episode workload. Low trial/draw counts have substantial Monte Carlo uncertainty and cannot choose the confirmatory method. Retain all 18 benchmark cells, including unfavorable cases.

## Fresh target-size variance stage

Keep the existing generator laws, B0–B3 information access, model sizes, Adam .001, batch 32, clip 1 and probability clip 1e-8. Data counts per unit: 4096 training, 1024 validation, 2048 assessment, 129 observations. Cap 300 epochs, patience 20, minimum-validation checkpoint; assessment only after selection. Seeds come from `target-variance-1.0`; never reuse previous datasets or weights.

Retain exact compressed datasets (lossless uint8 representation of categorical values), probabilities with original floating precision, losses, weights, traces, secondary diagnostics, wall times and process peak memory. Compression changes storage, not scientific values. The auditor regenerates data and replays saved predictions/analysis without optimization. Existing runs remain immutable.

The stopping budget defines the algorithm being measured. Near-cap/final-20/final-five flags are retained with prior definitions. Such flags preclude an optimality or settled-optimization assertion; they do not change the estimand for this fixed-budget algorithm. This clarification is pre-outcome for the new pipeline and does not reclassify prior exploratory warnings.

## Fixed sample-count and resource rule

From the seven fresh variance-stage contrast SDs, calculate a simultaneous 95% normal-theory upper SD bound using df=4 and chi-square lower quantile .05/7. Use the largest upper bound for every world. Among eligible counts 20,30,50 select the smallest whose twofold-inflated Bonferroni t planning half-width is <=.005 nats. If none meets precision, choose the largest eligible count and explicitly report resource-limited precision. If none is eligible, do not execute confirmation. Means and favorable effect sizes are not inputs to this rule.

This upper-SD calculation assumes independent normal replicate differences. Five exploratory replicates yield a deliberately conservative, unstable bound; it is a planning assumption, not a validated variance guarantee or 80% power claim. Every candidate count remains within the same four-hour attempt allowance; runtime is not guaranteed. Do not use additional training to rescue a failed precision, calibration or wall-time gate.

## Confirmatory estimand and decisions

For each world/contrast the target is expected paired episode-mean clipped natural-log-loss difference of the completely specified training/checkpoint procedure, averaged over independent training, validation, initialization/order and assessment draws. Timepoints reduce to episode means, then equally weighted training replicate means. Paired assessment episodes are shared by all models within a replicate. E0, E1 and E2 are never pooled.

Primary family and ordered decision kinds are fixed:

| Contrast | Kind |
|---|---|
| E1:B1-B0 | Benefit |
| E1:B2-B0 | Benefit |
| E0:B1-B0 | Equivalence |
| E0:B2-B0 | Equivalence |
| E2:B1-B0 | Equivalence |
| E2:B2-B0 | Equivalence |
| E1:B2-B1 | Benefit; implementation comparison only |

Benefit requires the entire adjusted interval strictly below -.01. Equivalence requires the entire interval strictly inside [-.01,+.01]. All other cases are indeterminate; nonsignificance is not equivalence. The .01-nat threshold is a **fixture-specific engineering tolerance**: approximately one quarter of the E1 ideal current-to-history opportunity (.03981 nats), while distinguishing numerical/implementation deviations in the null controls. It is not a universal substantive threshold. The ideal window-eight gap (~.000012 nats) remains far below this margin; B2–B1 never tests recurrence necessity. Report this limited rationale rather than asserting external relevance.

The interval uses n-1 df and s/sqrt(n), with a fixed factor two on the Bonferroni t critical value. Assumptions and synthetic gate limitations must accompany every outcome. No actual-loss normality test is used to switch methods after outcomes. Zero observed SD is treated as an analysis failure, not perfect precision.

## Complete secondary diagnostics

Per world/replicate/model retain multiclass Brier score (sum of squared probability errors), natural-log loss conditioned on **current observation** being erasure or visible, fraction of target probabilities clipped below 1e-8, unclipped log loss if all selected target probabilities are positive (otherwise null), gap to information-matched B3, and ten fixed top-label confidence bins [b/10,(b+1)/10), with the final bin including one. Store counts, mean confidence and accuracy; empty strata/bins remain null. These are descriptive secondary outputs with no additional confirmatory decisions. Equal-replicate aggregation and any pooled display must be distinguished.

## Provenance, failure and scientific status

Pinned local environment: Python 3.9.6, NumPy 2.0.2, PyTorch 2.8.0, SciPy 1.13.1, macOS arm64 CPU, two threads. CI checks software on Linux; it never runs research stages. Each one-run approval binds frozen plan SHA256, unchanged baseline hash, source ancestor, exact stage/run ID and clean source. Only the matching approval record may differ from the approved source anchor. Dependencies of the final configuration are separately hashed.

Stage manifests retain source/plan/approval/environment/seed provenance, hashed output sets, elapsed time and platform-aware lifetime process peak resident memory. Failure retains partial outputs and traceback without a full-stage summary. No additional run is implied by any software check. Scientific Claim promotion or Cycle closure requires separate evidence/graph review; a completed execution alone cannot resolve all 13 Cycle obligations.
