# Autorite 2.0 — GitHub, Website and Domain Publishing Plan v0.1
## Principle
**One canonical research source; multiple projections.** GitHub is the canonical living research record. Websites are readable/generated projections, never independent epistemic copies.

## Recommended domains
### autorite.org — Primary public publication
Canonical public URL and institutional face: Questions, Current Knowledge, Research, Reflections, Archive, Constitution/About. Research pages expose status, scope and provenance.

### autorite.net — Research Network / Lab gateway
Technical/researcher landing surface: GitHub, open packages, code/data, contribution/review instructions and live research status. Deep knowledge content links to canonical autorite.org URLs rather than duplicating it.

## Alternatives
1. Single-site: autorite.net redirects fully to autorite.org — simplest launch.
2. Two independent sites — rejected for v0.1 due to duplication, synchronization and authority ambiguity.
3. **Recommended hybrid:** autorite.org publication + autorite.net lab/network gateway, one shared canonical repository.

## GitHub topology
Suggested public repository: `autorite/autorite-research` (final owner/name subject to GitHub account/organization availability).
Folders: `/canonical`, `/cycles`, `/research`, `/legacy`, `/graph`, `/protocols`, `/publications`, `/site`.

`main` = canonical/current. Research/feature branches = proposals. Tags/releases = frozen baselines and cycle closures.

Protect `main`: PR required, status checks, force-push/deletion blocked; linear history preferred; signed commits optional. Tags such as `baseline-v0.1` and `cycle-01-close` are immutable anchors.

## Live publishing flow
Research branch → typed result/review → canonical PR → merge to main → validation/build → autorite.org publication → autorite.net activity/network projection.

## CI checks
Frontmatter/schema validity; broken references; claim scope/status presence; invalid supersession links; publication provenance; site build; link check. Later: formula/type and epistemic-cast checks.

## Website architecture
Home → Questions → Current Knowledge → Research → Reflections → Archive.
Research package pages: question, scope, status, preregistration, results, deviations, evidence, next decision.
Claim pages: statement, type, scope, status, evidence/counterevidence, known limits, “does not imply”, version history, what would change our view.

## Release policy
Freeze Baseline v0.1 as a Git tag/release. Research remains live between cycle releases. Cycle closures publish immutable snapshots plus a synthesis report.

## Recommended launch decision
Use **autorite.org as canonical public site**. Launch **autorite.net as a lightweight Research Network/Lab gateway**; if maintaining two surfaces becomes overhead, temporarily redirect autorite.net to autorite.org/research without changing the canonical architecture.
