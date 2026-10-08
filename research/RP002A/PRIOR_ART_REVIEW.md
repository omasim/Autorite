# RP002A — Initial prior-art review

Date: 2026-10-08. Working review, not a completed collision assessment or frozen protocol. No experiments were run. Baseline definitions are unchanged.

## Question and scope

In finite partially observed stochastic processes, when does recursively updated history recover predictive distinctions unavailable in current observation? The baseline limits the package to passive, discrete stochastic processes stationary within episodes.

## Sources inspected

### Predictive Representations of State

Michael L. Littman, Richard S. Sutton and Satinder Singh, NIPS 2001. [Paper](https://papers.neurips.cc/paper/1983-predictive-representations-of-state.pdf). The inspected full-text copy is also available at [Georgia Tech](https://faculty.cc.gatech.edu/~isbell/reading/papers/predictive-nips2001.pdf). Sections 1–2 define predictive sufficiency and recursive updating; Theorem 1 establishes a finite linear predictive representation for finite POMDP models.

Our preliminary collision judgment: representing predictive information in a recursively updated state is established prior art. RP002A cannot claim novelty for that general idea. Its passive setting is narrower than the paper's action-conditional framework. The finite-history comparison and representation sufficiency are directly relevant; existence of an exact representation does not establish that our learned B2 will recover it under finite data and optimization budgets.

### Recurrent Predictive State Policy Networks

Ahmed Hefny, Zita Marinho, Wen Sun, Siddhartha Srinivasa and Geoffrey Gordon, ICML 2018. [Proceedings and abstract](https://proceedings.mlr.press/v80/hefny18a.html). Inspection in this first pass is limited to the proceedings abstract. It introduces a recurrent architecture informed by predictive state representations for reinforcement learning under partial observability.

Our preliminary collision judgment: recurrent learned representations under partial observability are also established prior art. Policy learning is outside RP002A's passive scope. A full-method reading is still needed before borrowing architectural or optimization choices.

## Working contribution boundary

Treat RP002A initially as a controlled boundary study and reproducibility exercise, not a new memory theory or new recurrent architecture. Compare current observation, a finite history window, learned recursive state and a generator-derived prediction reference across E0/E1/E2. Any novelty statement requires a broader, documented search and an explicit difference from existing benchmarks and theory.

## Open protocol decisions

Before confirmatory runs: select the prediction target and horizon; define E0/E1/E2 transition and observation laws; distinguish an observable-history Bayes reference from a latent-state privileged oracle; fix episode lengths, sample counts, split independence and seeds; choose B0–B2 models and capacity/optimization controls; fix history window and recurrent-state size; select the primary metric, effect-size threshold, uncertainty and aggregation; define equivalence/non-superiority criteria, calibration, failed-run handling and stopping rules.

A latent-state oracle may have extra information unavailable to every learned model. The protocol must state that information difference before interpreting the gap to B3. The baseline's oracle label alone does not resolve this operational choice.

## Next review tasks

1. Read the full RPSP methods and its references.
2. Review belief-state filtering, hidden Markov prediction, observable operator models and finite-history representation bounds.
3. Search newer work and existing synthetic comparison suites; record search dates and scope.
4. Map each proposed generator and baseline to prior constructions.
5. Complete the collision assessment before a novelty claim or confirmatory protocol freeze.

## Search provenance and limits

Search date: 2026-10-08. Initial queries targeted predictive representations of state, partial observability and recurrent belief representations on academic and conference domains. This is a seed review, not an exhaustive systematic search. No claim of literature completeness or scientific support is made. Search snippets were used for discovery; the judgments above use inspected paper text or the identified abstract, with that boundary stated.

## Follow-up review — 2026-10-08

`COLLISION_REVIEW.md` expands this seed review with scoped primary-source inspection, including the close finite-history benchmark overlap. `CONFIRMATORY_DESIGN_REVIEW.md` records deterministic information-gap and precision calculations. These are working design records, not novelty clearance, model outcomes or new scientific Claims. The completed isolated engineering pilot remains separate.
