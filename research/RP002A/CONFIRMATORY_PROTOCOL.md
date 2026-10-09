# RP002A frozen confirmatory protocol

Date: 2026-10-09. Run ID: `confirmatory-20261009-001`. Version: `confirmation-1.0`. Frozen before confirmatory outcomes. User authorization: explicit instruction to perform steps 1–4. Exact numerical file: `CONFIRMATORY_CONFIG.json`; full procedure and interpretation rules: `STATISTICAL_PIPELINE_PROTOCOL.md`. Historical `CONFIG_PROPOSAL.json` remains unchanged.

## Exact scope

Question: for these finite, discrete, stochastic, passive, partially observed generators, when do the specified trained history-based algorithms improve next-observation prediction over a current-observation conditional-count algorithm? E0 p=.1,q=0; E1 p=.1,q=.5; E2 p=.5,q=.5. Initial hidden-bit probability .5, stationary within independent episodes. No action, policy, intervention, self-modification or privileged realized hidden-state access. Prior-art and analytic limits are retained in `COLLISION_REVIEW.md` and `CONFIRMATORY_DESIGN_REVIEW.md`.

The frozen configuration selects **20 fresh training replicates per world**, 60 units and 120 learned fits. Each unit uses 4096 training, 1024 validation and 2048 held-out assessment episodes, 129 observations/128 prediction pairs. B0 counts, B1 window-eight MLP (579 parameters), B2 GRU state 12 (651 parameters), B3 observed-history Bayes filter. Training: Adam .001, batch 32, gradient clip 1, cap 300 epochs, patience 20, minimum-validation checkpoint. The exact fixed-budget procedure is the target, not an optimally trained algorithm. All trace warnings are retained.

Fresh `confirmation-1.0` seeds separate every world/replicate/split and model initialization/order; no calibration, variance or earlier data/checkpoint reuse. World lexicographic, B1 then B2; reset recurrent state every episode. CPU two threads, pinned environment, one 14400-second attempt including data/training/assessment/artifacts. No retry, extension, discretionary seed replacement or optional stopping. An incomplete attempt has no complete family decisions.

## Pre-outcome count selection

Synthetic calibration qualified n=20,30,50 only under its fixed fixtures. Five independent target-size exploratory replicates per world supplied the seven contrast SDs. The largest observed SD was 0.000450571; the simultaneous normal-theory upper-SD planning bound was 0.001805443, factor 4.007010. Apply the predeclared .005-nat half-width rule to the qualified counts:

| n per world | Assumed planning half-width |
|---:|---:|
| 20 | 0.002433256 |
| 30 | 0.001908195 |
| 50 | 0.001433789 |

Selected n=20; target met under the declared assumptions: True. Count selection uses exploratory SDs only, not effects or confirmatory observations. Five-replicate chi-square bounds assume normality and are unstable; this is a precision rationale, not an 80% power guarantee. Calibration does not prove actual-loss or distribution-free coverage. Dependency hashes bind all inputs and the selection record.

## Primary decisions and limits

Equal-weight training-replicate paired episode-mean natural-log-loss differences, clip 1e-8. Seven fixed two-sided Bonferroni intervals at alpha .05: mean +/- 2*t(1-.05/14,n-1)*s/sqrt(n). Independence and normal-theory assumptions remain explicit. The preselected factor two was stress tested before the variance stage; no normality test switches methods after confirmation. Zero observed SD is an analysis failure.

E1:B1-B0 and E1:B2-B0 require an entire interval below -.01 for benefit. E0/E2 B1-B0 and B2-B0 require an entire interval strictly inside [-.01,+.01] for equivalence. E1:B2-B1 requires the benefit rule, but is solely an implementation comparison. Other outcomes are indeterminate; nonsignificance does not establish equivalence. The .01 margin is a fixture-specific engineering tolerance, about one quarter of E1's ideal .03981-nat current-to-history gain, not a universal substantive threshold. The ideal window-eight/full-history gap is ~.000012 nats: this experiment cannot establish recurrence necessity.

Secondary outputs are descriptive: multiclass Brier score, current-erasure/visible conditional log losses, fixed top-label confidence bins, clipping fractions, unclipped loss if finite and gap to B3. Empty strata/bins remain null. All raw datasets, selected weights, validation traces, original-precision predictions/losses and model-level secondary metrics are retained losslessly; saved predictions and analysis must replay without training.

The user has authorized execution, but an exact source/baseline/config approval record must be committed before launch. No automatic scientific Claim promotion or Cycle closure follows a completed benchmark.
