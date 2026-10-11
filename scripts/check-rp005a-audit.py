"""Verify the reviewed implementation freeze and any preserved RP005A run."""
import hashlib
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from research.RP005A.contract import INPUTS, OUTPUTS, FREEZE_PATH
from research.RP005A.replay import canonical, strict_loads, check_config, replay


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_freeze(root=ROOT):
    freeze = strict_loads((root / FREEZE_PATH).read_text())
    assert set(freeze) == {"version", "source_commit", "input_sha256", "configuration"}
    assert freeze["version"] == "0.1" and set(freeze["input_sha256"]) == set(INPUTS)
    assert len(INPUTS) == 16 and len(set(INPUTS)) == 16
    source = freeze["source_commit"]
    assert isinstance(source, str) and len(source) == 40 and all(c in "0123456789abcdef" for c in source)
    check_config(freeze["configuration"])
    for name, expected in freeze["input_sha256"].items():
        original = subprocess.check_output(["git", "show", source + ":" + name], cwd=root)
        assert hashlib.sha256(original).hexdigest() == expected, name
        assert digest(root / name) == expected, name
    assert canonical(freeze["configuration"]) == canonical(strict_loads((root / "research/RP005A/RP005A_AUDIT_CONFIG.json").read_text()))
    return freeze


def check_run(run, root=ROOT):
    freeze = check_freeze(root)
    manifest = strict_loads((run / "manifest.json").read_text())
    assert set(manifest) == {"configuration", "seeds", "environment", "outputs"}
    configuration, config = manifest["configuration"], freeze["configuration"]
    assert set(configuration) == {"source_commit", "input_sha256", "config", "source_freeze_sha256",
                                  "command", "execution_authorization", "output_inventory"}
    assert configuration["source_commit"] == freeze["source_commit"]
    assert canonical(configuration["input_sha256"]) == canonical(freeze["input_sha256"])
    assert canonical(configuration["config"]) == canonical(config)
    assert configuration["source_freeze_sha256"] == digest(root / FREEZE_PATH)
    assert configuration["output_inventory"] == OUTPUTS
    note = configuration["execution_authorization"]
    assert isinstance(note, str) and note.strip()
    assert configuration["command"] == ["python3", "scripts/run-rp005a-audit.py", "--run-id", config["run_id"], "--authorization-note", note]
    assert run.name == config["run_id"]
    files = {p.name for p in run.iterdir()}
    assert {"manifest.json", "frozen-inputs.json", "timing.json"} <= files
    assert files <= set(OUTPUTS) | {"failure.txt"}
    assert set(manifest["outputs"]) == files - {"manifest.json"}
    for name, expected in manifest["outputs"].items():
        assert digest(run / name) == expected, name
    frozen = strict_loads((run / "frozen-inputs.json").read_text())
    assert canonical(frozen) == canonical({k: manifest[k] for k in ("configuration", "seeds", "environment")})
    assert canonical(manifest["seeds"]) == canonical(config["seeds"])
    environment = manifest["environment"]
    assert set(environment) == {"python", "os", "processes", "network", "peak_memory_units"}
    assert type(environment["processes"]) is int and environment["processes"] == 1
    assert environment["network"] == "none used by the audit" and environment["peak_memory_units"] == "bytes"
    assert tuple(map(int, environment["python"].split()[0].split(".")[:2])) >= (3, 11)
    timing = strict_loads((run / "timing.json").read_text())
    assert set(timing) == {"status", "started_at", "ended_at", "elapsed_monotonic_seconds", "peak_resident_memory_bytes"}
    assert type(timing["elapsed_monotonic_seconds"]) in (int, float)
    assert type(timing["peak_resident_memory_bytes"]) is int
    if timing["status"] == "INCOMPLETE":
        assert "failure.txt" in files and (run / "failure.txt").read_text().strip()
        assert timing["peak_resident_memory_bytes"] >= 0
        return {"status": "INCOMPLETE", "preserved_files": len(files)}
    assert timing["status"] == "COMPLETE" and files == set(OUTPUTS)
    assert 0 <= timing["elapsed_monotonic_seconds"] <= config["wall_seconds"]
    assert 0 < timing["peak_resident_memory_bytes"] <= config["memory_bytes"]
    fixtures = strict_loads((root / "research/RP005A/RP005A_FIXTURES.json").read_text())
    with (run / "planner.jsonl").open() as planners, (run / "pairs.jsonl").open() as pairs, (run / "structural.jsonl").open() as sources:
        summary = replay(planners, pairs, sources, fixtures, config)
    assert canonical(summary) == canonical(strict_loads((run / "summary.json").read_text()))
    verification = {"status": "PASS", "planner_rows_verified": 24,
        "paired_comparisons_verified": 12, "structural_sources_verified": 35,
        "ordered_pairs_per_inclusion_family_verified": 313,
        "coverage_order_types_and_all_values_verified": True,
        "disclosed_calibration": {"cases": 4, "planner_rows": 24, "paired_controls": 12, "inclusion_sources": 35}}
    assert canonical(verification) == canonical(strict_loads((run / "replay.json").read_text()))
    return {"status": "COMPLETE", "summary": summary}


if __name__ == "__main__":
    check_freeze()
    root = ROOT / "research/RP005A/runs"
    runs = sorted(root.iterdir()) if root.exists() else []
    completed, incomplete = 0, 0
    for run in runs:
        if not run.is_dir():
            raise ValueError("Unexpected RP005A run artifact")
        result = check_run(run)
        completed += result["status"] == "COMPLETE"
        incomplete += result["status"] == "INCOMPLETE"
    print(f"RP005A: 16 frozen input hashes verified; {completed} complete audits; {incomplete} preserved incomplete attempts")
