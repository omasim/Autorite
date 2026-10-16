# Cycle 03 entry-review packet — finite lineage challenge

**Packet status:** ready for independent review; Cycle 03 remains unopened. No candidate corpus or answer-bearing challenge output is included.

## Exact material to review

Review the complete preparation draft at `research/preparation/FINITE_LINEAGE_CHALLENGE_DRAFT.md` with SHA-256:

`4d43c6175bd595a7abe2fd9dc2c24dc1ddfceec321050df46c3d53cecddfa0e7`

The review basis includes the payload-free RP004 structural export at SHA-256 `b448013d9f849f51af1bf026c9bf7b666bd5110a32aa28315c84c1e2819ff1ea`; the bounded producer `research/RP006/producer.py` at SHA-256 `ba00145e13666f6c134918f83cc8d0ff5f58e98c549b7a450f1f5e04b02eab84`; the independent verifier `research/RP006/verifier.py` at SHA-256 `68e102e0d58ed796d998b207bd105a4b93a7a95bf453a7ab44660d5c919042f4`; the capped writer and row-at-a-time sink `research/preparation/finite_lineage_writer.py` at SHA-256 `ad0917f34a09f00952ce9d3fba635d42de5d3e9fd5762b2bcc7eda0ed66b6f89`; the toy bounded integration `scripts/check-finite-lineage-bounded-pipeline.py` at SHA-256 `e34fea92b2c75c3e1e273a2110c498a03c33c6384c3bf4f946de98bb0ecbe719`; the maximum-row placeholder stream `scripts/check-finite-lineage-streaming-memory.py` at SHA-256 `fe14b6bee2f54816ab95eef233b7a727abef885b85bdebcaf3aff9a8a26dcdb1`; and the non-witness schema-shape check `scripts/check-finite-lineage-bounded-memory-shape.py` at SHA-256 `223642681751a8483dc4b3b32e0e57604fdbf65c55326412fc6f3dc785c7dec1`, plus earlier writer integration and memory-shape checks. The draft names the cited protocols, prior-art sources, author-side checks, and supplemental AI reviews. Do not treat those AI reviews as external approval.

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
