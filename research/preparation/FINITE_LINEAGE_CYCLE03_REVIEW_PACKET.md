# Cycle 03 entry-review packet — finite lineage challenge

**Packet status:** ready for independent review; Cycle 03 remains unopened. No candidate corpus or answer-bearing challenge output is included.

**Review boundary:** the designated review basis is this packet and the accompanying bundle, together with the exact files and hashes listed below. The bundle includes `research/preparation/FINITE_LINEAGE_RP004_SEMANTICS_EXCERPT_2026-10-16.md` (SHA-256 `44b22c907990094983f1a11dab7f087524cfc519379f204d91c18a682fc31138`), containing only the question and construction/merge semantics. It excludes the full RP004 and RP006 operational protocols because they disclose legacy control answers and outcomes. Do not consult those outcome-bearing protocols, fixture files, or prior answer artifacts for this control-blind design review; disclose and stop if such material is encountered. The excerpt contains no fixture cases or expected answers.

## Exact material to review

Review the complete preparation draft at `research/preparation/FINITE_LINEAGE_CHALLENGE_DRAFT.md` with SHA-256:

`973ed516dc3e495002fea4ff320d2d8b084d2271112217c42aa8226e3fb66db7`

The review basis includes the payload-free RP004 structural export at SHA-256 `b448013d9f849f51af1bf026c9bf7b666bd5110a32aa28315c84c1e2819ff1ea`; the bounded producer `research/RP006/producer.py` at SHA-256 `899d6b3b0e70c6b4af420fdd19b9043e790547b92caac2376586da0e27ce8868`; the independent verifier `research/RP006/verifier.py` at SHA-256 `9422bb99adfd45b3ab192d4750e3965b6de2569207e8b16bfc5336bb0c714a9e`; the capped writer and row-at-a-time sink `research/preparation/finite_lineage_writer.py` at SHA-256 `e6b1d82134bba57b2d725ad4e2b12da5d381da4ac03690acaa54731f1fbae865`; the toy bounded integration `scripts/check-finite-lineage-bounded-pipeline.py` at SHA-256 `321dfe89dcbc034f669295264c3b495266646c366ed412c72de779e8dc9f6732`; the maximum-row placeholder stream `scripts/check-finite-lineage-streaming-memory.py` at SHA-256 `fe14b6bee2f54816ab95eef233b7a727abef885b85bdebcaf3aff9a8a26dcdb1`; and the non-witness schema-shape check `scripts/check-finite-lineage-bounded-memory-shape.py` at SHA-256 `223642681751a8483dc4b3b32e0e57604fdbf65c55326412fc6f3dc785c7dec1`, plus earlier writer integration and memory-shape checks. The draft names the cited protocols, prior-art sources, author-side checks, and supplemental AI reviews. Do not treat those AI reviews as external approval. The supported-runtime, answer-free revalidation record is `research/preparation/FINITE_LINEAGE_REVALIDATION_2026-10-16.md` (SHA-256 `47574479d6d9572395b5bf614abc35f93c814dbd64d8d5ae0d4c9c44e5272ed5`); it records a sequential rerun under Python 3.12.13 and the exact remaining scope limits.

## Requested disposition

Assess the exact draft bytes above and return one disposition: **proceed to a separate entry decision**, **revise and return**, or **defer/decline**. Address each question with concise evidence:

1. Does the finite challenge have a concrete decision value beyond testing software? Are `FULL` and `TOPOLOGY_STATE` both tied to real, distinct uses?
2. Are all eight proposed event templates legal under RP004 semantics, and are the three-value state bound and cross-case `A/B/C` alignment defensible?
3. Are the D/L/R/O overlap definitions, reported motif reuse, and exclusion rule suitable for the stated transfer question?
4. Is the selective prior-art review sufficient to decide whether to proceed, and what limits must remain on contribution or novelty language?
5. Are the denominators, independent-truth plan, producer/verifier separation, output contract, resource ceilings, and failure controls adequate for a later separately authorized run? Review the bounded conflict-stream path and toy supervised test. A placeholder list reached 900,333,568 and 882,343,936 bytes for 1,077,936 rows, while a capped streaming placeholder writer emitted the same row count at 14,516,224 bytes worker RSS. Schema-shaped placeholders for the 55-case non-witness inventories measured 26,116,096 bytes but did not execute either implementation. The opt-in bounded producer and independent verifier passed on two toy cases; the complete 55-case producer/verifier/writer and full process-tree peak have not been measured. Decide whether this bounded path and its remaining controls are adequate before entry, or whether further implementation/resource evidence is required; also identify host-level checks.

Do not generate candidate inputs or query outcomes, inspect answer-bearing outputs, tune templates from outcomes, freeze sources or inputs, register a Test/package, or authorize execution. A favorable review only permits a later, separate entry decision; it does not itself open Cycle 03.

## Provenance to complete

- Reviewer name and institution/organization:
- Review date:
- Independence/conflict disclosure:
- Exact draft SHA-256 reviewed:
- Exact supporting-file hashes reviewed:
- Materials or outcome-bearing files excluded from review:
- Disposition and evidence:
- Required revisions or remaining gates:

The reviewer has not yet been selected. This packet is prepared for a later, identifiable independent review and is not itself approval or an entry decision.

The assessment supplied earlier by the user is retained as AI feedback with unknown authoring system and unknown reviewed-byte hash. It is not an identifiable human/external review. The separate AI reports in this directory are supplemental implementation/design feedback only.
