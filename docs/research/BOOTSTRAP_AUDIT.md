# Bootstrap audit and first-pilot approval proposal

Date: 2026-10-08. The user approved the proposed audited freeze and isolated pilot on 2026-10-08 by replying “devam” to the explicit approval request. Approval metadata and the baseline release tag are recorded separately; confirmatory execution remains unauthorized.

## Preserved baseline

The user-selected 20 Markdown sources have byte-identical copies in `baseline/v0.1/`; their SHA-256 manifest and checker pass. Historical source material remains separate. No scientific definition has been changed. The proposed release is this exact source snapshot, not the evolving operational supplement.

## Implemented and checked

- One canonical GitHub repository, `omasim/Autorite`, with branch/PR workflow and CI.
- Main protection requires an up-to-date `validate` check and PR workflow, blocks force pushes/deletion, and applies to administrators. Solo self-review is permitted; no external scientific review is implied.
- Fifteen typed source-backed research objects and the Cycle 01 manifest with 13 unresolved equal-weight obligations.
- Schema/status/reference/evidence/supersession/run integrity and Cycle closure/publication validation before both site builds.
- RP002A finite generators, information-matched Bayes filter, B0 counts, causal B1 MLP and B2 GRU, validation-based checkpointing, deadlines and paired resampling primitive.
- Thirty local software tests passed. Linux CI must pass for the final merged implementation before any run.
- Both English sites generate from shared validated data; publication versions and source commits are recorded separately from scientific records.
- DAM X source dependency and template are preserved; no archaeology material is invented.

## Explicit limitations and bootstrap deviations

1. The research graph contains no scientific Claims, Tests or Results yet. Result pages intentionally show empty states; automatic scientific result publication is not implemented. The first pilot must be reviewed and recorded explicitly before a public update.
2. Git provides history/provenance; a dedicated historical-query UI is deferred. There is no graph database or automatic inference.
3. Site deployment is performed through the recorded Sites workflow after reviewed merges, not unattended GitHub deployment. Research checks in CI are automatic.
4. Local acceptance used Python 3.9.6, NumPy 2.0.2 and PyTorch 2.8.0; CI uses Python 3.11 with CPU PyTorch. Each eventual run captures the actual environment. Cross-platform bit-identical model training is not claimed.
5. Prior-art review is a seed review, not exhaustive. No novelty claim is made. Full collision review, power/effect-threshold justification and confirmatory protocol freeze remain prerequisites to confirmatory research.
6. The first pilot is strictly exploratory engineering work with its own seeds, tiny data budget and no hypothesis/equivalence conclusions. Its data may not be reused as confirmatory evidence.

## Concrete approval scope proposed

Approve the audited initial bootstrap with the limitations above, freeze/tag the preserved baseline as `baseline-v0.1`, and authorize only the isolated pilot specified by `research/RP002A/PILOT_PLAN.json`: three worlds, 64/32/32 training/validation/diagnostic episodes each, 16 prediction pairs per episode, one replicate, at most three epochs, two CPU threads and 300 seconds maximum training wall time.

After human approval, record the approval, version and freeze the pilot plan before outcomes, anchor the exact implementation commit, then execute once in a new immutable run directory. Preserve failures as well as successful artifacts. The runner refuses execution before matching approval metadata exists.

This approval would not freeze the confirmatory configuration, authorize a confirmatory study, validate a novelty claim or resolve a Cycle obligation. Those remain separate, evidence-backed decisions.
