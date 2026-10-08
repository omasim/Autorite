# Autorite 2.0 — Codex Master Instructions v1.0
**Handoff:** 2026-10-07

## Mission
Turn Baseline v0.1 into a versioned, executable, publicly publishable living research system. Do not redesign the theory during bootstrap.

## Locked decisions
- Launch two separate websites from the beginning.
- `autorite.org` = public knowledge/publication.
- `autorite.net` = live research laboratory/network.
- GitHub = canonical research record.
- Sites are separate apps/deployments but consume shared canonical research data.
- Cycle 1 = RP002A, RP003, RP004, RP005A; DAM X archaeology parallel.
- No grand theory, new mathematics project, ARM redesign or production Research OS during bootstrap.
- Baseline v0.1 is immutable after freeze except explicit amendment.

- Autorite itself is an open-ended research program and never receives a terminal CLOSED status.
- Individual Cycles are finite, closable and publishable; every closed Cycle publishes results/synthesis and a frozen knowledge-state snapshot.
- Cycle completion is derived from research obligations, never elapsed time.
- Shared visual identity uses the selected Horizon mark.
- Both sites implement a shared Cycle Ring: Cycle number centered, outer ring filled by obligation completion; 100% means CLOSED.
- Horizon Logo and Cycle Ring must remain distinct components: Open Inquiry vs Finite Research Commitment.


## Repository
The authoritative baseline input is `baseline/`, selected by the user on 2026-10-07. Use its updated publishing and site architecture documents when older copies in `autorite-2-baseline-v0.1/` conflict. Preserve the older package as historical source material; do not treat it as a second canonical baseline. Source selection is separate from freeze approval.

Use one monorepo initially:
`baseline/`, `canonical/`, `cycles/`, `research/`, `graph/`, `legacy/`, `protocols/`, `publications/`, `apps/org/`, `apps/net/`, `packages/research-schema/`, `packages/content/`, `packages/ui-foundation/`, `scripts/`, `docs/`, `.github/`.

Do not split repositories unless a demonstrated deployment/security/ownership requirement appears.

## Canonical data
Canonical knowledge lives in Git as Markdown/frontmatter + structured research objects. A Claim has one ID/record. Both sites may project it differently. Site-local scientific assertions must reference canonical IDs. Archive material is never silently rewritten.

## Bootstrap order
A. Repository and exact, checksum-recorded baseline snapshot; release approval remains pending.
B. v0.1 research schema.
C. RP002A/RP003/RP004/RP005A skeletons; never fabricate results.
D. DAM X folder/template only until source material is supplied.
E. Build two independent sites from shared data.
F. CI/CD validation and independent deployment.
G. Audit, obtain explicit bootstrap/freeze approval, then tag `baseline-v0.1`. Do not execute RP002A before bootstrap approval.

## Constraints
Implementation clarifications are recorded in `RESEARCH_DATA_CONTRACT.md`, `CYCLE_GOVERNANCE.md` and `RESEARCH_EXECUTION_READINESS.md`. They do not amend baseline scientific definitions or authorize research execution.

Prefer simple inspectable technology. No graph database/CMS as canonical store in v0.1. No automatic claim generation, graph inference or status promotion. Never overwrite runs; invalidate/supersede. Preserve IDs across title changes.

## Bootstrap Definition of Done
Baseline frozen; living canonical docs present; schema passes; Cycle 1 skeletons exist; both sites build independently from shared records; cross-site links correct; CI passes; deployment/runbooks exist; bootstrap audit lists every deviation.

## Stop and ask
Stop if implementation requires changing frozen scientific definitions, a baseline contradiction prevents faithful implementation, secrets are required, a second canonical store would be created, or a new object/status/relation is necessary for correctness.
