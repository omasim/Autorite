"""One reviewed RP005A attempt with pinned inputs; never overwrites a run."""
import argparse
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import platform
import resource
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from research.RP005A.contract import INPUTS, OUTPUTS, FREEZE_PATH
from research.RP005A.planning import check_fixtures
from research.RP005A.audit import iter_planner, iter_pairs, iter_structural, summarize, write_jsonl
from research.RP005A.replay import canonical, check_config, strict_loads, replay


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(canonical(value) + "\n")


def utc():
    return datetime.now(timezone.utc).isoformat()


def memory():
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(peak if sys.platform == "darwin" else peak * 1024)


def verify_freeze(root, freeze):
    if (set(freeze) != {"version", "source_commit", "input_sha256", "configuration"}
            or freeze["version"] != "0.1" or set(freeze["input_sha256"]) != set(INPUTS)
            or not isinstance(freeze["source_commit"], str)
            or len(freeze["source_commit"]) != 40
            or any(c not in "0123456789abcdef" for c in freeze["source_commit"])):
        raise ValueError("Reviewed source freeze inventory")
    check_config(freeze["configuration"])
    for name, expected in freeze["input_sha256"].items():
        source = subprocess.check_output(["git", "show", freeze["source_commit"] + ":" + name], cwd=root)
        if hashlib.sha256(source).hexdigest() != expected or digest(root / name) != expected:
            raise ValueError("Input differs from reviewed freeze: " + name)
    if canonical(strict_loads((root / "research/RP005A/RP005A_AUDIT_CONFIG.json").read_text())) != canonical(freeze["configuration"]):
        raise ValueError("Frozen configuration source mismatch")
    return freeze["source_commit"], freeze["input_sha256"]


def preflight(run_id, authorization_note):
    if sys.version_info < (3, 11):
        raise ValueError("Python >=3.11 required")
    if not isinstance(authorization_note, str) or not authorization_note.strip():
        raise ValueError("Record the actual execution authorization")
    freeze = strict_loads((ROOT / FREEZE_PATH).read_text())
    if run_id != freeze["configuration"]["run_id"]:
        raise ValueError("Run ID mismatch")
    if subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"], cwd=ROOT).strip():
        raise ValueError("Tracked source must be committed")
    committed_freeze = subprocess.check_output(["git", "show", "HEAD:" + FREEZE_PATH], cwd=ROOT)
    if committed_freeze != (ROOT / FREEZE_PATH).read_bytes():
        raise ValueError("Source freeze must be committed")
    verify_freeze(ROOT, freeze)
    if (ROOT / "research/RP005A/runs" / run_id).exists():
        raise ValueError("Existing run directory; no overwrite or automatic retry")
    return freeze


def execute(directory, freeze, authorization_note, clock=time.monotonic, resident=memory):
    """Used only after preflight; injected clocks support engineering failure tests."""
    config = freeze["configuration"]
    directory.mkdir(parents=True, exist_ok=False)
    started, begin = utc(), clock()
    configuration = {"source_commit": freeze["source_commit"], "input_sha256": freeze["input_sha256"],
                     "config": config, "source_freeze_sha256": digest(ROOT / FREEZE_PATH),
                     "command": ["python3", "scripts/run-rp005a-audit.py", "--run-id", config["run_id"],
                                 "--authorization-note", authorization_note],
                     "execution_authorization": authorization_note, "output_inventory": OUTPUTS}
    manifest = {"configuration": configuration, "seeds": config["seeds"],
                "environment": {"python": sys.version, "os": platform.platform(), "processes": 1,
                                "network": "none used by the audit", "peak_memory_units": "bytes"},
                "outputs": {}}
    status = "INCOMPLETE"
    previous_alarm = signal.getsignal(signal.SIGALRM)

    def guard():
        if clock() - begin > config["wall_seconds"] or resident() > config["memory_bytes"]:
            raise RuntimeError("Declared resource budget exceeded")

    def timeout(*_):
        raise TimeoutError("60-second RP005A audit limit")

    try:
        write(directory / "manifest.json", manifest)
        write(directory / "frozen-inputs.json", {k: manifest[k] for k in ("configuration", "seeds", "environment")})
        signal.signal(signal.SIGALRM, timeout)
        signal.setitimer(signal.ITIMER_REAL, max(0.001, config["wall_seconds"] - (clock() - begin)))
        guard()
        fixtures = strict_loads((ROOT / "research/RP005A/RP005A_FIXTURES.json").read_text())
        calibration = check_fixtures(fixtures)
        saved = []
        for name, generate in (("planner.jsonl", iter_planner), ("pairs.jsonl", iter_pairs),
                               ("structural.jsonl", iter_structural)):
            rows = []
            with (directory / name).open("x") as stream:
                for row in generate(fixtures, config, guard):
                    write_jsonl(stream, row)
                    rows.append(row)
            saved.append(rows)
        summary = summarize(*saved, config)
        with (directory / "planner.jsonl").open() as planners, (directory / "pairs.jsonl").open() as pairs, (directory / "structural.jsonl").open() as sources:
            independently = replay(planners, pairs, sources, fixtures, config, guard)
        if canonical(summary) != canonical(independently):
            raise ValueError("Independent aggregate mismatch")
        write(directory / "summary.json", summary)
        write(directory / "replay.json", {"status": "PASS", "planner_rows_verified": 24,
              "paired_comparisons_verified": 12, "structural_sources_verified": 35,
              "ordered_pairs_per_inclusion_family_verified": 313,
              "coverage_order_types_and_all_values_verified": True, "disclosed_calibration": calibration})
        guard()
        status = "COMPLETE"
    except Exception as exc:
        (directory / "failure.txt").write_text(type(exc).__name__ + ": " + str(exc) + "\n")
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous_alarm)
        elapsed, peak = clock() - begin, resident()
        if elapsed < 0 or elapsed > config["wall_seconds"] or not 0 < peak <= config["memory_bytes"]:
            status = "INCOMPLETE"
            with (directory / "failure.txt").open("a") as failed:
                failed.write("Final resource check failed\n")
        write(directory / "timing.json", {"status": status, "started_at": started, "ended_at": utc(),
              "elapsed_monotonic_seconds": elapsed, "peak_resident_memory_bytes": peak})
        manifest["outputs"] = {p.name: digest(p) for p in sorted(directory.iterdir()) if p.name != "manifest.json"}
        write(directory / "manifest.json", manifest)
    return status


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--authorization-note", required=True)
    args = parser.parse_args()
    freeze = preflight(args.run_id, args.authorization_note)
    status = execute(ROOT / "research/RP005A/runs" / args.run_id, freeze, args.authorization_note)
    print(canonical({"run": args.run_id, "status": status, "source_commit": freeze["source_commit"]}))
    if status != "COMPLETE":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
