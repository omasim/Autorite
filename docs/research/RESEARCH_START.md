# Research start — 2026-10-08

The user requested that research begin after the public sites were ready, and that both websites and GitHub remain current. This authorizes preparation and investigation; it is not an audited baseline release or a completed experimental preregistration.

## Work begun

RP002A is the first workstream. Its initial prior-art review is recorded in `research/RP002A/PRIOR_ART_REVIEW.md`; the proposed operational design is in `research/RP002A/PROTOCOL_DRAFT.md`. No experiment, result, supported claim or resolved Cycle obligation is created by that review.

## Current gaps

- The canonical Git repository is [omasim/Autorite](https://github.com/omasim/Autorite). Its initial import contains research sources and publication generators; the two Sites repositories remain generated output.
- The 20 selected baseline source files are preserved byte-for-byte in `baseline/v0.1/` with `baseline/SNAPSHOT.json`. A checksum check is implemented; the audited release was approved and tagged `baseline-v0.1`.
- The research-object validator, Cycle 01 manifest and 15 typed records are implemented. Bootstrap audit and release approval are recorded in `docs/research/BOOTSTRAP_APPROVAL.json`.
- RP002A's full collision assessment and operational protocol choices remain open.
- DAM X still requires supplied source material.

## Publication workflow

GitHub will hold one canonical repository for source documents, protocols, code, immutable runs, evidence and decisions. Substantive changes follow issue/decision → branch → PR → checks → explicit review → merge. Sites are generated from the merged canonical state and published together. Generated Sites repositories do not become scientific authorities.

Every meaningful research update should state what changed, its evidence and scope, whether it is exploratory or confirmatory, and which public pages are affected. A successful build cannot promote a scientific claim. Runs receive unique directories and preserved manifests/checksums; corrections never overwrite original runs.

## Immediate sequence

1. Keep the connected GitHub repository and preserved baseline under version control.
2. Implement canonical records, validation and CI; audit bootstrap before requesting a release approval.
3. Complete RP002A's collision review and protocol supplement, including justified operational parameters.
4. Freeze the approved confirmatory protocol before observing its outcomes.
5. Execute, retain artifacts, review results and publish traceable updates to both sites.

RP003 follows RP002A preparation. RP004/RP005A and DAM X retain the baseline ordering and dependencies. Cycle progress remains based on evidence-backed obligation resolutions, not the fact that work has started.

## First exploratory pilot

`research/RP002A/PILOT_001_REPORT.md` records the completed isolated engineering pilot and raw artifacts. No scientific Claim or Cycle obligation was resolved. Further runs require a separate reviewed plan; confirmatory preparation remains open.

## Convergence-stage disposition — 2026-10-09

`research/RP002A/CONVERGENCE_001_REPORT.md` documents the separately approved 20-unit exploratory stage. All 40 fits completed and artifact/checkpoint replay passed; many fits still improved near the 50-epoch cap. Settled optimization and confirmatory readiness are not established. No additional run or scientific Claim promotion is authorized.

## Longer-budget disposition — 2026-10-09

`research/RP002A/CONVERGENCE_002_REPORT.md` records the separately approved fresh-seed stage: 40 fits completed in 383.749 seconds and 322 outputs replay successfully. Twelve near-cap warnings remain despite no late-improvement flags; settled optimization is not established. No further execution or confirmatory Claim promotion is authorized.
