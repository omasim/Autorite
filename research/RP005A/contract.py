"""File inventories only; no shared planner, scoring or reachability logic."""
INPUTS = ["research/RP005A/" + name for name in (
    "RP005A_OPERATIONAL_PROTOCOL.md", "RP005A_FIXTURES.json", "planning.py",
    "RP005A_COLLISION_REVIEW.md", "RP005A_PREPARATION_REVIEW.md",
    "RP005A_AUDIT_CONFIG.json", "audit.py", "replay.py", "contract.py",
    "RP005A_EXECUTION_REVIEW.md", "audit-001/RECORD.md")]
INPUTS += ["scripts/run-rp005a-audit.py", "scripts/check-rp005a-audit.py",
           "scripts/check-rp005a-preparation.py", "tests/test_rp005a_planning.py",
           "tests/test_rp005a_audit.py"]
OUTPUTS = ["manifest.json", "frozen-inputs.json", "planner.jsonl", "pairs.jsonl",
           "structural.jsonl", "summary.json", "replay.json", "timing.json"]
FREEZE_PATH = "research/RP005A/RP005A_SOURCE_FREEZE.json"
