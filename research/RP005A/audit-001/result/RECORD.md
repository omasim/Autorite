---
{
  "schema_version": "0.1",
  "id": "R-RP005A001",
  "type": "Result",
  "title": "Audited finite restrictions and horizon-limited planning",
  "created_at": "2026-10-11",
  "updated_at": "2026-10-11",
  "source_refs": [
    "research/RP005A/RP005A_AUDIT_001_REPORT.md",
    "research/RP005A/RP005A_OPERATIONAL_PROTOCOL.md",
    "research/RP005A/RP005A_EXECUTION_REVIEW.md",
    "research/RP005A/RP005A_SOURCE_FREEZE.md"
  ],
  "relations": [
    {
      "relation": "informs",
      "target": "Q-2"
    }
  ],
  "status": "VALID",
  "test_ref": "TST-RP005A001",
  "package_ref": "RP-005A",
  "run_ref": "research/RP005A/runs/audit-20261011-001",
  "artifact_refs": [
    "research/RP005A/runs/audit-20261011-001/manifest.json",
    "research/RP005A/runs/audit-20261011-001/frozen-inputs.json",
    "research/RP005A/runs/audit-20261011-001/planner.jsonl",
    "research/RP005A/runs/audit-20261011-001/pairs.jsonl",
    "research/RP005A/runs/audit-20261011-001/structural.jsonl",
    "research/RP005A/runs/audit-20261011-001/summary.json",
    "research/RP005A/runs/audit-20261011-001/replay.json",
    "research/RP005A/runs/audit-20261011-001/timing.json"
  ],
  "observations": "24 planner rows, 12 paired comparisons and 35 structural sources independently replayed. Two positive, four zero and six negative comparisons: V1 gains +1/5 at H=1/2, with zero at H=4; V0 is zero at all horizons; V2 and C0 lose -1/5 at all horizons. Raw and B=3 edge-removal inclusion pass for 313 ordered pairs each. Counts describe four predeclared deterministic constructions and correlated horizon controls, not empirical frequencies, universal restriction benefit, viability kernels, novelty or confidence estimates."
}
---

Explicit internal outcome review accepts the scoped evidence of TST-RP005A001 as VALID after complete source/input provenance, resource checks, output hashes and independent full-value replay. The informs edge to Q-2 concerns resource-bounded target options, truncated reward selection and pure edge-removal inclusion. Q-2 remains ACTIVE. No broad Claim, package disposition or Cycle obligation resolution follows.
