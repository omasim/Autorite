# RP002A confirmatory design review

Follow-up (2026-10-10): this earlier planning review is historical. Calibration, target-size variance and pre-outcome freeze completed. The first confirmation attempt is incomplete after a wall-time incident, with no confirmatory decisions. See `CONFIRMATORY_001_REPORT.md`; the historical numerical proposal is unchanged.

Date: 2026-10-08. Planning review only. No new samples, model training, confirmatory outcomes or scientific Claim promotions. `CONFIG_PROPOSAL.json` remains unfrozen and unauthorized; the approved pilot and its raw artifacts are unchanged.

## What the declared generator can distinguish

For flip probability p and erasure probability q, let r = 1 − 2p. If the last visible bit was k steps before the current observation, its posterior sign decays by r^k. The next hidden bit's binary entropy is h((1+r^(k+1))/2), where h uses natural logarithms. Independent next-observation erasure adds h(q) and scales the hidden-bit entropy by (1−q).

After t observations, the probability that the last visible bit has age k<t is (1−q)q^k. The probability of no visible bit in the prefix is q^t, in which case the hidden bit remains equiprobable. Therefore the full observed-history ideal loss is:

`h(q) + (1−q) [ Σ(k=0..t−1) (1−q)q^k h((1+r^(k+1))/2) + q^t log(2) ]`.

For an ideal predictor restricted to the last w observations, replace t inside the bracket by min(t,w). Current-only prediction uses w=1. Average over t=1..128 to match the proposed episode metric. These are our deterministic operational calculations, not a new theorem or learned-model result. Independent hidden-path enumeration verifies short-history conditional entropies in software tests.

| World | Ideal current only | Ideal window 8 | Ideal full observed prefix | Current-to-history gain | Window-to-history gap |
|---|---:|---:|---:|---:|---:|
| E0 | 0.325083 | 0.325083 | 0.325083 | 0 | 0 |
| E1 | 0.947705 | 0.907908 | 0.907896 | 0.039809 | 0.000012 |
| E2 | 1.039721 | 1.039721 | 1.039721 | 0 | 0 |

Reproduce with `python3 scripts/rp002a-design-review.py --check`. Exact numeric values and configuration hash are in `research/RP002A/design/ANALYTIC_REVIEW.json`. No random generator is invoked by that calculation.

These distribution-aware ideal predictors are different from learned B0/B1/B2. The E1 history opportunity is about 0.03981 nats, so a 0.01-nat learning benefit could be meaningful relative to this fixture. That does not establish an externally meaningful effect threshold. The ideal window-eight gap is roughly 826 times smaller than 0.01 nats. A learned B2 beating a particular B1 by 0.01 could reflect approximation, optimization or finite data rather than information that inherently requires recursion. B1–B2 is therefore an implementation comparison, never a recurrence-necessity test.

This interpretation agrees with the existing finite-past benchmark perspective documented in the [collision review](https://autorite.net/sources/rp002a-collision-review/). The numerical erasure-process calculation is our planning derivation; it is not attributed to that source.

## Estimand and independent units

For each world and contrast, define the estimand as expected paired episode-mean log-loss difference across independently trained replicates. Each replicate must draw independent training, validation and held-out episodes and model/batch randomness. Within a replicate all models share held-out episodes. Reduce timepoints to episode means, then to one paired mean per training replicate; give replicates equal weight.

Independent held-out episodes estimate conditional prediction uncertainty for a fixed trained model. They do not replace independent training replicates when measuring algorithm variability. This distinction is also motivated by [Bengio & Grandvalet's variance discussion](https://www.jmlr.org/papers/v5/grandvalet04a.html), although RP002A uses independent holdouts, not their overlapping cross-validation setting.

## Precision sensitivity, not a completed power claim

The proposed five training replicates cannot be justified from the single engineering pilot. No between-replicate variance estimate exists. More held-out episodes cannot repair this missing information.

For illustration only, a normal approximation with seven two-sided Bonferroni intervals at familywise alpha=0.05 gives z≈2.690. Half-width is z × assumed replicate SD / sqrt(n). It treats SD as known and may be optimistic; a Student-t or hierarchical bootstrap procedure has its own assumptions and finite-sample calibration requirements.

| Assumed SD of replicate means | n=5 | n=10 | n=20 | n=30 | n=50 |
|---|---:|---:|---:|---:|---:|
| 0.01 | 0.0120 | 0.0085 | 0.0060 | 0.0049 | 0.0038 |
| 0.03 | 0.0361 | 0.0255 | 0.0180 | 0.0147 | 0.0114 |
| 0.05 | 0.0602 | 0.0425 | 0.0301 | 0.0246 | 0.0190 |
| 0.10 | 0.1203 | 0.0851 | 0.0602 | 0.0491 | 0.0381 |

Every SD above is hypothetical, not fitted to the pilot. Even n=30 is insufficient for a 0.01-nat half-width if SD is 0.03. Precision is not power: a benefit decision requiring the entire interval below −0.01 needs the true difference to lie sufficiently below −0.01; an effect exactly at that boundary cannot give high decision probability. Equivalence requires an entire interval within [−0.01,+0.01], not a nonsignificant comparison. [NIST's sample-size discussion](https://www.itl.nist.gov/div898/handbook/prc/section2/prc222.htm) similarly distinguishes error rate, desired detection and unknown variability; our table is a problem-specific planning illustration.

Do not freeze five replicates or claim 80% power. Retain 0.01 as a sensitivity target awaiting substantive justification. Compare alternative margins before confirmation and record one fixed choice. The hierarchical bootstrap primitive is implemented but its coverage is not validated by successful software tests.

## Recommended next stage and freeze gates

Prepare a separately reviewed exploratory convergence/variance plan with fresh seeds and validation-only model selection. Its scope should test whether the chosen training budget is adequate and estimate between-training variability across several independent fits. Do not optimize against the already inspected pilot diagnostics; preserve them as engineering evidence only. A future plan must name sample counts, repeats, stopping rules and resource caps before execution. No such extra run is authorized by this review.

Then choose confirmatory replicate count using explicit variance assumptions and sensitivity or a separately validated analysis-calibration procedure. Check whether the fixed CPU budget can accommodate the resulting training workload. Fix environment/hardware, full analysis outputs, calibration bins, failure handling and all secondary measures; not all are implemented in the current pilot runner. Confirmatory evaluation must use a separate runner and untouched seed namespace, with exact pre-outcome approval metadata.

No hypothesis family, baseline scientific definition, pilot output or Cycle resolution is amended here. The numerical proposal is preserved as a historical proposal; this review explains why it is not ready to freeze.

## Uncertainty design follow-up — 2026-10-09

`research/RP002A/UNCERTAINTY_DESIGN_REVIEW.md` audits the current nested resampling variance and extreme-tail bootstrap resolution, with deterministic precision/resource sensitivity. Target-size variance, analysis coverage and substantive margins remain open. No final sample count or interval is chosen; no new training, Claim or Cycle resolution. The historical numerical proposal remains unchanged.
