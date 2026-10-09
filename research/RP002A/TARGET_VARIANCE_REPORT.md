# RP002A target-size variance review

Date: 2026-10-09. Run `target-variance-20261009-001`. Exploratory variability stage, not confirmation.

All 15 independent units and 30 learned fits completed in 1409.049 seconds (23 minutes 29 seconds). Each world has five independently generated training/validation/assessment datasets and initialization/order draws at 4096/1024/2048 episodes, 129 observations. No predeclared near-cap, late-20 or last-five warnings occurred. This is absence of warnings, not optimization proof; earlier stage warnings remain unchanged.

| Paired contrast | n | Mean difference | Sample SD | Leave-one-out SD min | Leave-one-out SD max |
|---|---:|---:|---:|---:|---:|
| E1:B1-B0 | 5 | -0.039426787 | 0.000334082 | 0.000172657 | 0.000385253 |
| E1:B2-B0 | 5 | -0.040034166 | 0.000450571 | 0.000309682 | 0.000520194 |
| E0:B1-B0 | 5 | 0.000058470 | 0.000024284 | 0.000016154 | 0.000028037 |
| E0:B2-B0 | 5 | 0.000027389 | 0.000023343 | 0.000006185 | 0.000026801 |
| E2:B1-B0 | 5 | 0.000103839 | 0.000043073 | 0.000021223 | 0.000049443 |
| E2:B2-B0 | 5 | 0.000029315 | 0.000022351 | 0.000018649 | 0.000025341 |
| E1:B2-B1 | 5 | -0.000607379 | 0.000149135 | 0.000121093 | 0.000169620 |

No old smaller-data stage is pooled with these values. Means are descriptive and cannot tune models, margins or the count rule. No inferential interval or hypothesis decision is made from this exploratory stage. Five replicates provide limited variance resolution; leave-one-out changes are displayed rather than hidden.

## Predeclared count selection

The largest of the seven sample SDs is 0.000450571. The frozen chi-square rule gives a simultaneous normal-theory upper-SD planning bound 0.001805443, factor 4.007010. It assumes normal independent replicate differences and is not a distribution-free variance guarantee. Qualified counts from synthetic calibration are 20,30,50. At n=20 the twofold-inflated Bonferroni-t assumed half-width is 0.002433256, below the fixed .005 target. Therefore the unchanged rule selects **20 replicates per world**. This is precision planning under assumptions, not 80% power or guaranteed confirmation runtime.

The separate `CONFIRMATORY_CONFIG.json` and `CONFIRMATORY_PROTOCOL.md` bind this selection and the calibration/variance hashes. They use untouched `confirmation-1.0` seeds. No assessment outcome selected the training budget, effect margin or interval method.

## Provenance and audit

Execution source `10cddc582e3dab164f48df413a4c8503eb4f5c29`; frozen pipeline SHA256 `b3bd602411fd0f7269cd6b48b25d123423f6f9f849a37bb3ae5e389b20d1fd2a`; manifest SHA256 `667f4d9c97ba0904a4e0f08dcd64ecb8097137e2ba8502da306643102e35d1fc`. Separate approval: `docs/research/VARIANCE_APPROVAL.json`, tied to source, plan and unchanged baseline under the explicit user instruction for steps 1–4.

All 123 outputs plus manifest are retained. The auditor verifies immutability/hashes, source/approval binding, fresh regenerated data, B0/B3 references, selected learned-checkpoint predictions, losses, secondary diagnostics, traces and seven replicate summaries without optimization. Original categorical data and floating prediction precision are preserved losslessly in compressed archives.

[All raw variance files](https://github.com/omasim/Autorite/tree/main/research/RP002A/runs/target-variance-20261009-001)

No scientific Claim or Cycle obligation is resolved. Proceed only to the separately source-bound frozen one-attempt confirmation; no discretionary repeats or extensions.
