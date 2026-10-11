---
{
  "schema_version": "0.1",
  "id": "R-RP003001",
  "type": "Result",
  "title": "Audited finite local-to-global preservation enumeration",
  "created_at": "2026-10-11",
  "updated_at": "2026-10-11",
  "source_refs": [
    "research/RP003/AUDIT_001_REPORT.md",
    "research/RP003/PROTOCOL.md",
    "research/RP003/EXECUTION_REVIEW.md"
  ],
  "relations": [
    {
      "relation": "informs",
      "target": "Q-0"
    }
  ],
  "status": "VALID",
  "test_ref": "TST-RP003001",
  "package_ref": "RP-003",
  "run_ref": "research/RP003/runs/audit-20261011-001",
  "artifact_refs": [
    "research/RP003/runs/audit-20261011-001/manifest.json",
    "research/RP003/runs/audit-20261011-001/frozen-inputs.json",
    "research/RP003/runs/audit-20261011-001/paths.jsonl",
    "research/RP003/runs/audit-20261011-001/summary.json",
    "research/RP003/runs/audit-20261011-001/replay.json",
    "research/RP003/runs/audit-20261011-001/timing.json"
  ],
  "observations": "11,100 complete ordered paths independently replayed. Tolerance local-to-endpoint has 848 failures among 5,396 eligible paths; local-to-prefix has 1,136 among 5,396. Exact local-to-endpoint/local-to-prefix and variation-budget-to-prefix controls have zero failures. Counts and first witnesses apply only to the declared finite grid and path lengths. No statistical, novelty, metaphysical identity or arbitrary-domain conclusion."
}
---

Audited result of TST-RP003001 in RP-003. The informs edge to Q-0 attaches finite evidence about specified preservation criteria; it does not resolve the foundational question. Every saved row and witness was independently replayed, with frozen inputs and output hashes verified. VALID accepts the scoped evidence after internal interpretation review; it is not a broad Claim, package disposition or Cycle resolution.
