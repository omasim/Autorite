# RP003 — Prior-art collision review

Reviewed 2026-10-11 as part of protocol preparation. This is a targeted collision check, not an exhaustive literature review. No novelty Claim is made.

## Tolerance is not equivalence

Alain Connes and Walter D. van Suijlekom, *Tolerance relations and operator systems*, arXiv:2111.02903v1 (2021). [Primary source and abstract](https://arxiv.org/abs/2111.02903v1).

Inspection: title, authors, version metadata and abstract. The abstract discusses metric tolerance and the information lost when replacing a tolerance relation with an associated equivalence relation. RP003 uses an inclusive rational-coordinate threshold; that convention is specified independently. We have not reviewed the operator-system construction and do not import its results into this protocol.

Collision: treating small pairwise differences as equivalent and then composing them is already a recognized issue. RP003 must keep the tolerance relation and transitive exact-feature control separate. A monotonic-drift witness is illustrative calibration, not a novel theorem.

## A whole-path condition needs its own statement

Leslie Lamport, *Proving Safety Properties*, 18 May 2019, minor correction 16 July 2019. [Author-hosted primary note](https://lamport.org/tla/proving-safety.pdf).

Inspection: introduction and section 4.2, PDF pages 4 and 9–10 (printed pages 1 and 6–7). The note defines invariance over states of allowed behaviors and presents the initial-state and next-step obligations for an inductive invariant. The complete note and proof-system implementation have not been audited here.

Collision: induction from an initial condition and preserved invariant is standard. RP003's reference-to-start prefix judgment is distinct from an adjacent-pair tolerance test. Its elementary finite-path arguments are mathematical background, not newly established theory. The planned Python audit is neither TLC model checking nor a TLAPS proof.

## Scope of the proposed work

The operational supplement separates exact-feature equality, metric tolerance, endpoint displacement, prefix excursion and accumulated variation. The fixed examples make these distinctions explicit in PC01 terms. Planned finite enumeration can verify saved witnesses and count failures in its declared domain. It cannot certify an arbitrary relation or all real-world paths. Further work should examine alternative predicates and provenance-sensitive transformations only under a separately specified protocol.

No source establishes Autorite's broad conceptual program. No resemblance to this literature licenses a metaphysical identity theory or a unification claim. Review of the present two-source selection leaves wider related work open.
