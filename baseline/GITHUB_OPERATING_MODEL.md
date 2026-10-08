# GitHub Operating Model v0.1
## Canonical branch
`main` contains current canonical research state and site source. No direct routine pushes after baseline freeze.

## Change path
1. Open issue or Decision Record for substantive changes.
2. Create research/feature branch.
3. Add/update claim/result/decision records.
4. Open PR with epistemic impact summary.
5. Run required checks.
6. Review.
7. Merge.
8. Build/deploy site.
9. Tag immutable milestones when appropriate.

## Recommended PR template
- What changed?
- Object types affected
- Evidence/result basis
- Scope/assumption changes
- Claims challenged/superseded
- Public pages affected
- Is this confirmatory, exploratory, correction or infrastructure?
- Does it require a baseline amendment?

## Branch/rules policy
Protect `main` using GitHub rulesets or protected-branch controls. Require PR and checks; block force pushes/deletion. For solo operation, review can initially be self-review plus automated checks; external review is added for foundational claims.

## Tags
`baseline-v0.1`; `cycle-01-checkpoint-a`; `cycle-01-close`; publication-specific tags where needed.

## Issues/labels
Suggested labels: question, claim, experiment, formal, empirical, legacy, collision, decision, correction, blocked, synthesis, site, review.

## Live status
GitHub Issues/Projects may track execution, but canonical epistemic status remains in versioned research records, not only project-management metadata.
