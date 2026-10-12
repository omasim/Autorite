---
schema_version: '0.1'
id: R-RP006001
type: Result
title: Finite query-relative lineage field-ablation result
created_at: '2026-10-12'
updated_at: '2026-10-12'
source_refs:
  - research/RP006/RP006_RESULT_REVIEW_001.md
  - research/RP006/RP006_OPERATIONAL_PROTOCOL.md
  - research/RP006/RP006_PREEXECUTION_REVIEW.md
  - research/RP006/audit-001/RECORD.md
  - docs/decisions/DECISION-0017_RP006_RESULT_DISPOSITION.md
relations:
  - relation: informs
    target: Q-3
  - relation: informs
    target: Q-4
status: VALID
test_ref: TST-RP006001
package_ref: RP-006
run_ref: research/RP006/attempts/570e92be-204b-4330-8300-bcbc4e2078d2
artifact_refs:
  - research/RP006/attempts/570e92be-204b-4330-8300-bcbc4e2078d2/manifest.json
  - research/RP006/attempts/570e92be-204b-4330-8300-bcbc4e2078d2/truth.jsonl
  - research/RP006/attempts/570e92be-204b-4330-8300-bcbc4e2078d2/projections.jsonl
  - research/RP006/attempts/570e92be-204b-4330-8300-bcbc4e2078d2/pairs.jsonl
  - research/RP006/attempts/570e92be-204b-4330-8300-bcbc4e2078d2/conflicts.jsonl
  - research/RP006/attempts/570e92be-204b-4330-8300-bcbc4e2078d2/certificates.json
  - research/RP006/attempts/570e92be-204b-4330-8300-bcbc4e2078d2/summary.json
  - research/RP006/attempts/570e92be-204b-4330-8300-bcbc4e2078d2/timing.json
  - research/RP006/attempts/570e92be-204b-4330-8300-bcbc4e2078d2/replay.json
observations: >-
  Independently replayed finite audit: FULL sufficient masks 001, 011, 101, 111 with
  inclusion-minimal mask 001; TOPOLOGY_STATE sufficient masks 001, 010, 011, 101,
  110, 111 with inclusion-minimal masks 001 and 010. Coverage: 216 truth rows, 48
  projections, 120 pair/mask comparisons, 438 conflict rows, 16 certificates,
  1,152 FULL and 960 TOPOLOGY_STATE equality-gated query checks. These reproduce
  already disclosed RP004/preflight classifications on six known constructions;
  they are not blind confirmation or fresh evidence and do not imply unseen-domain
  sufficiency, universal necessity, optimal encoding, novelty, or Q-3/Q-4 resolution.
---

`R-RP006001` informs Q-3 about inquiry-relative preservation and Q-4 about recoverable realized-history distinctions only on the registered finite corpus. D-0017 accepts the exact replay and limited interpretation; no broader Claim is promoted.
