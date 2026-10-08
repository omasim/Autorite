# First exploratory pilot: engineering review

Date: 2026-10-08. Run: `pilot-20261008-001`. Outcome: completed with finite numerical outputs. This is an engineering diagnostic, not a confirmatory Result or support for a scientific Claim.

## Approval and provenance

The user approved the audited bootstrap, preserved baseline freeze and one bounded exploratory pilot. The immutable baseline is tagged `baseline-v0.1`; preservation metadata in `baseline/SNAPSHOT.json` is unchanged. Approval is recorded separately in `docs/research/BOOTSTRAP_APPROVAL.json`.

The run used source commit `3c97b72ad89b6abd8d380a4b01d7c04407bbc317`, frozen pilot plan `pilot-0.1`, Python 3.9.6, NumPy 2.0.2 and PyTorch 2.8.0 on macOS arm64 CPU. The run manifest captures full configuration, seed schedule, environment and output hashes. No retraining, seed replacement or discretionary retry was performed.

## Scope and artifact review

Three worlds; 64 training, 32 validation and 32 diagnostic episodes per world; 17 observations / 16 prediction pairs per episode; one replicate; B1/B2 at most three epochs; two CPU threads and a 300-second training deadline. All six training traces contain three epochs. Diagnostic samples were never used for model checkpoint selection.

All 49 output checksums match; all 36 NumPy arrays are finite. Replay reconstructs observed datasets from their declared seeds, B0 counts and B3 history-conditioned probabilities. Recomputed categorical losses reproduce all twelve descriptive summaries. Validation losses are finite. Checkpoints and traces are retained. The checker performs no learned-model retraining and does not claim bit-identical cross-platform training.

Raw artifacts are preserved in [the canonical GitHub run directory](https://github.com/omasim/Autorite/tree/main/research/RP002A/runs/pilot-20261008-001). `scripts/check-pilots.py` checks hashes, coverage, replay and committed-run immutability in CI.

## Descriptive diagnostic losses

Natural-log loss averaged over the 32 diagnostic episodes (512 prediction pairs) in each world. Smaller values indicate better prediction on this particular diagnostic sample. No intervals or hypothesis decisions are produced from this single tiny replicate.

| World | B0 counts | B1 finite window | B2 recursive state | B3 Bayes history filter |
|---|---:|---:|---:|---:|
| E0 | 0.360006 | 1.151015 | 0.987936 | 0.358556 |
| E1 | 0.930505 | 1.079471 | 1.164359 | 0.890254 |
| E2 | 1.057468 | 1.099844 | 1.097989 | 1.055966 |

B1 and B2 remain above B0 and B3 on this diagnostic sample after only three training epochs. This establishes neither the absence of a history benefit nor failure of a model class. It does not justify tuning against these diagnostic data. The pilot verifies execution and artifact plumbing; it does not establish training convergence, model comparison, equivalence, novelty or statistical power.

## Disposition and next work

The engineering pilot completed. No scientific Claim was promoted and no Cycle obligation was resolved; progress remains 0/13. Pilot observations must not enter confirmatory evidence.

Before a confirmatory run: complete the prior-art collision assessment, justify sample size and effect/equivalence thresholds, fix the environment and final analysis specification, and review/freeze the confirmatory protocol before outcomes. Larger exploratory convergence work, if needed, requires a separately versioned plan and fresh isolated data; this one-pilot approval does not authorize further runs.
