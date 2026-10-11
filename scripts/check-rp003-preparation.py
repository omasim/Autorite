"""Known-answer calibration only. Does not enumerate or create research artifacts."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("rp003", ROOT / "research/RP003/preservation.py")
rp003 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rp003)

if __name__ == "__main__":
    config = json.loads((ROOT / "research/RP003/FIXTURES.json").read_text())
    count = rp003.check_fixtures(config)
    record = (ROOT / "research/RP003/RECORD.md").read_text()
    for name in ("PROTOCOL.md", "PRIOR_ART_REVIEW.md", "PREPARATION_REVIEW.md"):
        assert (ROOT / "research/RP003" / name).is_file()
        assert "research/RP003/" + name in record
    print(f"RP003 preparation: {count} known-answer fixtures verified; no enumeration or Result")
