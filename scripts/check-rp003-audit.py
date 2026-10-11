"""Verify preserved evidence, input provenance and independent full-row replay."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research/RP003"))
from replay import replay

if __name__ == "__main__":
    run = ROOT / "research/RP003/runs/audit-20261011-001"
    manifest = json.loads((run / "manifest.json").read_text())
    assert set(manifest) == {"configuration", "seeds", "environment", "outputs"}
    assert {p.name for p in run.iterdir()} == set(manifest["outputs"]) | {"manifest.json"}
    for name, expected in manifest["outputs"].items():
        assert hashlib.sha256((run / name).read_bytes()).hexdigest() == expected, name
    frozen = json.loads((run / "frozen-inputs.json").read_text())
    assert frozen == {k: manifest[k] for k in ("configuration", "seeds", "environment")}
    config = manifest["configuration"]
    for name, expected in config["input_sha256"].items():
        original = subprocess.check_output(["git", "show", config["source_commit"] + ":" + name], cwd=ROOT)
        assert hashlib.sha256(original).hexdigest() == expected, name
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, name
    timing = json.loads((run / "timing.json").read_text())
    assert timing["status"] == "COMPLETE" and not (run / "failure.txt").exists()
    assert 0 <= timing["elapsed_monotonic_seconds"] <= config["config"]["wall_seconds"]
    assert 0 < timing["peak_resident_memory_bytes"] <= config["config"]["memory_bytes"]
    with (run / "paths.jsonl").open() as stream:
        summary = replay(stream, config["config"])
    assert summary == json.loads((run / "summary.json").read_text())
    audit = json.loads((run / "replay.json").read_text())
    assert audit == {"status": "PASS", "rows_verified": 11100, "fixtures_verified": 4,
                     "coverage_order_verified": True, "all_measurements_counts_and_first_witnesses_match": True}
    print(f"RP003 audit: {summary['path_count']} rows independently replayed; {len(manifest['outputs'])} output hashes and frozen inputs verified")
