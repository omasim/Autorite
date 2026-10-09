# RP002A remaining budget-warning review

Date: 2026-10-09. Post-outcome planning review of `convergence-20261009-002`; no new observations or model training. The recorded convergence disposition remains unresolved.

## Evidence and reproduction

`design/CONVERGENCE_002_DIAGNOSTICS.json` records 40 per-fit validation diagnostics and six world/model summaries. Its source manifest hash and 80 input checksums bind validation episodes, saved training-only B0 tables and recorded validation traces. Reproduce with `python3 scripts/rp002a-budget-diagnostics.py`. This operation does not read assessment observations or losses, train models, draw new data or amend immutable run files.

B0 and the observed-history B3 filter are evaluated on the same checkpoint-selection validation episodes. Learned losses are taken from the recorded minimum-validation checkpoints. Those validation episodes already influenced model selection, so these comparisons are optimistic planning diagnostics, not independent evaluation. Learned trace losses use float32 cross entropy; references use clipped probability loss. Precision and clipping conventions remain visible. A sampled reference loss is not an empirical lower bound that every learned predictor must exceed.

## Where the remaining warnings occur

Of 12 near-cap warnings, E0 accounts for eight (B1: three, B2: five) and E1 for four (B1: three, B2: one). E2 has none. Among these flagged fits, the last-20-epoch endpoint decline ranges from -0.000140 to +0.000111 nats; the last-50-epoch decline ranges from -0.000027 to +0.000265 nats. Positive values mean lower loss at the endpoint. Small endpoint changes do not rule out oscillation, slow progress or later improvement; per-fit last-20 loss ranges remain in the JSON.

| World | Model | Replicates | Near-cap fits | Mean selected validation loss minus B0 | Mean selected validation loss minus B3 |
|---|---|---:|---:|---:|---:|
| E0 | B1 | 5 | 3 | +0.000434 | +0.000541 |
| E0 | B2 | 5 | 5 | +0.000662 | +0.000769 |
| E1 | B1 | 10 | 3 | -0.036904 | +0.003579 |
| E1 | B2 | 10 | 1 | -0.039710 | +0.000773 |
| E2 | B1 | 5 | 0 | +0.000677 | +0.000718 |
| E2 | B2 | 5 | 0 | +0.000172 | +0.000214 |

E0 gaps and endpoint changes are small on these reused validation samples. E1 B1 remains farther from the observed-history filter than B2. This cannot separate finite-data error, approximation limits, optimizer behavior or selection noise, and it does not imply a fundamental need for recurrence. The earlier ideal window-eight/full-history gap is only about 0.000012 nats. No convergence threshold or scientific effect margin is changed using this review.

## Next design choice

Do not reopen this run or retroactively remove its 12 warnings. The next useful question is whether the intended confirmatory **data sizes** are computationally feasible and how validation traces behave there. Stages 001/002 used only 256 training episodes; their runtimes and variances cannot be silently transferred to 4096 episodes.

`BUDGET_TRANSFER_PROTOCOL.md` and `BUDGET_TRANSFER_PLAN.json` propose one fresh replicate in each world, six learned-model fits total, at 4096/1024/2048 training/validation/assessment episodes. The pilot is for runtime and trace behavior only. One replicate per world provides no between-training variance estimate, power justification or scientific decision. The proposal remains unfrozen and unauthorized; its runner and artifact audit are now implemented and tested; a separate one-run approval is still required before execution.

After that separately reviewed feasibility step, revisit optimization and statistical calibration rather than copying a favorable exploratory SD into confirmation. The baseline and numerical confirmation proposal remain unchanged; no Claim or Cycle obligation is resolved.
