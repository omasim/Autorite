# Autorite 2.0 — Codex Handoff v1

## Published sites
- [Knowledge & Publication](https://autorite.org)
- [Open Laboratory](https://autorite.net)

Both sites are public and in English. Their www hostnames also work over HTTPS. They share the preparation record in `canonical/site-state.json`; site publication does not approve baseline freeze or research execution.

Start with `CODEX_MASTER_INSTRUCTIONS.md`, then `FIRST_CODEX_PROMPT.txt`.

## Research repository
[omasim/Autorite](https://github.com/omasim/Autorite) holds the canonical source. Proposals use branches and PRs; CI verifies baseline checksums and both generated sites. The audited preserved baseline is approved and tagged `baseline-v0.1`. The first isolated engineering pilot completed; confirmatory protocol approval remains pending.

## Authoritative baseline source
Use `baseline/` as the authoritative bootstrap source, as confirmed by the user on 2026-10-07. Its updated publishing and site architecture documents (v0.2) take precedence over the older copies in `autorite-2-baseline-v0.1/`.

`autorite-2-baseline-v0.1/` is a historical input package, not a second canonical source. Preserve it for provenance. This source selection does not itself approve a freeze or a release tag.

Implementation clarifications: [handoff decisions](HANDOFF_CLARIFICATIONS.md), [data contract](RESEARCH_DATA_CONTRACT.md), [Cycle governance](CYCLE_GOVERNANCE.md), and [research execution gates](RESEARCH_EXECUTION_READINESS.md).

This package contains:
- frozen Baseline v0.1 source documents;
- two-site product architecture;
- monorepo blueprint;
- research data contract;
- governance and CI/CD plan;
- implementation roadmap;
- first Codex execution prompt;
- Decision-0001 locking the two-site launch.

The handoff intentionally stops before RP002A execution and before DNS/secrets.

Additional locked decisions: open-ended program / closable Cycles, mandatory Cycle publications, Horizon identity, and shared obligation-based Cycle Ring.

## First exploratory pilot

`research/RP002A/PILOT_001_REPORT.md` records the completed isolated engineering pilot and raw artifacts. No scientific Claim or Cycle obligation was resolved. Further runs require a separate reviewed plan; confirmatory preparation remains open.

## Convergence-stage disposition — 2026-10-09

`research/RP002A/CONVERGENCE_001_REPORT.md` documents the separately approved 20-unit exploratory stage. All 40 fits completed and artifact/checkpoint replay passed; many fits still improved near the 50-epoch cap. Settled optimization and confirmatory readiness are not established. No additional run or scientific Claim promotion is authorized.

## Longer-budget disposition — 2026-10-09

`research/RP002A/CONVERGENCE_002_REPORT.md` records the separately approved fresh-seed stage: 40 fits completed in 383.749 seconds and 322 outputs replay successfully. Twelve near-cap warnings remain despite no late-improvement flags; settled optimization is not established. No further execution or confirmatory Claim promotion is authorized.

## Target-size feasibility disposition — 2026-10-09

The separately approved pilot `budget-transfer-20261009-001` completed once: three units, six fits, 348.175 seconds, about 251.42 MiB lifetime peak process resident memory. No predeclared warning was triggered; this is not convergence proof. One training replicate per world supplies no variance or inferential conclusion. The full review is `research/RP002A/BUDGET_TRANSFER_REPORT.md`. Prior warnings remain on record; confirmation is PLANNED and Cycle 01 remains 0/13. No further execution is authorized.
