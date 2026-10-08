# RP002A — Operational protocol draft

Version: working-0.1. Date: 2026-10-08. **Exploratory design proposal, not a frozen preregistration.** No model training or confirmatory outcomes have been observed. This supplement does not amend the selected baseline.

## Predictive query

Proposed primary task: estimate the distribution of the next observation, given the observations available through time t. Target alphabet: `{0, 1, erasure}`. Horizon: one step. Longer horizons are secondary candidates and must be separately specified before use.

Predictive information, not hidden-state decoding, is the target. The generator may expose hidden states to diagnostics, but B0–B2 must never receive them.

## Candidate finite stationary worlds

Use a two-state hidden Markov process with a symmetric bit-flip probability p and an independent observation erasure probability q. When not erased, the observation equals the hidden bit. Start each independent episode from the stationary distribution. Transition and observation laws remain constant throughout an episode.

| World | Candidate law | Intended sanity condition |
| --- | --- | --- |
| E0 | q = 0; persistent hidden bit | Current observation suffices for next-observation prediction. |
| E1 | 0 < p < 1/2 and 0 < q < 1 | During erasures, prior observations can change the predictive distribution. |
| E2 | p = 1/2 and 0 < q < 1 | Observations are independent across time; history is future-irrelevant. |

These laws are proposed fixtures, not adopted benchmark defaults. Choose exact probabilities and any additional families only after collision review. E0's erasure probability is zero; retain the common output alphabet rather than changing model dimensionality. Inspect E1 performance conditional on erasure as well as the overall primary measure, since visible observations can dilute the informative subset. E2 uses the same observation alphabet as E1 to avoid making the null merely an alphabet difference.

## Proposed reference and sanity checks

B3 should be the generator-derived Bayes predictor conditional on the same full observed history, with exact recursive filtering. It does not read the realized hidden state. A privileged latent-state predictor may be a separately named diagnostic, not a replacement for this information-matched reference.

Before model comparison, verify transition/emission normalization, stationary initialization, conditional independence assumptions, exact-filter predictions against enumerated short histories, and the E0/E2 history-irrelevance conditions. Verify that at least two positive-probability E1 histories ending with the same current observation yield different next-observation distributions. These are proposed generator acceptance checks, not reported research results.

## Proposed learned comparisons

- B0: current-observation categorical predictor.
- B1: finite window of observations, with explicit beginning-of-episode padding/mask.
- B2: a fixed-dimensional recurrent state updated with the next observation; a GRU is a candidate implementation.
- B3: the information-matched exact filter described above; it is a reference, not a learned competitor.

Select B1's model, history window, B2's state dimension and optimization budgets before confirmatory data. Match parameter counts and training resources where feasible and report the remaining differences. Include a simple tabular current-observation B0 so failures of an unnecessarily complex B0 do not manufacture a history benefit. Do not interpret B2 beating one particular B1 as a proof that recurrence is necessary.

## Splits, randomness and leakage

Partition by independently generated whole episodes, never by adjacent time points from the same episode. Specify disjoint train/validation/test generator seeds and separate model-initialization seeds in an immutable run manifest. Reset recurrent state and history buffers at every episode boundary. Fit preprocessing only on training data. Tune on validation data; access confirmatory test outcomes only after configuration freeze.

Generator seeds and model seeds are distinct experimental factors. Correlated timestamps from one episode are not independent replicates. Paired comparisons must use the same held-out episodes across baselines.

## Measures and inference proposals

Log loss in natural-log units is the proposed primary metric, retaining its baseline status as a candidate until frozen. Compute timepoint losses, then episode-level means; define weighting across seeds/worlds explicitly. Report probability calibration and erasure-conditioned diagnostics as secondary measures. Fix probability clipping and its rationale before results, and keep an unclipped diagnostic when finite.

Set a smallest meaningful effect before confirmation. Define an equivalence procedure for E0/E2 and B1 versus B2; failure to reject a difference is not evidence of equivalence. Specify intervals that respect episode and training-seed dependence, the family of primary comparisons, and how multiplicity is handled. Keep world-specific conclusions rather than pooling away the intended boundaries.

## Resource and stopping contract

Before any execution, declare the hardware/software environment, data sizes, model sizes, optimizer, learning schedule, early-stopping rule, maximum steps, total CPU/GPU budget, repeat count and failure/retry policy. Stop at the declared budget; do not extend it in response to a desirable or surprising effect without a recorded exploratory deviation.

An exploratory pilot may check generator correctness, numerical stability and approximate resource cost. It requires a separately fixed pilot manifest and remains excluded from confirmatory evidence. No pilot is authorized by this draft alone.

## Freeze checklist

The following choices remain **pending**, not hidden defaults:

1. Full collision assessment and final generator families/parameters.
2. Exact predictive query/horizon and episode length.
3. Training, validation and test episode counts.
4. Generator/model seed schedules and number of repeats.
5. B0–B2 architectures, window/state sizes and resource matching.
6. Optimizer, learning rates, steps and early stopping.
7. Primary metric acceptance, aggregation, clipping and effect threshold.
8. Uncertainty, equivalence and multiplicity procedures.
9. Calibration and secondary diagnostics.
10. Failed-run, retry, stopping and deviation rules.
11. Reproducibility environment and artifact manifest.
12. Bootstrap audit/release approval, protocol hash and pre-outcome freeze record.

## Interpretation boundaries

E1 benefits support only the declared generators, queries, models and budgets. E0/E2 benefits trigger capacity/leakage/generator investigation. E1 failure triggers generator/model/optimization diagnosis. B1–B2 equivalence does not establish a special recurrent-state advantage. None of these comparisons establishes universal memory, full-history retention or a general ontology.

## Provenance

Baseline: `baseline/RP002A_PREREGISTRATION.md`; implementation gates: `RESEARCH_EXECUTION_READINESS.md`; literature overlap: `research/RP002A/PRIOR_ART_REVIEW.md`. All construction and analysis choices above are explicitly proposed operational choices.
