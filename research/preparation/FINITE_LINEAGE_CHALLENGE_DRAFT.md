# Finite lineage challenge — preparation draft

**Status: PREPARATION ONLY.** This is a working design note following D-0021. It does not open Cycle 03, create a package or Test, commit resources, freeze source or inputs, or authorize execution. No candidate corpus has been generated or scored here.

## Proposed question and boundary

For the two registered RP006 inquiry families, do the same eight whole-field masks over state (`S`), complete direct-parent sets (`P`), and birth operation (`K`) remain sufficient when the comparison corpus contains newly authored, valid lineage logs with four and five entities and both repeated and distinct state payloads?

This is a finite challenge to the transfer of RP006's classifications from six disclosed three-entity constructions to a separately specified corpus. A same-projection/different-answer pair falsifies sufficiency for any declared corpus containing that pair. No conflicts would establish only the finite classification of the reviewed corpus and mask/query class; it would not establish universal, probabilistic, natural-population, or bit-optimal sufficiency.

The registered queries remain unchanged: `same_state`, strict `ancestor`, `shared_root`, `parents`, `birth_kind`, and `alive` for `FULL`; the first four for `TOPOLOGY_STATE`. The eight masks remain `000` through `111` with the existing field meanings. Entity IDs are public and aligned within each stratum, as in RP006. Compare cases only within a stratum; four- and five-entity query universes are not pairwise aligned with one another.

## Candidate finite scope

A reviewable starting point is two entity-count strata (4 and 5), with four candidate constructions in each. The eight slots should be selected before inspecting outcomes and should cover distinct structural motifs: a multi-step continuation; a nested branch with uneven descendant depth; independent roots that later merge; and a mixed branch/merge construction. The final templates must be checked against the six RP004 fixtures so they are not merely renamed or append-only copies. This is a proposed coverage grid, not an authored case inventory.

State assignment is a separate, predeclared factor. Across each stratum, cases should include (a) repeated values, (b) more than one distinct value, (c) equal values on entities with unrelated origins, and (d) a changed value along a connected lineage where the event grammar permits it. `copy` and `fork` must continue to preserve the parent's state as required by the existing construction semantics. Values are opaque labels; no value may encode a case, event position, answer, or intended conflict.

For four cases in each stratum, the expected work from the query inventory alone is 600 `FULL` truth rows and 64 projections (8 masks × 8 cases). There are 96 aligned case-pair/mask comparisons (6 pairs × 8 masks in each of two strata). `TOPOLOGY_STATE` reuses the relevant subset of the same truth table. These are arithmetic estimates for the candidate scope, not measured runtime, a resource commitment, or a run plan.

## Construction and independence controls

- Reuse only the existing event grammar (`root`, `continue`, `copy`, `fork`, `merge`) if the entry review confirms that this is the intended domain. Every input must be a live prior entity; entity IDs must be fresh; operation arities and consumption rules must hold; the acyclic history is the ordered event log.
- Store only case identifiers and event logs in the candidate source. Do not store expected answers, mask verdicts, conflict labels, or per-case descriptive labels in producer input.
- Fix the structural slot definitions and state-payload assignment rule before materializing cases or inspecting their query outcomes. If generation uses a seed, commit the seed policy and generator before generating the final corpus; otherwise specify the deterministic enumeration and selection rule.
- Reconstruct truth directly from the event log in a verifier that does not import producer/query-generation/projection code. Independently enumerate the complete query inventory and check types as well as values.
- Preserve the equality-gated criterion: compare full answers only when canonical projections are exactly equal; record every differing aligned answer as a conflict witness. Retain all no-conflict, conflict, and incomparable minimal-mask outcomes.
- Include validation controls for invalid parent availability, duplicate/future parents, invalid event arity, copy/fork state violations, and an entity count outside the declared strata. Controls test implementation behavior; they do not become additional research cases.
- Compare the final candidate inventory structurally and by hash against the six old fixtures. Report overlap and the rule used to exclude simple extensions before entry review.

## Prior-art boundary

This design sits inside established query-determinacy and provenance work. Segoufin and Vianu define view determinacy by equality of view outputs implying equality of query answers across database instances; their paper also distinguishes that information-theoretic property from effective rewriting. RP006's pairwise equality-and-answer check is a finite corpus analogue, not a new determinacy concept or an all-instances result ([Segoufin & Vianu, *Views and Queries: Determinacy and Rewriting*](https://dbucsd.github.io/paperpdfs/2005_7.pdf)).

Database provenance already studies lineage annotations and algebraic propagation ([Green, Karvounarakis & Tannen, *Provenance Semirings*](https://web.cs.ucdavis.edu/~green/papers/pods07.pdf)). W3C PROV represents derivation between entities and permits qualified derivations that retain additional activity and usage detail ([PROV-DM](https://www.w3.org/TR/prov-dm/#term-Derivation), [PROV-O](https://www.w3.org/TR/prov-o/#qualifiedDerivation)). These are direct conceptual overlaps with ancestry and operation fields.

The plausible contribution, if any, remains a small, reproducible finite comparison of declared fields against declared query answers on an independently authored corpus. This note makes no novelty, theorem, general representation-minimality, or field-necessity claim. The references above are a targeted starting set, not an exhaustive prior-art review or external peer review. Before entry, broaden the collision review to query determinacy for graph views, provenance summarization/abstraction, and finite-instance dependency tests; document search terms, exclusions, and nearest-neighbor differences.

## Gates before any separate entry decision

1. Review the question and the two-stratum comparison rule, including whether keeping both registered inquiry families remains justified.
2. Fix the finite construction templates, entity counts, state controls, public side information, and exclusion test against old fixtures.
3. Complete a scoped prior-art collision review and describe the finite contribution without overclaiming.
4. Independently review the input schema, producer/verifier separation, coverage calculation, negative/conflict handling, and output inventory.
5. Measure feasibility on an explicitly non-research toy workload, with proposed resource limits and suspension behavior reviewed separately.
6. Commit the reviewed protocol and inputs; bind hashes to that exact source state; perform the actual pre-execution review and receive a separate decision before any research run.

Until these gates are reviewed, this document remains a preparation draft only. Cycle 02 remains PUBLISHED; Cycle 03 remains unopened.
