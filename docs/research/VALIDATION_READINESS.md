# Research record validation — 2026-10-08

## Current pipeline disposition — 2026-10-10

The separately authorized second confirmation `confirmatory-20261010-002` completed: **60 units, 120 learned fits, 20 replicates per world**. All 484 output hashes and data/checkpoint/analysis replay passed. Seven frozen conditional decisions: **two benefit, four equivalent, one indeterminate**; no predeclared trace warning. Test TST-RP002A002 has audited Result R-RP002A002 (VALID). See `research/RP002A/CONFIRMATORY_002_REPORT.md` and the preserved timing/host review.

Civil elapsed time was 12297.895 seconds (3h 24m 58s), including lid-triggered host sleep; monotonic elapsed was 6426.015 seconds. Both stayed below the 14400-second allowance. The first attempt remains INCOMPLETE and unchanged. No samples/checkpoints or primary results were pooled; no further run is authorized. These decisions concern the fixed algorithms and generator settings under independence/normal-theory assumptions and fixture-specific .01-nat margins. No recurrence necessity, broad Claim or Cycle closure follows. RP002A and Cycle 01 remain ACTIVE; 0/13 obligations resolved.

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

## Longer-budget disposition — 2026-10-09

`research/RP002A/CONVERGENCE_002_REPORT.md` records the separately approved fresh-seed stage: 40 fits completed in 383.749 seconds and 322 outputs replay successfully. Twelve near-cap warnings remain despite no late-improvement flags; settled optimization is not established. No further execution or confirmatory Claim promotion is authorized.

## Target-size feasibility disposition — 2026-10-09

The separately approved pilot `budget-transfer-20261009-001` completed once: three units, six fits, 348.175 seconds, about 251.42 MiB lifetime peak process resident memory. No predeclared warning was triggered; this is not convergence proof. One training replicate per world supplies no variance or inferential conclusion. The full review is `research/RP002A/BUDGET_TRANSFER_REPORT.md`. Prior warnings remain on record; confirmation is PLANNED and Cycle 01 remains 0/13. No further execution is authorized.

## Uncertainty design follow-up — 2026-10-09

`research/RP002A/UNCERTAINTY_DESIGN_REVIEW.md` audits the current nested resampling variance and extreme-tail bootstrap resolution, with deterministic precision/resource sensitivity. Target-size variance, analysis coverage and substantive margins remain open. No final sample count or interval is chosen; no new training, Claim or Cycle resolution. The historical numerical proposal remains unchanged.
