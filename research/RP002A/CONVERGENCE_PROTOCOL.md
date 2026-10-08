# RP002A exploratory convergence and replicate-variability stage

Version: convergence-proposal-0.1. Date: 2026-10-08. **Proposed, unfrozen and execution not authorized.** This is a separately reviewable follow-up to the first engineering pilot, not confirmation. No new model outcomes have been observed.

## Purpose and limits

Check whether the fixed B1/B2 training budget settles validation loss, and describe variability across independently trained replicates. This addresses the open convergence and variance gates in `CONFIRMATORY_DESIGN_REVIEW.md`. The frozen baseline, numerical confirmatory proposal and first pilot artifacts remain unchanged.

The stage cannot decide a scientific hypothesis, equivalence, recurrence necessity, novelty, statistical power or Cycle closure. Its data and trained models may never enter confirmatory evidence. Variance estimates from a small exploratory study are unstable; they will inform sensitivity assumptions, not certify a final sample count.

## Fixed scope proposed before outcomes

| Item | Proposed choice |
|---|---|
| Worlds | Existing E0/E1/E2 laws, unchanged |
| Independently trained replicates | E0: 5; E1: 10; E2: 5 |
| Per replicate | 256 training, 128 checkpoint-selection validation, 128 independent assessment episodes |
| Episode length | 129 observations; 128 next-observation prediction pairs |
| Models | Existing B0 counts, B1 window-eight MLP, B2 12-state GRU, B3 observed-history exact filter |
| B1/B2 training | Adam 0.001, episode batches 32, gradient clip 1, at most 50 epochs |
| Checkpoint selection | Minimum validation loss; stop after five consecutive epochs without improvement |
| Execution environment | Python 3.9.6, NumPy 2.0.2, PyTorch 2.8.0; macOS arm64 CPU; two threads |
| Stage deadline | 900 seconds from stage start; checked before phases, each training batch and after validation |
| Number of attempts | One fixed run ID: convergence-20261008-001 |
| Order | Replicate index ascending, world lexicographic, then B1 followed by B2 |

There are 20 independent world/replicate units, 40 learned-model fits and 80 descriptive model records. More replicates are allocated to E1 because that fixture is the history-informative case. The control-world sample counts remain too small for reliable equivalence inference; none is attempted. Episode counts are an explicit bounded exploratory choice, not a completed power rationale.

The machine/library gate rejects a different environment. The actual OS build, source commit, dependency versions, per-fit elapsed seconds and overall elapsed seconds will be captured. Deadline checks are cooperative: an in-progress CPU batch/validation operation finishes before the check; the plan does not promise a process-kill at exactly 900 seconds. There is no discretionary deadline extension.

## Separation and randomness

The seed namespace is `convergence-proposal-0.1`, distinct from `pilot-0.1` and the proposed `proposal-0.1` confirmation schedule. The version is an opaque seed namespace; if approval freezes this exact proposal, preserve it. No extra randomness is silently introduced.

For each world/replicate, declare independent seeds for training, validation and assessment observations, plus separate B1/B2 initialization and batch-order seeds. SHA-256 derivation is unchanged. The complete 140-seed schedule can be computed before execution and has no collision with the declared pilot/confirmation seeds. Random seed separation is verified; global stochastic independence beyond the generator construction is not asserted from hashes alone.

B0 fits training data only. B1/B2 optimization and checkpoint selection see only training and validation; no realized latent-state arrays reach a predictor. Only after each model's selection are its assessment predictions evaluated. Within a replicate, all models share the same assessment episodes for paired comparisons. Across replicates, all three datasets and model seeds change. Episodes and prediction timepoints are never counted as independent training replicates.

## Predeclared descriptive outputs

For each fit, retain the validation trace, selected model weights, best epoch, final loss, epochs completed and fit elapsed time. Report two diagnostic flags without treating them as proof:

- **Best near the cap:** the fit completed all 50 epochs and its selected epoch lies in the final ten epochs.
- **Late improvement:** first minus last validation loss in the final five recorded epochs exceeds 0.001 nats. A shorter trace is explicitly reported and cannot receive this flag.

These flags indicate potential budget sensitivity, not statistical convergence or permission to extend training. Early stopping also does not prove convergence. Final validation loss can differ from the restored best checkpoint's loss; both are identified.

For B0–B3, average assessment timepoint log losses within episodes, then across episodes, giving one mean per training replicate. Report model means, sample SD with n−1 denominator, range and leave-one-replicate-out SD range. For the seven existing contrast labels, compute paired differences within each training replicate before summarizing across replicates. Report n=5 or n=10 explicitly; do not pool worlds.

All outputs are descriptive. No p-values, inferential intervals, equivalence calls, power guarantees or automatic confirmatory sample-count selection are generated. A complete aggregate is produced only if every planned fit and replicate succeeds. Partial completed outputs remain visible on failure but are not summarized as a completed-stage comparison.

## Failure and preservation

Use a new immutable directory. Existing directories cannot be overwritten, and approval is bound to one fixed run ID. A timeout, numerical failure or interruption preserves completed datasets, checkpoints/traces, partial replicate records, a traceback and the output-hash manifest. An interrupted fit has no guaranteed final checkpoint/trace; this limitation is explicit. No retry, model substitution, seed replacement, extra epoch or extra replicate is allowed by this plan.

## Executable preparation and audit

`python3 scripts/rp002a-convergence.py` is plan-only and creates no data. `--execute --run-id convergence-20261008-001` refuses before artifact creation until the plan is frozen/authorized and a separate `docs/research/CONVERGENCE_APPROVAL.json` matches its plan hash, baseline manifest hash, fixed run ID and exact reviewed source commit. The earlier bootstrap/first-pilot approval cannot authorize this stage. The source must remain unchanged except for that approval record and the checkout must be clean.

Approval metadata must contain `approved: true`, `run_id`, `plan_sha256`, `baseline_manifest_sha256`, `source_commit`, date and human approval evidence. Freeze and commit the approved proposal before adding that matching approval record, then execute from a reviewed clean source. Source and plan changes require renewed review before outcomes.

After execution, `scripts/check-convergence.py` will verify file coverage/checksums, committed-run immutability, approved source configuration, seed/data replay, B0/B3 replay, saved learned-checkpoint predictions, losses and replicate-level summaries. It performs no training. Learned-checkpoint replay uses explicit floating-point tolerance across CPU platforms; it does not establish bit-identical cross-platform optimization.

Current software fixtures cover the authorization boundary, one-run ID, independent seed namespace, assessment exclusion from optimization, partial-failure preservation, paired replicate summaries and descriptive trace flags. No full convergence run or 15-minute feasibility measurement has been performed.

## Concrete approval scope

Approve only this one separately declared exploratory stage with the fixed scope above. Do not approve a confirmatory study, baseline amendment, novelty claim, new hypothesis or Cycle resolution. After the stage, review actual convergence flags, replicate variability and runtime before proposing a separate confirmatory freeze.
