---
{
  "schema_version": "0.1",
  "id": "RP-005A",
  "type": "ResearchPackage",
  "title": "Constraints and viable futures",
  "created_at": "2026-10-08",
  "updated_at": "2026-10-11",
  "source_refs": [
    "baseline/v0.1/RP005A_PROTOCOL.md",
    "RESEARCH_EXECUTION_READINESS.md",
    "research/RP005A/RP005A_OPERATIONAL_PROTOCOL.md",
    "research/RP005A/RP005A_COLLISION_REVIEW.md",
    "research/RP005A/RP005A_PREPARATION_REVIEW.md",
    "research/RP005A/RP005A_FIXTURES.json",
    "research/RP005A/planning.py",
    "research/RP005A/RP005A_AUDIT_CONFIG.json",
    "research/RP005A/audit.py",
    "research/RP005A/replay.py",
    "research/RP005A/contract.py",
    "research/RP005A/RP005A_EXECUTION_REVIEW.md",
    "research/RP005A/audit-001/RECORD.md",
    "research/RP005A/RP005A_SOURCE_FREEZE.md",
    "research/RP005A/RP005A_SOURCE_FREEZE.json"
  ],
  "relations": [],
  "aliases": [
    "RP005A"
  ],
  "status": "PLANNED",
  "question_refs": [
    "Q-2"
  ],
  "scope": "Can targeted restrictions steer horizon-limited decisions away from states with fewer viable future targets? Removing edges does not expand raw structural reachability. Any benefit is conditional.",
  "protocol_ref": "baseline/v0.1/RP005A_PROTOCOL.md",
  "cycle_ref": "cycles/cycle-01/manifest.json"
}
---

The bounded saved-output audit and independent serialized replay are implemented and internally reviewed. TST-RP005A001 is registered before execution. All protocol choices and disclosed controls remain unchanged. RP005A stays PLANNED and Q-2 ACTIVE. No recorded attempt, Result, Claim or Cycle resolution exists. The reviewed source commit and sixteen exact input hashes are recorded in the source freeze. Next is one bounded recorded audit after this freeze is committed. Removing edges does not expand raw structural reachability; any policy benefit is conditional.
