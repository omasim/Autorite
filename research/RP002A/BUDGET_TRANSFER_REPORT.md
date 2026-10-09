# RP002A target-data-size feasibility review

Date: 2026-10-09. Run: `budget-transfer-20261009-001`. **Completed once; exploratory feasibility only.**

## Disposition

All three independent units and six learned-model fits completed in 348.175 seconds (5 minutes 48 seconds), within the separately authorized 3600-second allowance. Each unit used 4096 training, 1024 validation and 2048 assessment episodes of 129 observations. All fits stopped after 20 epochs without a new validation minimum. None triggered the predeclared near-cap, final-20 or secondary final-five warning. This records absence of these warnings at this setting; it does not prove convergence. The earlier stage's 12 warnings remain part of that immutable record.

There is one independently trained replicate per world. This pilot supplies no between-training SD, inferential interval, power justification, equivalence or hypothesis decision. It does not justify five confirmatory replicates or guarantee full-workload resources. RP002A and Cycle 01 remain PLANNED; Cycle resolutions remain 0/13. No scientific Claim is promoted and no further execution is authorized.

## Runtime and validation traces

| World | Model | Epochs | Best epoch | Stop | Fit seconds | Near-cap | Late-20 | Last-five |
|---|---|---:|---:|---|---:|---|---|---|
| E0 | B1 | 75 | 55 | patience 20 | 10.365 | no | no | no |
| E0 | B2 | 116 | 96 | patience 20 | 135.535 | no | no | no |
| E1 | B1 | 164 | 144 | patience 20 | 21.909 | no | no | no |
| E1 | B2 | 107 | 87 | patience 20 | 128.309 | no | no | no |
| E2 | B1 | 29 | 9 | patience 20 | 3.858 | no | no | no |
| E2 | B2 | 39 | 19 | patience 20 | 46.698 | no | no | no |

The total includes data generation, training, selected-checkpoint assessment and artifact writing through the recorded timer. Per-fit times are measured locally and are not cross-platform benchmarks. Lifetime peak process resident memory was **263634944 bytes (251.42 MiB)**. The macOS raw `RUSAGE_SELF.ru_maxrss` value is 263634944 bytes; this includes imports and all fits, not incremental allocation or per-model memory. The auditor verifies recorded unit conversion, not the historical peak measurement itself.

## Single-replicate assessment diagnostics

Natural-log loss, equally weighted across held-out episodes. Lower is better. These are sampled descriptive diagnostics; episodes/timepoints do not increase the number of independently trained replicates. Checkpoint selection used validation only. B3 conditions on observed history and has no privileged realized hidden-state access.

| World | B0 | B1 | B2 | B3 | Training replicates |
|---|---:|---:|---:|---:|---:|
| E0 | 0.326296217 | 0.326333858 | 0.326312292 | 0.326294974 | 1 |
| E1 | 0.947108902 | 0.907665489 | 0.907184650 | 0.907087188 | 1 |
| E2 | 1.037966114 | 1.038062286 | 1.037995425 | 1.037946548 | 1 |

| Paired contrast | Difference | Training replicates |
|---|---:|---:|
| E1:B1-B0 | -0.039443413 | 1 |
| E1:B2-B0 | -0.039924252 | 1 |
| E0:B1-B0 | 0.000037642 | 1 |
| E0:B2-B0 | 0.000016075 | 1 |
| E2:B1-B0 | 0.000096172 | 1 |
| E2:B2-B0 | 0.000029311 | 1 |
| E1:B2-B1 | -0.000480839 | 1 |

No across-world pooling or comparison with earlier fresh-seed stages is used for a causal budget effect. Assessment outcomes cannot select a follow-up optimization budget. The prior analytic window-eight review and missing statistical calibration remain relevant; a learned-model difference does not establish necessity of recurrent memory.

## Provenance and audit

- Execution source: `ea5cd5188681cefd94a83b40afa8d32bc71f1f8d`.
- Frozen plan SHA256: `e0e55a02902b350cbab04f23f558ce69bad3fa82ef5eb98ef51ed2c0ee65174e`.
- Base configuration SHA256: `fdd50646ee1e5e6ae659091a0fc9e3e1b6ff47bea09b8f3e1471e8bac0cf34ee`.
- Manifest SHA256: `78ae8dfe2b50544ccfe1838a4d3d47a75f0393a3bf536800f09f7a4de9cb1d77`.
- Separate approval: `docs/research/BUDGET_TRANSFER_APPROVAL.json`, bound to frozen source `cd0bc4c751517bf84998a406d3ed233609577196`, unchanged baseline and this run ID.
- Environment: Python 3.9.6, NumPy 2.0.2, PyTorch 2.8.0; macOS arm64 CPU, two threads. Fresh `budget-transfer-proposal-0.1` seeds, no warm start, retry or extension.
- Fifty output hashes plus the manifest are preserved. The auditor verifies file sets/hashes, source/approval binding, regenerated data/seeds, B0/B3 reference predictions, selected learned-checkpoint predictions, losses, trace flags and the no-variance summary without optimization.
- Fifty-seven software tests pass. Baseline, research schema and generated-site checks remain required by CI.

[Raw run and manifest](https://github.com/omasim/Autorite/tree/main/research/RP002A/runs/budget-transfer-20261009-001) · [Frozen protocol](https://github.com/omasim/Autorite/blob/main/research/RP002A/BUDGET_TRANSFER_PROTOCOL.md)

## Next design work

The intended data sizes are feasible for this one local pilot. Before confirmation, review optimization rationale, variance assumptions, substantive margins and uncertainty calibration with a complete analysis implementation. Any additional training needs a separate fixed scope and authorization; this completed pilot grants none.
