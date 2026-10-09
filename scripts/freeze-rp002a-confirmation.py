from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from packages.rp002a import pipeline as p,inference as i
import argparse
a=argparse.ArgumentParser();a.add_argument('--write',action='store_true');args=a.parse_args()
if not args.write:raise SystemExit('Plan-only: use --write to freeze the already authorized derived protocol; no sampling or training.')
plan=json.loads(p.PLAN.read_text());base=json.loads((ROOT/plan['base_configuration']).read_text())
cal=ROOT/'research/RP002A/runs'/plan['calibration']['run_id'];var=ROOT/'research/RP002A/runs'/plan['variance']['run_id']
if (cal/'failure.txt').exists() or (var/'failure.txt').exists():raise SystemExit('Failed prerequisite; no confirmation freeze')
cs=json.loads((cal/'summary.json').read_text());vs=json.loads((var/'summary.json').read_text())
selected=i.select_count([r['sample_sd'] for r in vs['contrasts']],cs['eligible_counts'],plan)
from scipy.stats import t
import math
selected['planning_widths']={str(n):float(2*t.ppf(1-.05/14,n-1)*selected['upper_sd']/math.sqrt(n)) for n in plan['confirmation_rule']['candidate_counts']};selected['eligible_counts']=cs['eligible_counts']
selpath=ROOT/'research/RP002A/CONFIRMATORY_SELECTION.json';selpath.write_text(json.dumps(selected,indent=2)+'\n')
rule=plan['confirmation_rule'];config=dict(version=rule['version'],run_id=rule['run_id'],frozen=True,execution_authorized=True,base_configuration=plan['base_configuration'],base_configuration_sha256=plan['base_configuration_sha256'],environment=plan['environment'],replicates=selected['selected_n'],training=plan['training'],inflation=rule['inflation'],margin=rule['margin'],decision_kinds=rule['decision_kinds'],max_wall_seconds=rule['max_wall_seconds'],interval_method='twofold-inflated replicate-mean Student-t Bonferroni, familywise alpha=.05, seven primary contrasts',scope='Fixed-budget passive finite-process algorithm benchmark; conditional normal-theory inference, no recurrence-necessity or universal-history claim',dependency_sha256={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [p.PLAN,cal/'manifest.json',cal/'summary.json',var/'manifest.json',var/'summary.json',selpath]})
p.CONFIRM.write_text(json.dumps(config,indent=2)+'\n')
text=f'''# RP002A frozen confirmatory protocol

Date: 2026-10-09. Run ID: `{config['run_id']}`. Version: `{config['version']}`. Frozen before confirmatory outcomes. User authorization: explicit instruction to perform steps 1–4. Exact numerical file: `CONFIRMATORY_CONFIG.json`; full procedure and interpretation rules: `STATISTICAL_PIPELINE_PROTOCOL.md`. Historical `CONFIG_PROPOSAL.json` remains unchanged.

## Exact scope

Question: for these finite, discrete, stochastic, passive, partially observed generators, when do the specified trained history-based algorithms improve next-observation prediction over a current-observation conditional-count algorithm? E0 p=.1,q=0; E1 p=.1,q=.5; E2 p=.5,q=.5. Initial hidden-bit probability .5, stationary within independent episodes. No action, policy, intervention, self-modification or privileged realized hidden-state access. Prior-art and analytic limits are retained in `COLLISION_REVIEW.md` and `CONFIRMATORY_DESIGN_REVIEW.md`.

The frozen configuration selects **{config['replicates']} fresh training replicates per world**, {3*config['replicates']} units and {6*config['replicates']} learned fits. Each unit uses 4096 training, 1024 validation and 2048 held-out assessment episodes, 129 observations/128 prediction pairs. B0 counts, B1 window-eight MLP (579 parameters), B2 GRU state 12 (651 parameters), B3 observed-history Bayes filter. Training: Adam .001, batch 32, gradient clip 1, cap 300 epochs, patience 20, minimum-validation checkpoint. The exact fixed-budget procedure is the target, not an optimally trained algorithm. All trace warnings are retained.

Fresh `confirmation-1.0` seeds separate every world/replicate/split and model initialization/order; no calibration, variance or earlier data/checkpoint reuse. World lexicographic, B1 then B2; reset recurrent state every episode. CPU two threads, pinned environment, one 14400-second attempt including data/training/assessment/artifacts. No retry, extension, discretionary seed replacement or optional stopping. An incomplete attempt has no complete family decisions.

## Pre-outcome count selection

Synthetic calibration qualified n=20,30,50 only under its fixed fixtures. Five independent target-size exploratory replicates per world supplied the seven contrast SDs. The largest observed SD was {selected['maximum_observed_sd']:.9f}; the simultaneous normal-theory upper-SD planning bound was {selected['upper_sd']:.9f}, factor {selected['upper_sd_factor']:.6f}. Apply the predeclared .005-nat half-width rule to the qualified counts:

| n per world | Assumed planning half-width |
|---:|---:|
'''
for n,w in selected['planning_widths'].items():text+=f'| {n} | {w:.9f} |\n'
text+=f'''
Selected n={config['replicates']}; target met under the declared assumptions: {selected['precision_target_met_under_assumptions']}. Count selection uses exploratory SDs only, not effects or confirmatory observations. Five-replicate chi-square bounds assume normality and are unstable; this is a precision rationale, not an 80% power guarantee. Calibration does not prove actual-loss or distribution-free coverage. Dependency hashes bind all inputs and the selection record.

## Primary decisions and limits

Equal-weight training-replicate paired episode-mean natural-log-loss differences, clip 1e-8. Seven fixed two-sided Bonferroni intervals at alpha .05: mean +/- 2*t(1-.05/14,n-1)*s/sqrt(n). Independence and normal-theory assumptions remain explicit. The preselected factor two was stress tested before the variance stage; no normality test switches methods after confirmation. Zero observed SD is an analysis failure.

E1:B1-B0 and E1:B2-B0 require an entire interval below -.01 for benefit. E0/E2 B1-B0 and B2-B0 require an entire interval strictly inside [-.01,+.01] for equivalence. E1:B2-B1 requires the benefit rule, but is solely an implementation comparison. Other outcomes are indeterminate; nonsignificance does not establish equivalence. The .01 margin is a fixture-specific engineering tolerance, about one quarter of E1's ideal .03981-nat current-to-history gain, not a universal substantive threshold. The ideal window-eight/full-history gap is ~.000012 nats: this experiment cannot establish recurrence necessity.

Secondary outputs are descriptive: multiclass Brier score, current-erasure/visible conditional log losses, fixed top-label confidence bins, clipping fractions, unclipped loss if finite and gap to B3. Empty strata/bins remain null. All raw datasets, selected weights, validation traces, original-precision predictions/losses and model-level secondary metrics are retained losslessly; saved predictions and analysis must replay without training.

The user has authorized execution, but an exact source/baseline/config approval record must be committed before launch. No automatic scientific Claim promotion or Cycle closure follows a completed benchmark.
'''
(ROOT/'research/RP002A/CONFIRMATORY_PROTOCOL.md').write_text(text)
# Register the pre-outcome Test without asserting a scientific result.
f=ROOT/'research/RP002A/confirmation/RECORD.md';f.parent.mkdir(parents=True,exist_ok=True)
d=dict(schema_version='0.1',id='TST-RP002A001',type='Test',title='Fixed-budget history-prediction benchmark',created_at='2026-10-09',updated_at='2026-10-09',source_refs=['research/RP002A/CONFIRMATORY_PROTOCOL.md','research/RP002A/CONFIRMATORY_CONFIG.json','research/RP002A/COLLISION_REVIEW.md'],relations=[{'relation':'tests','target':'Q-3'},{'relation':'tests','target':'Q-4'}],package_ref='RP-002A',protocol_ref='research/RP002A/CONFIRMATORY_PROTOCOL.md',target_refs=['Q-3','Q-4'])
f.write_text('---\n'+json.dumps(d,indent=2)+'\n---\n\nPre-outcome operational Test of Q-3 representation and Q-4 realized-history questions in the finite predictive fixture. No Result or Claim is asserted by registering this record.\n')
f=ROOT/'research/RP002A/RECORD.md';parts=f.read_text().split('---',2);d=json.loads(parts[1]);d.update(status='ACTIVE',updated_at='2026-10-09',protocol_ref='research/RP002A/CONFIRMATORY_PROTOCOL.md');body=parts[2];body='\n\nCurrent protocol: `CONFIRMATORY_PROTOCOL.md`, frozen for the one authorized benchmark. Earlier readiness dispositions below are historical; their outputs and warnings remain preserved.\n'+body;f.write_text('---\n'+json.dumps(d,indent=2)+'\n---'+body)
print(json.dumps(selected,indent=2))
