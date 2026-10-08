# CI/CD and Release Plan
## Pull-request checks
Markdown/frontmatter parse; schema validation; unique IDs; referential integrity; status/type compatibility; supersession integrity; public-claim scope/limitation checks; broken internal/cross-site links; build both sites; affected research-code tests.

## Deployments
Merge to `main` triggers independent production deployments:
- `apps/org` → autorite.org
- `apps/net` → autorite.net

Site PRs should produce independent preview deployments where supported.

## Research runs
Run artifacts are immutable. Bugs invalidate runs; corrected runs receive new IDs.

## Releases
- `baseline-v0.1`
- `cycle-01-checkpoint-a`
- `cycle-01-close`

## Secrets
Never commit credentials. DNS/deployment tokens live in GitHub/provider secret stores. Codex stops before any operation requiring user secrets.
