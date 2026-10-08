# 07 — Research Graph Spec v0.1
Purpose: reconstruct current knowledge, provenance, revisions and unresolved alternatives.

MVP objects: Question, Claim, Assumption, ResearchPackage, Test, Result, Decision, Source.

Relations: tests, supports, challenges, depends_on, derived_from, supersedes, informs, inspired_by. No automatic transitive inference in v0.1.

Statuses: Question OPEN/ACTIVE/PARTIALLY_RESOLVED/RESOLVED/REFORMULATED; Empirical Claim PROPOSED/SUPPORTED/FALSIFIED/INDETERMINATE; Formal Claim CONJECTURED/PROVED/DISPROVED; Result VALID/INVALIDATED; Package PLANNED/ACTIVE/BLOCKED/CLOSED; Decision ACTIVE/SUPERSEDED/REOPENED.

Required queries: current claim status; provenance; revision reason; historical status; impacted dependents; publication provenance; unresolved alternatives.

Cycle 1 storage: Markdown + structured frontmatter. Working / Canonical / Archive layers. Canonical does not mean true.

## Program/Cycle status rule
The Autorite program has no terminal CLOSED status. Cycle records use PLANNED / OPEN / ACTIVE / REVIEW / CLOSED / PUBLISHED. ResearchPackage status remains PLANNED / ACTIVE / BLOCKED / CLOSED.
