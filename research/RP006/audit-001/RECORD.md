---
schema_version: '0.1'
id: TST-RP006001
type: Test
title: Finite query-relative lineage field-ablation audit
created_at: '2026-10-12'
updated_at: '2026-10-12'
source_refs:
  - research/RP006/RP006_OPERATIONAL_PROTOCOL.md
  - research/RP006/RP006_PRIOR_ART_REVIEW.md
  - research/RP006/RP006_IMPLEMENTATION_REVIEW.md
  - research/RP006/RP006_EXECUTION_SUPERVISOR_REVIEW.md
  - research/RP006/RP006_PREEXECUTION_REVIEW.md
  - research/RP006/DOMAIN.json
  - research/RP004/RP004_FIXTURES.json
  - research/RP006/producer.py
  - research/RP006/verifier.py
  - research/RP006/recorded_attempt.py
  - research/RP006/recorded_worker.py
  - research/RP006/resources.py
  - tests/test_rp006_implementation.py
  - tests/test_rp006_supervisor.py
  - scripts/check-rp006-supervisor.py
relations:
  - relation: tests
    target: Q-3
  - relation: tests
    target: Q-4
package_ref: RP-006
protocol_ref: research/RP006/RP006_OPERATIONAL_PROTOCOL.md
target_refs: [Q-3, Q-4]
---

Pre-registered deterministic audit `TST-RP006001` over the six known RP004 event logs, three complete fields, all eight uniform masks, and the fixed FULL and TOPOLOGY_STATE query families. Its `tests` edges point to Q-3 (specified inquiry preservation) and Q-4 (recoverable realized-history distinctions), without claiming to resolve either question. `EXECUTION_FREEZE.json` binds the exact committed source inventory; D-0016 accepts the pre-execution review and this Test before the sole authorized attempt. The test covers finite-corpus sufficiency and inclusion-minimality only. Known RP004 and engineering-preflight classifications are disclosed; this is not blind confirmation or fresh evidence. Registration creates no Result and resolves no Cycle obligation.
