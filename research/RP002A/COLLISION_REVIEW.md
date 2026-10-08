# RP002A literature collision and contribution review

Date: 2026-10-08. Scoped design review, not an exhaustive systematic review or novelty clearance. No new scientific Claim is promoted. The first engineering pilot remains the only model-training run.

## Search and inspection record

Searches on 2026-10-08 covered predictive state representations, observable operator models, recurrent filtering, finite-history prediction benchmarks, and 2024–2026 HMM/next-token comparisons. Queries included `observable operator models Jaeger`, `recurrent networks hidden Markov prediction benchmark 2024 2025 2026`, `Complexity-calibrated Benchmarks`, and `hidden Markov prediction 2025 transformers`. Primary conference, journal, author and arXiv sources were used for judgments. Search snippets only guided discovery. No database-export screening or complete forward/backward citation census was performed; coverage is explicitly incomplete.

## Inspected overlap

| Source | Inspection scope | Established overlap | Consequence for RP002A |
|---|---|---|---|
| [Littman, Sutton & Singh, 2001](https://papers.neurips.cc/paper/1983-predictive-representations-of-state.pdf) | Prior recorded reading of sections 1–2 and Theorem 1 | Predictive state and recursive updates for finite partially observed models | No novelty for representing predictive history recursively |
| [Thon & Jaeger, 2015](https://www.jmlr.org/papers/volume16/thon15a/thon15a.pdf) | Introduction and model relationship discussion; not all proofs | Links between HMMs, observable operator models and predictive state representations | Our finite HMM and belief filter lie inside established model families |
| [Downey et al., 2017](https://proceedings.neurips.cc/paper_files/paper/2017/file/2bb0502c80b7432eee4c5847a5fd077b-Paper.pdf) | Abstract and introduction | Predictive recurrent networks combine filtering, prediction and learned updates | Learned recursive prediction is not a new architecture category |
| [Hefny et al., 2018](https://proceedings.mlr.press/v80/hefny18a/hefny18a.pdf) | Sections 1–3, including filtering and two-stage initialization | Predictive-state filtering with end-to-end optimization in a policy architecture | Control/rewards differ from our passive task; GRU training must not inherit their initialization guarantees |
| [Marzen, Riechers & Crutchfield, 2024 author manuscript](https://csc.ucdavis.edu/~cmg/papers/ngrc.pdf) | Abstract, process/finite-history discussion and entropy-gap analysis; manuscript dated March 28, 2024 | Complexity-calibrated stochastic prediction benchmarks and limitations of finite-past traces | Close collision with the proposed finite-window versus history-reference comparison |
| [Piotrowski et al., arXiv v2, 2025](https://arxiv.org/abs/2502.01954v2) | Abstract and version metadata only | HMM next-token prediction and constrained belief updates in transformers | Modern overlap lead; architecture-specific results are not transferred to GRUs |

The Marzen et al. overlap is particularly direct: measuring a finite-history predictor against attainable prediction limits is already a benchmark strategy. Our erasure-bit process is a small transparent fixture; we have not established that its exact parameterization is unique. The transformer paper remains a scoped discovery lead, not a full-method clearance. No unsupported claim of first use is made.

## Generator and comparator mapping

E0 is a fully observed stationary two-state Markov chain. E1 is the same chain with independent observation erasures. E2 has independent latent bits and independent erasures. B3 is the ordinary observed-history Bayesian filter, not access to realized latent states. B0 is a learned current-observation categorical table; B1 and B2 are generic MLP/GRU predictors. These are operational test fixtures and existing methods.

## Contribution disposition

Retain RP002A as a controlled boundary and reproducibility study. Its useful deliverable is a traceable comparison with declared information access, causal resets, explicit optimization limits and negative/indeterminate outcomes. Do not claim a new memory theory, new recurrent architecture, recurrence necessity or general unification. A publishable novelty claim needs an identified difference and broader citation/benchmark review; novelty is not required to execute an honestly framed replication/boundary study.

## Remaining collision work

Inspect the closest benchmark's released generators/evaluation code if available; compare loss target, erasure construction and information access explicitly. Read the full 2025 transformer methods only if making an architecture-comparison claim. Extend forward/backward citations before any novelty assertion. These tasks do not justify changing the frozen baseline definitions.
