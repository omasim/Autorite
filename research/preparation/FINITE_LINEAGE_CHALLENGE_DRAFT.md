# Finite lineage challenge — preparation draft

**Status: PREPARATION ONLY.** This is a working design note following D-0021. It does not open Cycle 03, create a package or Test, commit resources, freeze source or inputs, or authorize execution. The proposed templates below remain prose for review; no machine-readable candidate corpus has been generated and no candidate query outcomes have been computed. A separate synthetic software-only probe is recorded below; its answer outputs were not retained or inspected.

## Proposed question and boundary

For the two registered RP006 inquiry families, do the same eight whole-field masks over state (`S`), complete direct-parent sets (`P`), and birth operation (`K`) remain sufficient when the comparison corpus contains newly authored, valid lineage logs with four and five entities and both repeated and distinct state payloads?

This is a finite challenge to the transfer of RP006's classifications from six disclosed three-entity constructions to a separately specified corpus. A same-projection/different-answer pair falsifies sufficiency for any declared corpus containing that pair. No conflicts would establish only the finite classification of the reviewed corpus and mask/query class; it would not establish universal, probabilistic, natural-population, or bit-optimal sufficiency.

The registered queries remain unchanged: `same_state`, strict `ancestor`, `shared_root`, `parents`, `birth_kind`, and `alive` for `FULL`; the first four for `TOPOLOGY_STATE`. The eight masks remain `000` through `111` with the existing field meanings. Entity IDs are public and aligned within each stratum, as in RP006. Compare cases only within a stratum; four- and five-entity query universes are not pairwise aligned with one another.

## Candidate finite scope

A reviewable starting point is two entity-count strata (4 and 5), with four candidate constructions in each. The eight slots should be selected before inspecting outcomes and should cover distinct structural motifs: a multi-step continuation; a nested branch with uneven descendant depth; independent roots that later merge; and a mixed branch/merge construction. The final templates must be checked against the six RP004 fixtures so they are not merely renamed or append-only copies. This is a proposed coverage grid, not an authored case inventory.

### Proposed template grid for structural review

The following event notation omits states: `root(x)`, `continue(x→y)`, `copy(x→y)`, `fork(x→y,z)`, and `merge(x,y→z)`. IDs are the public aligned IDs within each stratum. The sequences are proposals, not frozen event-log inputs. Their intended order is part of each template.

| Slot | Entities | Ordered event structure | Motif |
| --- | ---: | --- | --- |
| F4-01 | 4 | `root(a); copy(a→b); continue(b→c); root(d)` | A copied lineage continues; a separate root supplies an unrelated component. |
| F4-02 | 4 | `root(a); continue(a→b); fork(b→c,d)` | A continued entity branches into two live leaves. |
| F4-03 | 4 | `root(a); copy(a→b); root(c); merge(b,c→d)` | A copy-derived entity merges with an independently rooted entity. |
| F4-04 | 4 | `root(a); root(b); copy(b→c); continue(a→d)` | Two roots develop differently, with a copy on one side and a continuation on the other. |
| F5-01 | 5 | `root(a); continue(a→b); fork(b→c,d); continue(c→e)` | A nested branch has unequal descendant depth. |
| F5-02 | 5 | `root(a); root(b); fork(a→c,d); merge(b,c→e)` | A branch is partly merged with an independent root; its other branch remains live. |
| F5-03 | 5 | `root(a); copy(a→b); root(c); continue(c→d); merge(b,d→e)` | Two independently rooted lines, with different operations, meet in a merge. |
| F5-04 | 5 | `root(a); root(b); continue(b→c); copy(c→d); merge(a,d→e)` | A two-step line meets a separate root, with a retained copy on the line. |

For a first legality pass, state vectors are listed in ID order and use opaque labels `A`, `B`, and `C`. These are proposed controls, not outcome-derived assignments. They obey the existing rule that `copy` and both `fork` outputs preserve the relevant parent's state; `continue` and `merge` may emit another opaque value.

| Slot | Proposed state vector (`a,b,c,d[,e]`) | Coverage role |
| --- | --- | --- |
| F4-01 | `(A,A,B,A)` | Repetition, a changed continuation, and equal values on unrelated roots. |
| F4-02 | `(A,B,B,B)` | A changed continuation followed by state-preserving fork outputs. |
| F4-03 | `(A,A,B,B)` | Distinct values, with a merge output sharing the independent root's value. |
| F4-04 | `(A,A,A,A)` | Repeated values across unrelated roots. |
| F5-01 | `(A,B,B,B,C)` | A changed continuation and unequal branch depth, with fork state preserved. |
| F5-02 | `(A,B,A,A,B)` | Distinct values across roots, with the fork preserving `a` and the merge output assigned `B`. |
| F5-03 | `(A,A,B,C,D)` | Copy preservation and a changed continuation across distinct payloads. |
| F5-04 | `(A,B,C,C,A)` | A changed continuation, copy preservation, and a merge output sharing `a`'s value. |

An in-memory, schema-only check using the existing RP004 construction grammar accepted all eight proposed event logs and their copy/fork state constraints. A separate ID-permutation comparison found no duplicate event graphs within either count stratum and no complete disclosed fixture as the first three events under renaming. This excludes a direct fixture-prefix-plus-appended-events pattern, not every possible shared substructure. F4-02 composes continuation with branching; F5-01 adds an unequal-depth descendant; the merge cases change parent structure or combine motifs. Before entry, an independent reviewer should repeat this check against the source-hashed fixture file and document any broader subgraph overlap.

The proposed vectors give each stratum repeated and distinct payloads, equal labels on unrelated roots, and a changed value along a connected continuation. They do not settle whether every slot is needed, whether both query families remain justified, or whether the planned eight cases are the best finite coverage. Those remain review questions.

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

## Candidate input, verifier, and evidence contract

This section specifies a review target only. It does not create the candidate inputs, freeze a schema, or authorize a producer run.

### Input boundary

Use two separate future input documents, one for the four four-entity cases and one for the four five-entity cases. Each document should contain only a case identifier and its ordered event log, with state payloads attached to the corresponding event output under the accepted RP004 grammar. The public entity universe is `a`–`d` or `a`–`e`, respectively, and must be common to all cases in that document. Keeping strata as separate inputs makes cross-size comparison impossible by construction; a later evidence manifest may label the stratum but must not merge their comparison universes. Do not put expected query answers, mask results, conflict expectations, motif/coverage labels, or prose explanations in producer input. The state vectors above remain review material until a separate input-freeze decision.

Before any future run, validate exact keys and types, unique case IDs, exact entity coverage, ordered event legality, and the copy/fork state-preservation rule. Reject unknown fields and malformed values rather than silently normalizing them. Hash the exact input bytes. Candidate identity and case ordering must be fixed before answer inspection; deterministic ordering should be by case ID, query family, mask, and canonical query key. The exact JSON canonicalization and byte-level serialization rules must be declared and versioned before freeze.

### Independent verifier boundary

The proposed verifier may rely on the accepted event semantics and replay domain, but it must independently reconstruct the entity facts and enumerate the registered query inventory. It must not import or call the future producer, its query enumerator, projection builder, conflict scanner, or certificate builder; it must not consume producer-generated truth rows as ground truth. The verifier should independently check input validity, truth rows, projected retained fields, all within-stratum pair/mask equality decisions, every equality-gated answer comparison, every conflict witness, certificate partitions and minimality claims, summary counts, and hashes. Producer and verifier should be authored and source-hashed separately. A disagreement is a failed verification, preserved with both outputs for diagnosis; it must not be resolved by editing expected answers or dropping a case after observing outcomes.

### Coverage arithmetic and edge handling

For the proposed inventory, the exact structural workload is:

| Stratum | FULL truth rows | Projections | Pair/mask comparisons | Family/mask certificates |
| --- | ---: | ---: | ---: | ---: |
| 4 entities × 4 cases | 240 | 32 | 48 | 16 |
| 5 entities × 4 cases | 360 | 32 | 48 | 16 |
| Total | 600 | 64 | 96 | 32 |

The per-case `FULL` query count is `3n² + 3n` (ordered pairs for the three pairwise families and one row per entity for the three unary families). `TOPOLOGY_STATE` uses the same truth inventory and checks its registered first-four-family subset. The 96 comparison records are present even when projections differ; answer checks are performed only for equal projections, and their number is outcome-dependent. No cross-stratum pairs are valid. These counts are protocol arithmetic, not query outcomes or measured work.

Each equal-projection comparison must retain all differing query answers, not just the first witness. An equal projection with no differing answer is recorded as an observed no-conflict pair; a non-equal projection is recorded as not answer-compared. Certificates must preserve the full equivalence partition for each mask/family, mark a partition's common answer vector only when all members agree, and record an explicit conflict state otherwise. Compute sufficiency and inclusion-minimality over all eight masks, retaining incomparable minimal masks. The protocol must not assume in advance that a conflict exists or that any particular mask is sufficient.

Coverage checks should independently assert: every candidate case appears once per stratum; all eight masks occur per case; each expected family/query row occurs exactly once; every unordered pair in a stratum appears for every mask; every certificate family/mask combination exists; and the verifier rejects each invalid-input control listed above. Invalid-input controls are kept outside the research corpus and never counted in the table. Missing rows, duplicate rows, mismatched hashes, or a comparison across different strata invalidate the evidence package.

### Future evidence inventory

If a later decision authorizes execution, the reviewed output contract should include:

- a manifest with protocol/schema versions, stratum, case/entity counts, exact input and source hashes, query/mask configuration, and deterministic ordering rules;
- complete truth rows, with query family/key and typed answer;
- all case/mask projections in canonical form;
- a record for every within-stratum unordered pair and mask, including projection equality and whether answers were compared;
- all conflict witnesses, including the differing query key and both typed answers;
- family/mask certificates with equivalence classes, common answer vectors or explicit conflict markers, sufficiency, and proper-submask evidence for inclusion minimality;
- a summary derived from those records, plus an independent verification receipt containing pass/fail, validated inventory counts, and hashes of the exact evidence and verifier source.

The verifier receipt is not itself proof of correctness; the verifier source and reproducible evidence remain part of the reviewable package. A future evidence contract must specify whether outputs are JSON or JSONL, canonical byte encoding, numeric/boolean typing, and stable row ordering before freeze. At present none of these output files exists for this challenge, and no candidate answers have been generated. The separate, non-research software feasibility probe below does not populate this evidence inventory.

## Prior-art boundary

View determinacy is already a formal information-theoretic property: equality of view outputs must force equality of query answers across the declared database-instance universe. The database-theory literature distinguishes finite-only from unrestricted instance universes, so this note must not use “finite determinacy” as a label for eight hand-selected cases. RP006 and the proposed challenge make finite-corpus comparisons; neither establishes determinacy over all finite databases ([Nash, Segoufin & Vianu, *Views and Queries: Determinacy and Rewriting*](https://dbucsd.github.io/paperpdfs/2010_3.pdf)).

A particularly close preservation result is Fan, Geerts and Zheng's formalization of selected-information preservation through invertibility and query preservation. They show that invertibility relative to a source query coincides with view determinacy, with results quantified over the declared database-instance class ([Fan et al., *View Determinacy for Preserving Selected Information in Data Transformations*, 2012](https://doi.org/10.1016/j.is.2011.09.001); [peer-reviewed author version](https://www.pure.ed.ac.uk/ws/portalfiles/portal/17752772/paper_viewd.pdf)). This makes query-relative preservation an established conceptual frame. The proposed work differs only at the operational level: a fixed finite corpus, fixed answer functions, and a declared whole-field mask class. That difference supports a reproducible finite challenge, not a new determinacy concept or a novelty claim.

The graph-view collision is direct. Work on path-query views studies determinacy over graph databases, and recent work studies regular-path views under walk-based semantics. Those papers vary query languages and quantify over database graphs; they are not this fixed aligned-entity corpus or its eight whole-field masks. They rule out presenting ancestry-query sufficiency as a new general determinacy concept ([Francis, *Asymptotic Determinacy of Path Queries using Union-of-Paths Views*](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ICDT.2015.44); [Francis, *View-Based Query Determinacy for Walk-Based Semantics*](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ICDT.2026.22)).

Following references from the graph-view literature also surfaces foundational overlaps. *Answering Queries Using Views* studies complete and minimal rewritings from materialized views; *Lossless Regular Views* asks when graph/path views preserve enough information to answer a query; and Afrati studies the relationship between determinacy and rewriting for conjunctive-query views. Together these make query-relative preservation and recovery from reduced information an established problem family, even though their language-defined views and database-wide semantics differ from the proposed finite, aligned-case comparison ([Levy et al., PODS 1995](https://doi.org/10.1145/212433.220198); [Calvanese et al., PODS 2002](https://iris.uniroma1.it/handle/11573/252669); [Afrati, *Determinacy and Query Rewriting for Conjunctive Queries and Views*](https://doi.org/10.1016/j.tcs.2010.12.031)).

Provenance work also studies abstraction and information loss. Existing systems summarize why/why-not provenance by grouping derivation patterns; SGProv compresses multiple workflow provenance graphs while retaining selected query answers; and later provenance-graph work segments derivations and summarizes similar paths under provenance constraints. These overlap with the concern that reduced fields may collapse distinctions relevant to answers; they use different representations, query tasks, and summaries ([Lee et al., *Integrating Approximate Summarization with Provenance Capture*](https://www.usenix.org/conference/tapp17/workshop-program/presentation/lee); [El-Jaick et al., *SGProv: Summarization Mechanism for Multiple Provenance Graphs*](https://periodicos.ufmg.br/index.php/jidm/article/view/249); [Miao & Deshpande, *Understanding Data Science Lifecycle Provenance via Graph Segmentation and Summarization*](https://arxiv.org/abs/1810.04599)). Database provenance also has established algebraic lineage models ([Green, Karvounarakis & Tannen, *Provenance Semirings*](https://web.cs.ucdavis.edu/~green/papers/pods07.pdf)), and W3C PROV explicitly models derivation and qualified derivation ([PROV-DM](https://www.w3.org/TR/prov-dm/#term-Derivation), [PROV-O](https://www.w3.org/TR/prov-o/#qualifiedDerivation)).

The expanded search followed selected references from the graph-view and view-determinacy papers and added foundational view-rewriting and provenance-graph summarization work. It used the terms “view determinacy graph databases path queries,” “provenance graph summarization abstraction,” “why-not provenance approximate summarization,” and “finite database view determinacy,” with primary conference/publisher and author-hosted records. It still is not a systematic citation-chain or database-index search, and it is not novelty clearance. The only defensible possible contribution remains a reproducible finite comparison of declared fields against declared answers on a separately reviewed corpus. No theorem, general representation-minimality, universal field-necessity, or novelty claim follows.

## Non-research software feasibility probe

On 2026-10-13, the existing RP006 producer and separately implemented verifier were exercised on a synthetic in-memory control domain with three toy cases and three entities. This domain was authored only to measure software overhead; it is not one of the proposed F4/F5 cases and is not candidate evidence. Five producer → verifier → canonical serialization rounds all passed. Each round handled 108 truth rows, 24 projections, 24 pair/mask comparisons, and 16 family/mask certificates. Serialized output size was 52,203 bytes per round. Median round time was 0.00717 seconds and maximum was 0.00771 seconds. The process lifetime peak RSS, including imports, was 14,778,368 bytes. No input, answer output, artifact, or report file was written; returned answer-bearing objects remained in memory and were discarded without inspecting individual answers or conflict/sufficiency results.

The probe used the existing engineering guard limits: 60 seconds, 134,217,728 bytes peak process RSS, and no more than a two-second civil/monotonic clock gap. Across the five rounds the guard's total measured interval was 0.03654 seconds with a clock gap below one microsecond. These observations establish only that this tiny local software path completed under those limits on the current host. The proposed challenge's arithmetic inventory is larger (600 truth rows, 64 projections, 96 pair/mask comparisons, 32 family/mask certificates across two separate strata); the toy timings and bytes do not establish a scale guarantee or forecast conflict-dependent output size. The probe did not test disk durability, archive packaging, host suspension, child-process policy, or a fresh independent implementation.

For any later recorded attempt, retain the 60-second/128-MiB ceilings only as provisional controls until they are reviewed against the actual challenge and output format. Stop and preserve an incomplete diagnostic if a sampled resource limit is crossed, clocks regress, the civil/monotonic gap exceeds two seconds, validation fails, or producer/verifier results differ. The cooperative guard cannot itself stop a suspended or runaway worker; an external suspension-aware supervisor and child-process policy must be reviewed before a recorded attempt. This probe does not authorize that attempt.

## Internal design review (2026-10-14)

This is an internal preparation critique, not the independent design review required before entry. The proposed question is falsifiable on a fixed corpus: a same-projection/different-answer pair is a counterexample for that family, mask, and corpus. A conflict-free result classifies only the reviewed cases. Neither outcome supports transfer to a population of possible lineages.

The eight cases are a purposive motif grid, not a sample. Four and five entities extend the disclosed three-entity examples, but count alone does not ensure substantive novelty or broad coverage. The stated prefix exclusion is useful but weaker than the required unlabeled-structure and shared-subgraph comparison. Keep the current templates provisional until a reviewer checks coverage, operation semantics, full overlap, and whether the two registered query families still answer the question worth asking.

The strongest defensible outcome is a finite stress test, especially if it yields an auditable conflict that rejects a previously sufficient mask on a new case pair. No conflict would be a bounded consistency result. Given the close view-determinacy and selected-information-preservation literature, a full Cycle 03 entry is worthwhile only if the independent review confirms that this finite challenge has a clear decision value beyond software validation. Otherwise, prioritize primary DAM/DAM X source recovery or choose a separately justified question. No candidate answers, input corpus, or run were produced for this review.

## Gates before any separate entry decision

Current preparation status: the scope and eight prose templates are proposed; a schema-only legality, within-stratum uniqueness, and fixture-prefix check passed. An expanded primary-reference collision map, proposed input/verifier/evidence contract, structural coverage arithmetic, and five-round non-research software probe are recorded below. Independent design review, a systematic citation-chain/database-index search, review of the input/evidence contract and feasibility limits, source freeze, and any entry decision remain outstanding.

1. Review the question and the two-stratum comparison rule, including whether keeping both registered inquiry families remains justified.
2. Fix the finite construction templates, entity counts, state controls, public side information, and exclusion test against old fixtures.
3. The scoped primary-source collision map has been expanded through selected references; complete systematic citation-chain/database-index review and describe the finite contribution without overclaiming.
4. Independently review the proposed input schema, producer/verifier separation, coverage calculation, negative/conflict handling, and output inventory in this draft.
5. A five-round non-research software feasibility probe is recorded below. Independently review its limits and output-size implications; review the suspension-aware supervisor and child-process stop behavior before any recorded attempt.
6. Commit the reviewed protocol and inputs; bind hashes to that exact source state; perform the actual pre-execution review and receive a separate decision before any research run.

Until these gates are reviewed, this document remains a preparation draft only. Cycle 02 remains PUBLISHED; Cycle 03 remains unopened.
