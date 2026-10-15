# Finite lineage challenge — clean AI design re-review 002

Date: 2026-10-16. Reviewer: OpenAI GPT-6 Sol, the separate AI review agent used for the control-blind re-review. This is an AI design assessment, not a human expert review, Cycle 03 entry decision, source freeze, or execution authorization.

## Reviewed material and limits

- Exact draft reviewed: `research/preparation/FINITE_LINEAGE_CHALLENGE_DRAFT.md`, SHA-256 `6c0640af27b510c009ad66178f1eea72742c137c88a7a16c2fa9ab45eed4f9f3`.
- The review used the draft and previously approved sanitized construction-semantics excerpt and payload-free RP004 structure export. It did not inspect candidate inputs, candidate outputs, original control-bearing protocols, or run the challenge.
- The reviewer did not inspect or rerun the synthetic resource helper. Its reported PASS below is the local execution record, not an independently reproduced reviewer result.

## Disposition

**Pass for the requested AI design re-review.** The reviewer confirmed the corrected manifest/receipt boundary, family-specific pair findings, and resource-sizing wording. It verified the arithmetic stated in the draft: `1,088×(60+52) + 5,624×(90+80) = 1,077,936` as an inventory-derived upper bound, and `1,077,936×420 = 452,733,120` bytes. The review explicitly leaves complete evidence-package bounds, low-disk rejection, final-writer integration, supervisor behavior, process-group termination/reaping, and crash handling open. It does not authorize Cycle 03, a source freeze, or a run.

## Local answer-free resource check

The separately executed helper `scripts/check-finite-lineage-resource-shape.py` (SHA-256 `4f1edb978d4e87ff5128b6c74dd084d75ba59c62b791c79fc2bb15de518e967d`) passed on 2026-10-16. It wrote 1,077,936 synthetic placeholder rows at 420 bytes per row, verified the streamed and reread SHA-256 (`ed69ae4b52da22cb932595d79af11a2ba2e2bcb4e61591610a4143deba450fad`), and removed temporary output. It also accepted the exact 448-byte row boundary and rejected row-byte, row-count, file-byte, and total-evidence-byte overflows while preserving a partial file and an `INCOMPLETE` receipt. The run observed 251,052,199,936 free bytes and took 7.660 seconds. It read no candidate input and generated no candidate answer. The low-disk rejection path and integration with a final challenge writer were not tested.

The earlier resource review of draft `19ff9f01d4a910e79c52badbbada8ab004a16b9a60c4f0ddd2c27297872bf883` correctly identified that the then-stated 1,329,008 count did not follow the query inventory. The draft was revised to the 1,077,936 upper bound and the corrected synthetic helper was rerun before this final re-review.

## Bounded primary-source citation follow-up

The same reviewer then examined the factual descriptions in draft SHA-256 `bd84381eb654a7f93bc0f28e43ec41a44061b10dc39aa47e35a65aa4bef80620`. Disposition: **pass for this bounded citation check**. It found no material title, date, attribution, or description mismatch in the checked sources:

- [Nash, Segoufin and Vianu, *Views and Queries: Determinacy and Rewriting*](https://dbucsd.github.io/paperpdfs/2010_3.pdf) define determinacy through view information fixing query answers; [Fan, Geerts and Zheng](https://www.sciencedirect.com/science/article/pii/S0306437911001098) connect selected-information invertibility to view determinacy and analyze selection/projection subclasses.
- [Calvanese et al., *Lossless Regular Views*](https://www.inf.unibz.it/~calvanese/papers/calv-degi-lenz-vard-PODS-2002.pdf) study lossless regular-path views on labelled graphs; [Francis 2015](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ICDT.2015.44) and [Francis 2026](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ICDT.2026.22) study path-view determinacy and regular-path determinacy under walk-based semantics.
- [Fan et al. 2012](https://www.research.ed.ac.uk/en/publications/query-preserving-graph-compression/) preserve reachability and graph-pattern answers through query-relative compression. [Fan et al., *The VLDB Journal* 32 (2023)](https://link.springer.com/article/10.1007/s00778-022-00731-7) use query-class synopses and decontraction for exact answers; [their SIGMOD 2022 hierarchy](https://muyang.me/publication/Hier2022.pdf) iterates contractions. The journal article appeared online in 2022 and in the 2023 volume, so the draft's 2023 citation is valid.
- [Niazmand et al.](https://www.sciencedirect.com/science/article/pii/S2667096822000258) describe a query-based lossless RDF summary aimed at complete SPARQL answers.

The reviewer found the finite-corpus distinction suitably cautious and no obvious stronger exact collision in this bounded set. The check did not cover every peripheral provenance citation, conduct a systematic literature review, or establish novelty clearance. It is not entry approval.

## Local resource-control update after review

This is an author-side addendum, not part of the AI reviewer's findings. A focused follow-up flagged that certificates and input events must not be counted as single 448-byte rows. The helper and draft were corrected so the JSONL subtotal includes only conflict, truth, projection and pair rows (1,089,528 total); the two input documents, 32 full certificates and all other non-row artifacts are charged to the 64 MiB reserve. The resulting package ceiling is 555,217,408 bytes, below the proposed 640 MiB total cap. Current helper SHA-256: `17d3d2113a85713f348b1617fc04158096b3ede1c484d6ea7b58042f768f3d34`. The 2026-10-16 rerun passed: 1,077,936 synthetic rows at 420 bytes each, 452,733,120 total bytes, streamed/reread SHA-256 `ed69ae4b52da22cb932595d79af11a2ba2e2bcb4e61591610a4143deba450fad`, 260,255,723,520 observed free bytes, temporary files removed, no candidate inputs read and no candidate answers generated. Synthetic boundary controls accepted exactly 2 GiB and rejected one byte below; this does not simulate a genuinely low-disk host. The complete-package bound assumes the stated row counts and a future writer enforcing the 64 MiB non-row reserve; final-writer integration remains open. The focused reviewer reports no further helper-logic blocker within this bounded review, but exact current draft/helper verification remains subject to the reviewer’s final response.

## Focused clean review of the updated resource contract

On 2026-10-16 the same separate AI reviewer completed a focused answer-free review of the exact draft SHA-256 `745e1573e8fbcc09f41da3c13039638f2f5050372a2d70747b38bcb743f39cca`, helper SHA-256 `17d3d2113a85713f348b1617fc04158096b3ede1c484d6ea7b58042f768f3d34`, and this report before this section was appended (report SHA-256 `6420c7ea42eb92f893913b9457a2c1a2fd1add0b795053b3480487f75f11aa96`). Disposition: **pass for this focused design review**. The reviewer confirmed that only conflict/truth/projection/pair JSONL rows use the 448-byte ceiling; full certificates and the two input documents are included in the 64 MiB non-row reserve, yielding a correct 555,217,408-byte bound. It found the tested cap-rejection partial/`INCOMPLETE` behavior and 2 GiB threshold logic consistent with the proposal. The reviewer did not execute the helper. It noted untested OS-level creation failure, disk exhaustion while writing the receipt, crash/suspension behavior, and final-writer enforcement; these remain explicit open gates. This review is not Cycle 03 entry approval.
