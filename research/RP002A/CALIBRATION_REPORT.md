# RP002A synthetic calibration review

Date: 2026-10-09. Run: `calibration-20261009-001`. Synthetic analysis stress tests only; no learned models or RP002A generator observations.

## Disposition

All 90 fixed Student-t cells (1,800,000 trials) and 18 percentile-bootstrap benchmark cells completed in 39.414 seconds. The preselected twofold-inflated Bonferroni replicate-mean Student-t procedure met the declared eligibility gate at n=20,30,50. No interval factor, scenario, threshold or decision rule was chosen after outcomes. Eligibility applies only to the declared synthetic fixtures. It does not establish distribution-free or actual-loss coverage.

| n | Worst simultaneous coverage | Largest simultaneous MC upper failure bound | Worst uninflated t coverage | Eligible for confirmation |
|---:|---:|---:|---:|---|
| 5 | 0.97935 | 0.02414 | 0.85200 | no; below predeclared minimum |
| 10 | 0.99060 | 0.01184 | 0.84540 | no; below predeclared minimum |
| 20 | 0.99840 | 0.00275 | 0.87855 | yes |
| 30 | 0.99890 | 0.00209 | 0.89505 | yes |
| 50 | 0.99970 | 0.00094 | 0.91140 | yes |

Coverage is the fraction of independent trials in which all seven intervals contain their true means. Upper failure bounds are Clopper-Pearson with .05/90, giving simultaneous Monte Carlo statements across the fixed grid. They describe simulation sampling error, not actual-loss uncertainty. Normal, centered Gamma(shape=2) and standardized t(df=5) effects, shared-component rho=0,.5 and within-mean fractions 0,.5,1 are all retained. The uninflated method's skew-case failures demonstrate why its normal approximation cannot be assumed safe in these stress fixtures. The fixed factor two is conservative in the grid; it is not a universally validated correction.

## Bootstrap benchmarks

Each cell has only 100 independent trials and 2,000 bootstrap draws over eight synthetic episodes. These are bounded comparison fixtures, not a target-data-size calibration or a method-selection gate. Coverage values consequently have substantial Monte Carlo uncertainty.

| n | Law | Within-mean fraction | Whole-cluster coverage | Nested coverage |
|---:|---|---:|---:|---:|
| 5 | normal | 0 | 0.50 | 0.50 |
| 5 | normal | 1 | 0.53 | 0.98 |
| 5 | centered-gamma2 | 0 | 0.43 | 0.43 |
| 5 | centered-gamma2 | 1 | 0.38 | 0.99 |
| 5 | standardized-t5 | 0 | 0.51 | 0.51 |
| 5 | standardized-t5 | 1 | 0.48 | 0.99 |
| 20 | normal | 0 | 0.93 | 0.93 |
| 20 | normal | 1 | 0.87 | 0.99 |
| 20 | centered-gamma2 | 0 | 0.82 | 0.82 |
| 20 | centered-gamma2 | 1 | 0.87 | 0.99 |
| 20 | standardized-t5 | 0 | 0.85 | 0.85 |
| 20 | standardized-t5 | 1 | 0.94 | 1.00 |
| 50 | normal | 0 | 0.95 | 0.95 |
| 50 | normal | 1 | 0.88 | 1.00 |
| 50 | centered-gamma2 | 0 | 0.91 | 0.91 |
| 50 | centered-gamma2 | 1 | 0.91 | 1.00 |
| 50 | standardized-t5 | 0 | 0.88 | 0.88 |
| 50 | standardized-t5 | 1 | 0.96 | 1.00 |

The complete summaries retain false benefit/equivalence boundary rates, center-equivalence rates and widths; no favorable cells are discarded. Nested variance inflation and small-n percentile undercoverage have different causes. Adding inner resampling is not a general solution to percentile tails or skew. There is no claim that these benchmark frequencies are precise estimates of nominal .95 coverage.

## Provenance and reproduction

Execution source: `350090247bba8d7c8cd98e4b3ccec69e80752966`. Frozen pipeline SHA256: `b3bd602411fd0f7269cd6b48b25d123423f6f9f849a37bb3ae5e389b20d1fd2a`. Manifest SHA256: `8f121239a0f020184f80299d54bf881851fde1808f9d6da6da612b36905db63b`.

Python 3.9.6, NumPy 2.0.2, SciPy 1.13.1; fixed SHA256 seed namespace `calibration-1.0`. The separately bound user approval is `docs/research/CALIBRATION_APPROVAL.json`. All 111 output hashes are preserved, including per-trial means/SDs/decision flags and every benchmark cell. `scripts/check-statistical-pipeline.py` verifies source/plan/approval binding, immutable files and recomputes interval flags/rates/eligibility from stored trial diagnostics without new sampling or training. Seventy software tests pass.

[All raw calibration files](https://github.com/omasim/Autorite/tree/main/research/RP002A/runs/calibration-20261009-001) · [Frozen pipeline protocol](https://github.com/omasim/Autorite/blob/main/research/RP002A/STATISTICAL_PIPELINE_PROTOCOL.md)

## Next authorized step

Proceed to the predeclared five fresh target-size training replicates per world. Only their seven contrast SDs may choose the final count by the frozen rule; means cannot tune models or margins. Actual-loss assumptions remain explicit, and no scientific Claim or Cycle obligation is resolved by calibration.
