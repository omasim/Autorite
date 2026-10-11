"""Validate disclosed engineering expectations only; never creates a run."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("rp005a", ROOT / "research/RP005A/planning.py")
rp005a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rp005a)

if __name__ == "__main__":
    config = json.loads((ROOT / "research/RP005A/RP005A_FIXTURES.json").read_text())
    result = rp005a.check_fixtures(config)
    record = (ROOT / "research/RP005A/RECORD.md").read_text()
    for name in ("RP005A_OPERATIONAL_PROTOCOL.md", "RP005A_COLLISION_REVIEW.md",
                 "RP005A_PREPARATION_REVIEW.md", "RP005A_FIXTURES.json", "planning.py"):
        assert (ROOT / "research/RP005A" / name).is_file()
        assert "research/RP005A/" + name in record
    print("RP005A disclosed preparation only: " + json.dumps(result, sort_keys=True))
