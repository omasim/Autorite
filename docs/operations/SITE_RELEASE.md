# Initial site release

Both sites are in English. The knowledge site presents questions, current knowledge, methods, publications and changes. The laboratory presents Cycle 01, its four research packages, results and a process journal.

## Source and generation
`canonical/site-state.json` is the shared preparation/publication record, not a completed research graph schema. `canonical/site-origins.json` holds verified deployment origins. Baseline files are copied verbatim as downloadable sources. Site output is generated; edit the shared sources or generator, not deployed copies.

Run from the workspace root:

```sh
python3 -m pip install -r scripts/requirements-sites.txt
python3 scripts/build-sites.py
python3 scripts/check-sites.py
```

## Document library
`canonical/documents.json` defines the shared catalog, descriptions, categories and primary reading site. `packages/content/document-library.py` renders safe Markdown with raw HTML disabled; the pinned Markdown renderer dependency is in `scripts/requirements-sites.txt`. The library preserves `/sources/`, adds full-text search and category filters, and generates a single primary reading page per document. Catalog downloads use unique record keys to avoid filename collisions between baseline and implementation versions. Original download routes remain available. Readable pages include a heading-based contents list and a print stylesheet for browser Print / Save PDF.

Verification covered combined search/category filters, no matches, reset, document reading, eight schema table rows, nine contents anchors, and a 390px reader without page overflow. The site checker validates all generated links and heading anchors; catalog source downloads were checked byte-for-byte against originals.

The checker verifies English HTML, local and cross-site page/asset/document references, and identical canonical Cycle data in both outputs. The ring computes resolved obligations over total obligations. The initial state has zero resolutions and makes no claim that research has been executed.

## Hosting
Each `apps/*/.openai/hosting.json` identifies its registered Site. Preserve those IDs for updates. Use the Sites hosting workflow to push the exact generated source, package it, save a matching version and deploy it. Keep credentials in process memory/stdin, never in files. After every shared-data change, regenerate, validate and deploy both sites; a single-site deployment can temporarily expose different snapshots. The JSON state includes a source hash to detect this.

The Sites source repositories hold generated publication output. They do not replace the planned single canonical Git research repository. GitHub governance, typed research validation, immutable pilot records and CI are implemented.

## Publication limits
This release is a static snapshot. It has no background updater. Engineering pilot artifacts are preserved in canonical Git; no confirmatory evidence is fabricated. Displayed changes are documented preparation decisions. The audited preserved baseline freeze was approved on 2026-10-08 and tagged `baseline-v0.1`; the first isolated engineering pilot is publicly documented. Confirmatory execution remains pending. Custom-domain and SSL verification succeeded for `autorite.org`, `autorite.net` and both www hostnames on 2026-10-07; all four HTTPS addresses served the correct English site. See `CUSTOM_DOMAINS.md` for DNS and rollback records.
