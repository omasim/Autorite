# RP006 — Query-relative lineage field-ablation protocol v0.1

Date: 2026-10-12. Entry design accepted for preparation under D-0013, following Cycle 01's published close and D-0011's Transition Record. RP006 is PLANNED in OPEN Cycle 02. This protocol specifies a future deterministic audit; it records no new outcome and authorizes no run.

## Question and disclosed subject

Within the declared finite class, which whole R3 fields are sufficient to answer the full lineage inquiry family, and which are sufficient for its topology/state subset? Find every inclusion-minimal sufficient mask for each family, rather than calling the entire R3 representation minimal.

Reuse the six RP004 constructions G0/G1/G2/G3/G4/C4 with the common opaque handles a,b,c and state A. `DOMAIN.json` contains only case identifiers and original ordered events, with the source fixture path/hash. The recorded RP004 results, decoder behavior and collision witnesses are already known. This is an explanatory extension of designed examples, not an independent confirmation, blinded study, sampled population or estimate of prevalence. Case identifiers locate saved artifacts but are never part of a projected representation.

Keep the exact RP004 synthetic semantics: fresh immutable-state entities; root creates one entity; continue consumes one input; copy preserves a live input and creates one equal-state output; fork consumes one input and creates two equal-state outputs; merge consumes two distinct live inputs and declares both parents of one supplied-state output. Inputs must exist and be live. Parent order is immaterial; ancestry is strict; root sets include an independent root itself. No physical/biological identity, content attribution or preferred original is introduced.

## Two inquiry families

| Family | Queries and exact answer types | Prospective finite coverage |
| --- | --- | --- |
| FULL | same_state(x,y): bool; ancestor(x,y): bool; shared_root(x,y): bool; parents(x): sorted list of handles; birth_kind(x): root/continue/copy/fork/merge; alive(x): bool | All ordered binary pairs including self, and every unary handle: 36 queries/case, 216 truth rows |
| TOPOLOGY_STATE | The first four queries above, with identical arguments and semantics | 30 queries/case, 180 truth rows, shared with FULL |

Use the fixed query-kind order above, then lexical argument tuples over the declared common universe. Reject unknown query names, wrong arities, unknown handles and type-coerced answers. False, an empty parent list and an omitted field are distinct. Feasibility uses exact complete truth vectors, not a conservative decoder's UNKNOWN count. A future decoder abstention is not an impossibility certificate.

## Eight masks and side information

There are three indivisible fields, in bit order S/P/K: complete handle-to-state map; complete handle-to-parent-set map (including roots with empty sets); complete handle-to-birth-kind map. Inspect masks 000,001,010,011,100,101,110,111, using exactly the same mask for all constructions and entities. A bit keeps or entirely omits its map. An omitted field must not be filled with false, an empty map or a guessed value. Partial parent sets, inferred fields, selected per-case masks and a one-parent R1 encoding are outside this class.

The only shared side information is the common aligned entity universe, query definitions, mask definition and the declared finite domain/semantics. A projection contains the sorted common `entities` array and a `fields` object with only retained maps. Canonical map keys and complete parent lists are sorted. Compare canonical JSON values/bytes with exact types; a digest may index them but cannot replace an equality check. Mask/case/family labels are outer artifact metadata; a mask is constant across cases and adds no case-dependent information.

Do not encode case names, event order, expected-answer caches, final live sets, fixture hashes or identifiers disguised as payloads. The known finite domain can justify a finite lookup certificate, but no case label may select its answer. The domain's equal payloads are deliberately disclosed: this limits state-field conclusions and provides no varying-state test.

## Feasibility and minimality criterion

For a family F, let T_F(c) be its complete exact truth vector and P_m(c) the declared projection. A mask is sufficient **on this finite corpus** exactly when P_m(c)=P_m(d) implies T_F(c)=T_F(d) for every case pair. A conflicting aligned query certifies infeasibility on any domain containing that pair. With no conflict, assign the common truth vector to each projection class: this constructs a finite lookup function on observed projections only. It does not specify behavior on unseen projections or prove adequacy on all admissible constructions.

This equality/functional-determination criterion uses existing mathematics, not a proposed new theorem or formal deficit. Its overlap with database dependencies is reviewed separately. Sufficient masks are inclusion-minimal only if none of their proper submasks is sufficient for that same family. Report every incomparable minimal mask. Field count is not byte/bit cost or global representation optimality. Adding a retained field refines a projection partition; use monotonicity as a consistency control, not independent evidence.

## Complete future artifact inventory

Generate six construction truth vectors, 48 mask/case projections, and both family classifications for all eight masks. Save all 120 unordered case-pair/mask comparisons (15 pairs times eight masks), including unequal projections. For equal projections, examine all aligned queries: the prospective maxima are 4,320 FULL and 3,600 TOPOLOGY_STATE pair/query checks; actual equality-gated counts are future outputs, not fixed results.

Save truth rows, projections, pair comparisons, every conflicting aligned query with both exact answers, partition membership keyed by projection value, conflict-free certificates, all sixteen family/mask verdicts, all inclusion-minimal masks and their proper-submask witnesses. Save a summary, resource/timing record, independent replay report and output hashes in a unique immutable run directory. Case IDs are for traceability outside representations. No witness, negative mask, duplicate truth vector or incomparable minimal mask may be omitted from denominators or reporting.

## Controls and independent verification

Use RP004's already disclosed state-only G0/G3 ancestor conflict and complete-parent/no-kind G1/G2 operation/availability conflict. Full S/P/K must reproduce the known R3 behavior for the same inquiries. G4/C4 complete parent sets differ: this catches accidental one-parent collapse but is not an R1 member of the new class. These are known engineering controls, not new discoveries.

Add malformed input/query/type tests, omitted-versus-empty-field checks, forbidden side-channel fields, full parent preservation, shared global opaque renaming across all cases, parent-order invariance and mask uniformity. Renaming changes serialized labels consistently while preserving partition/conflict/minimal-mask structure. Production and verifier must reconstruct ground truth from event logs independently; neither reads the fixture's old expected answers or the other's truth/ancestry/projection code. A verifier must independently recompute all projections, pair/query comparisons, certificates and masks, not just match totals. Software mutation tests must detect changed truth, missing rows/witnesses, hidden identifiers and corrupted certificates.

## Resource, source and execution gates

The future audit is one deterministic, standard-library, single-process attempt on Python 3.11+, without training, seeds or network access. Proposed ceiling: 60 monotonic seconds and 128 MiB peak process RSS. Before freezing, establish a reviewed feasibility preflight and a real process-memory measurement contract, including platform units and child-process policy. Monotonic runtime and civil elapsed time are recorded separately. A host-suspension incident cannot silently satisfy the gate merely because monotonic time stopped; a reviewed suspension-aware external deadline/stop policy is required before launch.

Before any recorded run: implement producer/verifier and controls; complete the methods/collision and forward/backward graph/source review; bind exact code, tests, protocol, domain and plan hashes to a committed source freeze; review resources and stopping behavior; register the Test with its fixed inputs; accept the actual pre-execution checkpoint/Decision. Entry acceptance alone does not fulfill that checkpoint or activate a run. The prepared `ENTRY_PLAN.json` keeps source_frozen and execution_authorized false; later execution uses its own reviewed freeze and authorization record.

Stop on malformed input, provenance mismatch, missing coverage, unsound truth/types, replay disagreement, source/side-information violation or a resource/deadline breach. Preserve an INCOMPLETE attempt and its failure artifacts, without a VALID Result. Investigate a discrepancy under a new reviewed correction and attempt authorization; do not overwrite or selectively retry. A change to domain, masks, families, side information or limits needs a separate scope review before producing outcomes.

## Disposition boundaries

The audit may resolve a finite RP006 commitment after its complete replay and explicit package review. It does not resolve Q-3/Q-4, establish whole-history necessity, reduce Q-4 to Q-3, grant novelty, validate DAM X, or establish open-world/byte-optimal sufficiency. All old Results and the immutable Cycle 01 snapshot remain preserved. A future source discovery or material error receives a new Decision rather than rewriting this dated entry.

[Cycle 02 entry](https://autorite.net/sources/cycle02-entry-review/) · [Prior-art review](https://autorite.net/sources/rp006-prior-art/) · [RP004 protocol](https://autorite.net/sources/rp004-operational-protocol/) · [Accepted transition](https://autorite.net/sources/cycle01-transition/)
