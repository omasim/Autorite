# RP004 — Targeted prior-art collision review

2026-10-11. Preparation review for the operational branching protocol. This is a bounded inspection of primary documentation, not a systematic literature review, novelty certification or standards-conformance assessment.

## Inspected sources

The W3C PROV-DM Recommendation, sections 5.1.8 and 5.2.1–5.2.3, distinguishes entity availability, derivation and more specific revision/quotation relations. Derivation can carry details about activities, use and generation. RP004's parent edges and operation labels therefore overlap established provenance machinery. Copy, fork and merge here are local synthetic construction rules, not asserted PROV subtypes. [PROV-DM](https://www.w3.org/TR/prov-dm/).

The W3C PROV-O Recommendation, sections 3.1 and 3.3, Example 11 and the entries for wasDerivedFrom and qualifiedDerivation, separates a binary entity derivation from a more detailed account of its activity and generation/use. This is relevant to comparing a complete untyped DAG with a graph carrying additional distinctions. RP004 retains birth kinds rather than implementing RDF/OWL qualified derivations. The documentation does not establish the particular sufficiency claims of this finite inquiry family. [PROV-O](https://www.w3.org/TR/prov-o/).

The official Git glossary entries “commit object,” “commit graph concept, representations and usage” and “DAG” describe parent-linked historical structure alongside a tree snapshot. RP004's separation of content state and parent structure is consequently familiar rather than a new discovery. Its consumption rule and copy/fork types are synthetic and are not Git commit semantics. [Git glossary](https://git-scm.com/docs/gitglossary).

## Collision assessment and interpretation

Parent DAGs, typed provenance, multiple inputs and the distinction between snapshot content and derivation have clear prior art in these inspected sources. A copy does not become an independent root solely because its payload matches another entity; conversely, payload equality is not a derivation record. The protocol tests recoverability of a declared query family after deliberate information removal. It attaches no novelty claim to the examples or to ordinary DAG reachability.

Our inference from this inspection is that a useful contribution at this stage is a precise, reproducible separation of query contracts and representation collapse in the Autorite research record. This is not evidence for an original ontology or a general identity theory. Neither PROV source prescribes this toy lifecycle policy, and R3 sufficiency is only for the declared six queries and controlled universe. A same-projection collision certificate establishes a finite-domain obstruction, not the minimality of a whole representation.

## Search limits and review boundary

Only the listed official documents and sections were inspected on 2026-10-11. No broad database-provenance, branching-time, distributed versioning, philosophy-of-identity or biological-lineage survey was completed. No theorem-equivalence search or external scientific review was performed. Any later novelty claim must expand that collision review before being promoted. The frozen baseline remains unchanged.

Read the [operational protocol](https://autorite.net/sources/rp004-operational-protocol/).
