# RP002A executable acceptance and pilot plan

Date: 2026-10-08. The generator, B0–B3 implementations, training primitive and paired bootstrap primitive are implemented. The first isolated exploratory pilot completed; see `PILOT_001_REPORT.md`. No confirmatory run has been executed.

## Acceptance checks completed

The exact history filter agrees with independently enumerated hidden-state paths on all four-symbol histories for the declared E0/E1/E2 laws. E0 present sufficiency, E2 history irrelevance and an E1 predictive-alias witness are deterministic fixture checks. The generator returns observed data only; no realized latent-state array reaches a model or reference predictor.

Finite windows and recurrent outputs are causal and independent across episodes. Model parameter counts match the proposed 579/651 sizes. The complete proposed seed schedule has no duplicate seeds. Log loss, paired resampling, optimizer/checkpoint plumbing and training deadlines pass software checks. The single optimizer-step fixture uses fixed arbitrary arrays, not a declared-world research comparison.

## Separate exploratory pilot

The approved and frozen `PILOT_PLAN.json` specifies 64 training, 32 validation and 32 engineering-diagnostic episodes per world, with 16 prediction pairs per episode, one replicate and at most three epochs. The total training wall-time cap is 300 seconds on two CPU threads. Pilot seeds use their own version namespace and do not overlap the proposed confirmation schedule.

The pilot checks finite numerical outputs, artifact integrity, deterministic plumbing and resource feasibility. It cannot support primary hypotheses, equivalence, novelty, statistical power or Cycle completion. Save pilot data/model checkpoints/traces and descriptive losses in a unique immutable run directory. A failed run retains its artifacts and failure traceback; it is never silently retried or overwritten.

## Commands

Install the research environment using `scripts/requirements-research.txt` and run:

```sh
python3 -m unittest discover -s tests
python3 scripts/rp002a-pilot.py
```

The second command is plan-only and creates no run. Execution requires an explicitly frozen/authorized pilot plan and an audited approval record tied to the baseline manifest, exact pilot plan hash and source commit. The current pilot plan is frozen and authorized for the one recorded run. The source gate prevents further execution after unapproved implementation changes. `--execute --run-id ...` refuses before creating a directory while those gates remain unmet. Confirmatory execution is not exposed by this pilot runner.

## Environment and limitations

Local acceptance checks used Python 3.9.6, NumPy 2.0.2 and PyTorch 2.8.0 on CPU. These installed library versions are pinned in the research requirements. Each eventual run captures its actual environment; a cross-platform reproducibility lock has not yet been approved. GRU state resets and parameter conventions follow [PyTorch 2.8 GRU documentation](https://docs.pytorch.org/docs/2.8/generated/torch.nn.GRU.html); optimization uses [Adam](https://docs.pytorch.org/docs/2.8/generated/torch.optim.Adam.html).

The audited bootstrap and preserved baseline freeze were approved. Full collision assessment, uncertainty/power rationale and confirmatory pre-outcome freeze remain open. Software acceptance does not resolve these scientific/governance requirements. Structural generator checks are not a report of learned-model performance.
