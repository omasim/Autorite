# Research record validation — 2026-10-08

The canonical research core now contains six Questions, four PLANNED ResearchPackages, three existing Decision indexes and two Source records. Cycle 01 is represented by one manifest with 13 equal-weight, unresolved obligations. There are no Claims, Tests or Results in the live research graph.

The validator checks schema keys, type/status compatibility, unique IDs and aliases, dates, graph/file references, relation endpoints and supersession cycles. Supported/proved claim projections require justification and valid evidence or proof artifacts. Result/Test package agreement, output checksums and committed run immutability are checked. Cycle closure requires the full ring, final close bundle, active close Decision and an existing Git snapshot; publication requires publication references.

Both site generators validate these records before publication and derive their Cycle data from the same manifest. Question statuses and package titles/statuses use the typed records. Editorial summaries remain publication metadata; they cannot promote epistemic status.

Thirteen tests cover valid source, unknown fields/references, forbidden statuses, alias shadowing, unsafe paths, duplicate YAML keys, premature full-ring state, tampered run checksums, invalidated sole support Result/Test package mismatch, supersession cycles and committed run-manifest mutation. Synthetic evidence fixtures exist only in temporary test directories and are never research results.

## Run locally

```sh
python3 -m pip install -r scripts/requirements-sites.txt
python3 scripts/check-baseline.py
python3 packages/research-schema/validate.py
python3 -m unittest discover -s tests
python3 scripts/build-sites.py
python3 scripts/check-sites.py
```

## Remaining execution gates

Structural validation is implemented; the audited bootstrap and baseline freeze were approved. RP002A has a numerical configuration proposal, but its collision assessment, power/effect rationale, full collision/power review, approved reproducibility environment and pre-outcome freeze are incomplete. No experiment is run by a validator or a passing CI job.

## Executable RP002A preparation

The generator, reference, model and pilot harness now have engineering acceptance checks; the complete suite has 30 tests. The separate pilot proposal and execution gates are documented in `research/RP002A/EXECUTION_READINESS.md`. No research run has occurred.

## First exploratory pilot

`research/RP002A/PILOT_001_REPORT.md` records the completed isolated engineering pilot and raw artifacts. No scientific Claim or Cycle obligation was resolved. Further runs require a separate reviewed plan; confirmatory preparation remains open.

## Convergence-stage disposition — 2026-10-09

`research/RP002A/CONVERGENCE_001_REPORT.md` documents the separately approved 20-unit exploratory stage. All 40 fits completed and artifact/checkpoint replay passed; many fits still improved near the 50-epoch cap. Settled optimization and confirmatory readiness are not established. No additional run or scientific Claim promotion is authorized.
