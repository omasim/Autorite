# Handoff clarifications — 2026-10-07

The user selected the newer `baseline/` and requested completion of handoff gaps. This record documents implementation choices; it is not a freeze approval or research execution authorization.

- Source precedence: `baseline/` wins over the historical `autorite-2-baseline-v0.1/`; both remain intact.
- Freeze order: M0 preserves exact source bytes/checksums; M6 audit and explicit approval precede `baseline-v0.1`.
- Serialization: `RESEARCH_DATA_CONTRACT.md` defines required fields, references and edge direction. Baseline graph types/statuses/relations are retained; types without defined statuses omit that field.
- Cycles: existing baseline lifecycle is represented as governance manifests outside the graph object registry.
- Progress: Cycle 1 uses equal-weight declared obligations; explicit evidence/decisions resolve them. CLOSED and PUBLISHED retain 100%; the final close bundle prevents early 100% progress.
- Research readiness: `RESEARCH_EXECUTION_READINESS.md` specifies pre-execution completion gates without selecting unapproved scientific parameters.

The remaining work is implementation of M0–M1, subsequent site/build/CI milestones, completion of living preregistrations before research, supplied DAM X sources, and explicit release/execution approvals. This clarification pass does not claim those milestones are complete.
