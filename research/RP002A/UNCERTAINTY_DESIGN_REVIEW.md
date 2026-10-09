# RP002A uncertainty and replicate-count design review

Date: 2026-10-09. **Deterministic planning review only.** No new generator observations, model training, Monte Carlo simulations, resampling of archived assessment data or scientific decisions. Existing configuration and all run bytes remain unchanged.

## Disposition

Do not freeze five training replicates or the current 2,000-draw hierarchical percentile interval. The target-size feasibility pilot establishes local execution feasibility for one replicate per world, not variability or coverage. This review makes the uncertainty target explicit and identifies two analysis gates. It does not select a final sample count or interval method.

For each contrast, write D_ri for alternative-minus-reference episode-mean loss in episode i of independent training replicate r. All models in a replicate share assessment episodes. Let A_r be the mean of its m episode differences. The estimator is the equally weighted mean of n independent A_r values. Its target averages over training, checkpoint-selection and finite independent assessment randomness; timepoints and assessment episodes are not extra training replicates. Keep each world's contrast separate.

## Exact conditional resampling audit

The existing `paired_interval` independently resamples n replicate indices and m episodes inside every selected occurrence. For a fixed rectangular matrix D, define v_A as the population-denominator variance of the observed A_r values, and v_r as the population-denominator episode variance within row r. Conditional on that matrix:

- Whole-replicate resampling variance of the grand mean is v_A/n.
- Current nested resampling variance is v_A/n + mean(v_r)/(n m).

This is our law-of-total-variance derivation for the implemented resampling kernel, not a coverage theorem. Independent exhaustive enumeration of all choices for a two-by-two matrix verifies the formula in software tests. The current implementation is preserved; historical exploratory records are not reanalysed or replaced.

To interpret the additional term, consider only an illustrative iid random-effects model D_ri = mu + U_r + epsilon_ri, with variances tau² and sigma². Actual model losses need not obey this model. The true sampling variance of the grand mean is (tau² + sigma²/m)/n. The expected nested variance divided by that true variance is:

`(n−1)/n + [(m−1)/m] × [ (sigma²/m)/(tau² + sigma²/m) ]`.

Whole-cluster bootstrap alone has the first factor (n−1)/n, so it can underestimate variance at small n. If within-episode sampling supplies essentially all replicate-mean variability, the nested ratio at n=5, m=2048 is about 1.7995, tending towards two for larger n. If training variability dominates, the added term is small. Neither direction alone establishes actual interval coverage, and overdispersion does not automatically make percentile decisions safe. This is a reason to calibrate, not to declare a universal replacement.

A candidate analysis is a paired replicate-mean Student-t interval using s_A/sqrt(n), with n−1 degrees of freedom and the same seven-contrast multiplicity correction. This includes held-out randomness already present in A_r, without adding another within-row bootstrap. The standard mean interval is documented by [NIST](https://itl.nist.gov/div898/handbook/eda/section3/eda352.htm). Exact finite-sample validity requires independent normally distributed replicate means; small-n learned-model differences need not satisfy this. Whole-cluster percentile and current nested percentile intervals remain comparison candidates. No candidate is selected by this review.

## Bootstrap tail resolution

Seven two-sided Bonferroni intervals with familywise alpha 0.05 put each endpoint at tail probability 0.05/(2×7) = 1/280. The table concerns Monte Carlo resolution of the resampling distribution, not research sample size or coverage.

| Bootstrap draws | Expected draws per tail | Tail-count SD | Relative tail-count SD |
|---:|---:|---:|---:|
| 2000 | 7.14 | 2.67 | 37.3% |
| 10000 | 35.71 | 5.97 | 16.7% |
| 50000 | 178.57 | 13.34 | 7.5% |

Counts follow the binomial illustration for independent draws from a continuous distribution at its true quantile. Ties and the density near an endpoint affect quantile uncertainty. Raising draws improves endpoint resolution but cannot repair insufficient training replicates or statistical miscalibration. The proposed 2,000 draws remain historical configuration; no silent change to 50,000 is made.

## Replicate-count sensitivity

The table below inverts the known-SD normal planning width `z × SD/sqrt(n)` with z≈2.690. Every SD is an assumption about independently observed replicate means at the target data sizes, not an estimate imported from prior smaller-data runs or the n=1 pilot. Values use ceil and a minimum of two; low counts are mathematical illustrations, not recommendations. Student-t uncertainty with estimated SD generally requires wider intervals. Precision is not decision power.

| Assumed SD | Half-width 0.005 | Half-width 0.010 |
|---:|---:|---:|
| 0.001 | 2 | 2 |
| 0.003 | 3 | 2 |
| 0.010 | 29 | 8 |
| 0.030 | 261 | 66 |

The 0.01-nat benefit and equivalence margins still need substantive justification. An effect on a decision boundary does not yield high decision probability. E1:B2−B1 remains an implementation contrast: the ideal window-eight information gap is only about 0.000012 nats, so a learned-model contrast cannot establish recurrence necessity.

## Resource sensitivity

The one target-size pilot measured 348.175 seconds for one replicate in each of three worlds, six fits total. Linear multiplication gives the following deliberately rough workload illustrations; multipliers allow sensitivity to different stopping and runtime behavior. They neither predict cap-length runs nor bound total confirmation cost. Memory peaks cannot be multiplied to infer per-fit memory.

| Replicates per world | Linear minutes | Twofold minutes | Fourfold minutes |
|---:|---:|---:|---:|
| 5 | 29.0 | 58.0 | 116.1 |
| 10 | 58.0 | 116.1 | 232.1 |
| 20 | 116.1 | 232.1 | 464.2 |
| 30 | 174.1 | 348.2 | 696.3 |
| 50 | 290.1 | 580.3 | 1160.6 |

Compare these with the historical four-hour training allowance cautiously: pilot elapsed time includes non-training work, while future stopping behavior may differ. Even a row fitting the illustration does not authorize or guarantee that workload.

## Concrete next design gate

Prepare a separate, fixed analysis-calibration specification before any simulations: candidate n values 5, 10, 20, 30 and 50; independent synthetic training-cluster effects and conditional episode noise; normal, skewed and heavy-tail stress cases; seven paired contrasts with declared dependence; current nested percentile, whole-cluster percentile and replicate-mean t candidates. Include benefit/equivalence boundaries, familywise simultaneous coverage, false benefit/equivalence decisions, widths and Monte Carlo error. Synthetic cases must be labelled as assumptions, with no learned-model training or claim that they prove validity for actual losses. Fix seeds, repetitions, bootstrap draws, runtime cap and pass/fail tolerances before executing. That simulation specification is not yet frozen or executed.

A target-data-size variance stage, if needed afterwards, must separately fix fresh training seeds, repeats, validation-only selection, resource limits and failure preservation. Do not reuse target-pilot assessment outcomes to tune training, pool older stages to manufacture target-size variance, choose the most favorable interval or silently stop when a desired conclusion appears. Any final design must state what empirical and simulated calibration still cannot guarantee.

## Reproduction and status

`python3 scripts/rp002a-uncertainty-review.py --check` reproduces `design/UNCERTAINTY_REVIEW.json` from the unchanged configuration and pilot manifest. Input hashes bind both. It reads no assessment array and invokes no random generator. Unit tests enumerate tiny deterministic fixtures; they do not validate inferential coverage.

The baseline, numerical confirmation proposal, approved runs and hypothesis family remain unchanged. RP002A confirmation and Cycle 01 remain PLANNED, with 0/13 Cycle resolutions and no Claim promotion. No extra model run is authorized by this review.
