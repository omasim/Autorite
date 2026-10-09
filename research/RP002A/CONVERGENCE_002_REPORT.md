# RP002A longer-budget convergence-stage review

Date: 2026-10-09. Run: `convergence-20261009-002`. Completed once with no retry, extension or confirmatory evidence.

## Approval and provenance

The user replied “devam edelim” to the explicit request to freeze and execute one 20-unit, 40-fit exploratory stage, with at most 300 epochs and a 1800-second cooperative allowance. The published plan and tested runner preceded approval. The frozen plan passed CI before `docs/research/CONVERGENCE_002_APPROVAL.json` bound its exact hash, baseline hash and reviewed source. Execution source: `1b4cf63d9ad87928e076fe31d1bab4cb9c48664a`. Frozen plan SHA-256: `5c378bdd091bcf336abf5f02cd22989294557564c7320f2c9801262d0dc8ad2b`. The numerical proposal changed only its two freeze/authorization flags.

Python 3.9.6, NumPy 2.0.2, PyTorch 2.8.0, macOS arm64 CPU with two threads. Stage wall time: 383.749 seconds, approximately 6 minutes 24 seconds, within the 1800-second allowance. All 20 independent world/replicate units, 40 learned-model fits and 80 model assessment records completed. E0/E2 have five independent units each; E1 has ten. Each uses fresh 256/128/128 training/validation/assessment episodes of 129 observations, with 140 seeds disjoint from earlier runs and the declared confirmation schedule.

Models, generator laws, learning rate, batching and information access remain as declared. No archived dataset, initialization or checkpoint was reused. Validation selects the minimum-loss checkpoint; assessment data are excluded from optimization and selection.

[Raw immutable artifacts](https://github.com/omasim/Autorite/tree/main/research/RP002A/runs/convergence-20261009-002) retain observed datasets, checkpoints, traces, probabilities, losses, replicate records, summaries and environment. The manifest lists 322 hashed outputs and is an additional file.

## Audit

All output hashes and file coverage pass. Source/approval/plan/baseline binding, seed-derived observed data, B0/B3 reference predictions, saved B1/B2 checkpoint predictions, categorical losses, trace summaries and paired replicate summaries replay successfully. Checkpoint replay performs evaluation only, using explicit floating-point tolerance; it is not a claim of bit-identical cross-platform optimization. Git immutability checks bind the run's file set and bytes once committed. Earlier stage-001 artifacts also pass their audit. Fifty software tests pass; no research training is performed by those tests.

## Convergence diagnostics

Primary near-cap warnings require all 300 epochs and a best checkpoint in epochs 271–300. Primary late-improvement warnings require a decline exceeding 0.001 nats between the first and last losses in the final 20 epochs. The secondary last-five-epoch flag retains the old five-epoch, 0.001-nat rule. These are descriptive warnings, not convergence tests.

| World | Fits | Reached 300 epochs | Best near cap | Primary late improvement | Secondary five-epoch improvement | Early stopping |
|---|---:|---:|---:|---:|---:|---:|
| E0 | 10 | 8 | 8 | 0 | 0 | 2 |
| E1 | 20 | 4 | 4 | 0 | 0 | 16 |
| E2 | 10 | 0 | 0 | 0 | 0 | 10 |

Twelve of 40 fits reached the cap and selected their best checkpoint near it; 28 stopped under the declared patience rule. No fit triggered either late-improvement flag. Under the predeclared disposition rule, **optimization remains unresolved because 12 fits are flagged near the cap**. Absence of late-improvement flags and early stopping do not prove convergence. The time allowance was not binding; the epoch limit remained binding in E0 and some E1 fits. It was not extended.

Stage 001 had 33 cap/near-cap fits and 26 last-five-epoch improvement flags. The new stage has fresh data and seeds, a larger cap, longer patience and different primary windows. Primary flag rates are not directly comparable; even the unchanged secondary rule gives only an unpaired descriptive comparison. Do not attribute between-stage differences solely to more epochs, pool stages or select the most favorable stage.

## Descriptive assessment contrasts

Difference is alternative minus reference natural-log loss; negative values favor the alternative on these exploratory assessment samples. Each summary observation is one independently trained replicate mean. Episode/timepoint counts do not inflate replicate counts. SD and leave-one-out SD ranges are descriptive, not inferential intervals.

| Contrast | Replicates | Mean difference (nats) | Sample SD | Leave-one-out SD range |
|---|---:|---:|---:|---:|
| E1:B1-B0 | 10 | -0.034846 | 0.001559 | 0.001404–0.001653 |
| E1:B2-B0 | 10 | -0.037887 | 0.001371 | 0.001169–0.001448 |
| E0:B1-B0 | 5 | +0.000380 | 0.000225 | 0.000066–0.000259 |
| E0:B2-B0 | 5 | +0.000541 | 0.000066 | 0.000024–0.000076 |
| E2:B1-B0 | 5 | +0.000783 | 0.000328 | 0.000152–0.000378 |
| E2:B2-B0 | 5 | +0.000185 | 0.000165 | 0.000128–0.000187 |
| E1:B2-B1 | 10 | -0.003041 | 0.000668 | 0.000542–0.000708 |

E1 learned-model means were below B0 in this stage. The B2-minus-B1 mean is about -0.003041 nats, smaller in magnitude than the proposed 0.01-nat effect threshold. Control-world mean differences were small but do not establish equivalence. These values do not validate a hypothesis, recurrence necessity, novelty, power or confirmatory sample count. No p-values or inferential intervals were generated.

## Disposition

The approved exploratory run is complete; no additional execution is authorized. The frozen baseline is unchanged, the numerical confirmatory proposal remains separate, no scientific Claim was promoted and Cycle 01 remains PLANNED at 0/13 resolved obligations.

The 256-training-episode setting does not validate optimization or variance at the proposed 4096-episode confirmation setting. Before further execution, review the remaining cap warnings and justify an optimization/variance design rather than automatically increasing epochs again. Any follow-up requires a separately declared scope, fresh seeds, reviewed source and one-run approval. Confirmation also still needs justified margins, sample counts, uncertainty calibration and a complete analysis implementation.
