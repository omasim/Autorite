# Finite lineage challenge — AI design review 001

Date: 2026-10-16. Reviewer: OpenAI GPT-6 Sol, a separate AI review agent. This is an AI assessment, not a human external expert review or Cycle 03 entry approval.

## Reviewed material and limits

- Draft: `research/preparation/FINITE_LINEAGE_CHALLENGE_DRAFT.md`, SHA-256 `bdf198bc95ec49dbcd720bfa156cf050c7d3c459484c0ded9cc616cfd3f91136`.
- Construction semantics excerpt, with only the question and construction/merge sections: SHA-256 `44b22c907990094983f1a11dab7f087524cfc519379f204d91c18a682fc31138`.
- Payload-free RP004 structure export v2: SHA-256 `b448013d9f849f51af1bf026c9bf7b666bd5110a32aa28315c84c1e2819ff1ea`.

The reviewer did not open the original fixture, original RP004 protocol, RP006 code/evidence, or outcome files, and generated no cases or answers. A prior AI review attempt had read control-bearing prose in the operational protocol and was stopped; none of that attempt's findings were used.

## Findings

**Decision value.** The challenge can change a corpus-specific representation decision if that decision is declared before execution. A same-projection/different-answer pair rejects the mask for that inquiry on any corpus containing the pair; no conflicts support only the declared 55 cases. `FULL` is justified when `birth_kind` and `alive` are needed. `TOPOLOGY_STATE`, a subset of `FULL`, has separate value only if a real downstream use excludes those two queries and could retain fewer fields. The draft must specify that use and the decision made under each possible result before outcomes.

**Construction and state sensitivity.** All eight event sequences are legal under the supplied semantics: live inputs, fresh outputs, arity, consumption, and copy/fork state preservation hold. Final live sets are F4-01 `{a,c,d}`, F4-02 `{c,d}`, F4-03 `{a,d}`, F4-04 `{b,c,d}`, F5-01 `{d,e}`, F5-02 `{d,e}`, F5-03 `{a,e}`, and F5-04 `{c,e}`. The illustrative vectors include repeated and distinct states but do not establish coverage. The forced-equality component counts are `3,2,3,3,3,3,4,4`; partitions into at most three blocks produce `5,2,5,5,5,5,14,14`, totaling 17 F4 and 38 F5 variants. Canonical `A/B/C` assignment must be fixed across cases: arbitrary per-case renaming can change cross-case `S` projection equality even when within-case `same_state` is unchanged.

**Structural overlaps.** `D` below means a parent-closed three-node parent-DAG match after ID relabeling. `L` also matches birth-operation labels and fork-sibling relation, but ignores independent event order. Blank cells have no match.

| Candidate | G0 | G1 | G2 | G3 | G4 | C4 |
| --- | --- | --- | --- | --- | --- | --- |
| F4-01 | D `{a,b,c}` |  |  |  |  | D `{a,b,d}` |
| F4-02 | D `{a,b,c}`, `{a,b,d}` |  |  |  |  |  |
| F4-03 |  |  |  |  |  | D `{a,b,c}` |
| F4-04 |  |  |  |  |  | D `{a,b,c}`; D+L `{a,b,d}` |
| F5-01 | D `{a,b,c}`, `{a,b,d}` |  |  |  |  |  |
| F5-02 |  | D `{a,c,d}` | D+L `{a,c,d}` |  |  | D `{a,b,c}`, `{a,b,d}` |
| F5-03 |  |  |  |  |  | D `{a,b,c}`; D+L `{a,c,d}` |
| F5-04 | D `{b,c,d}` |  |  |  |  | D+L `{a,b,c}` |

The draft's “operation-closed” term is incorrect: parent closure does not include every output of a fork. F4-02 and F5-01's G0 triples and F5-02's C4 triples omit a fork sibling and are not replayable three-entity sublogs. A corrected report should distinguish parent-closed DAG matches, event-labelled matches, event-complete replayable sublogs, and strict ordered event subsequences/prefixes. A local merge neighborhood resembles G4 when ancestry before the merge inputs is ignored, but is not a parent-closed G4 triple.

The sanitized C4 events are `root(a); root(b); continue(a→c)`. F5-04 begins `root(a); root(b); continue(b→c)`. Swapping roots makes the structures event-labelled isomorphic, but maps the chronology to `root(b); root(a); continue(a→c)`, so this is not a strict ordered prefix. It is a structural extension only if independent roots may commute. F4-04's `{a,b,d}` contains an ordered C4 subsequence with an interposed copy event; it is not a contiguous prefix. The reviewer could not check old-versus-new state-equality-pattern overlap because the v2 structure export contains no state values.

**Protocol and arithmetic.** Counts are correct: `17×60 + 38×90 = 4,440` `FULL` truth rows; `55×8 = 440` projections; `8×(C(17,2)+C(38,2)) = 6,712` pair/mask records; and `2×8×2 = 32` certificates. `TOPOLOGY_STATE` reuses its subset of `FULL` truth rows. Pair records need family-specific comparison status and findings because only projection equality is shared. A manifest cannot include its own hash; bind its hash through a separate receipt. The current toy probe does not bound challenge output volume, conflict-witness volume, disk behavior, or suspension/runaway-worker handling. Before a recorded run, define explicit output limits and partial-output handling; review a no-answer synthetic output-shape stress test, external suspension-aware supervisor, and process-group termination/reaping. The verifier should independently implement parsing, semantic reconstruction, enumeration, projection checks, and certificate validation; preserve disagreements.

**Prior-art boundary.** The draft's description of view determinacy and selected-information preservation as established work is defensible as written. The narrow possible contribution is an auditable finite benchmark for fixed lineage queries, aligned IDs, whole-field masks, and predeclared equality variants. It is not a new determinacy concept. The reviewer did not open cited papers or conduct another search; citation accuracy/completeness and exact benchmark overlap remain unresolved.

## Disposition

**Revise and return.** Fix the overlap terminology/criteria, predeclare the two use profiles and family-retention rule, make cross-case canonical state labels explicit, define family-specific pair outcomes and manifest hash binding, and close the output/resource/supervisor limits. Then submit the corrected exact bytes to another independent review before any separate entry decision. This review does not authorize Cycle 03, a source freeze, package/Test registration, resource allocation, or execution.
