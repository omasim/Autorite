"""Check disclosed RP004 controls only; creates no run, Test or Result."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("rp004", ROOT / "research/RP004/lineage.py")
rp004 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rp004)

if __name__ == "__main__":
    config = json.loads((ROOT / "research/RP004/RP004_FIXTURES.json").read_text())
    assert config["version"] == "0.1"
    assert len(config["collision_controls"]) == 3
    for case in config["cases"]:
        assert len(case["controls"]) == 9
        assert {x["query"]["kind"] for x in case["controls"]} == set(rp004.QUERIES)
    result = rp004.check_fixtures(config)
    record = (ROOT / "research/RP004/RECORD.md").read_text()
    for name in ("RP004_OPERATIONAL_PROTOCOL.md", "RP004_COLLISION_REVIEW.md", "RP004_PREPARATION_REVIEW.md", "RP004_FIXTURES.json", "lineage.py"):
        assert (ROOT / "research/RP004" / name).is_file()
        assert "research/RP004/" + name in record
    print("RP004 disclosed calibration only: " + json.dumps(result, sort_keys=True))
