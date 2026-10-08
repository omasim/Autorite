# Implementation Roadmap

## Launch priority — Sites first (2026-10-07)
The user requested both sites before the research implementation milestones, so the process can be shared from the beginning. Both sites are in English. Publish an initial knowledge site and laboratory from one shared preparation record, with source documents, explicit empty result states and a change journal. This is a preparation release, not scientific freeze, bootstrap completion or permission to execute research.

The initial static projections live in `apps/org` and `apps/net`; `scripts/build-sites.py` reads shared `canonical/site-state.json`. Generated Site repositories are deployment artifacts, not independent scientific authorities. Keep source documents intact. Continue M0–M6 after the initial publication; M2/M3 expand the first sites as validated research records become available.

## M0 — Import and Preserve
Import the authoritative `baseline/` package; create repository structure; preserve its exact contents in `baseline/v0.1`; create living `canonical`; preserve Decision-0001 and Decision-0002; record source checksums. Do not create the release tag yet. The source snapshot is protected from editing throughout bootstrap.
**Do not execute research yet.**

## M1 — Research Core
Implement schema/frontmatter validator, ID/reference checks, templates, Cycle 1 folders and graph fixtures.

## M2 — autorite.org Alpha
Implement Horizon identity and editorial Cycle Ring from canonical Cycle data.
Build public knowledge site: Home, Questions, Current Knowledge, Research summaries, Methods, Archive, About. Use shared canonical loader.

## M3 — autorite.net Alpha
Implement the same Cycle Ring semantics with operational obligation breakdown.
Build Lab site: dashboard, Cycle 1, RP pages, experiment/result/review/release views. Use same shared loader.

## M4 — Cross-Site Contract
Stable IDs, links, canonical public URLs, duplicate-content audit, sitemaps, search metadata, status vocabulary.

## M5 — CI/CD + DNS
Independent builds/deployments, previews, branch rules, custom domains and HTTPS. Credentials remain user-controlled.

## M6 — Bootstrap Audit
Run all checks; verify both sites against same records; record deviations; user approves the audited freeze. Only then create `baseline-v0.1`. M0 preservation and M6 release approval are separate steps.

## M7 — Start Research
Activate RP002A collision/preregistration execution. RP003 follows. DAM X archaeology may proceed in parallel only when source material is available.

## Checkpoint A
After RP002A/RP003: validate methodology, graph, site projections and handling of negative/surprise outcomes before full RP004/RP005A execution.
