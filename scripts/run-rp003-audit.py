"""One frozen deterministic audit; existing directories are never overwritten."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import platform
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research/RP003"))
from preservation import check_fixtures
from audit import enumerate_paths
from replay import check_config, independent_measure, replay

INPUTS = ["research/RP003/PROTOCOL.md", "research/RP003/FIXTURES.json",
          "research/RP003/RP003_COLLISION_REVIEW.md", "research/RP003/AUDIT_CONFIG.json",
          "research/RP003/preservation.py", "research/RP003/audit.py", "research/RP003/replay.py",
          "research/RP003/EXECUTION_REVIEW.md", "scripts/run-rp003-audit.py"]


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def utc():
    return datetime.now(timezone.utc).isoformat()


def memory():
    raw = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(raw if sys.platform == "darwin" else raw * 1024)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    config = json.loads((ROOT / "research/RP003/AUDIT_CONFIG.json").read_text())
    check_config(config)
    if args.run_id != config["run_id"] or sys.version_info < (3, 11):
        raise ValueError("Run ID or Python version mismatch")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"], cwd=ROOT).strip():
        raise ValueError("Tracked source must be committed before execution")
    hashes = {}
    for name in INPUTS:
        original = subprocess.check_output(["git", "show", commit + ":" + name], cwd=ROOT)
        if original != (ROOT / name).read_bytes():
            raise ValueError("Input differs from committed source: " + name)
        hashes[name] = digest(ROOT / name)
    directory = ROOT / "research/RP003/runs" / args.run_id
    directory.mkdir(parents=True, exist_ok=False)
    started, clock = utc(), time.monotonic()
    frozen = {"source_commit": commit, "input_sha256": hashes, "config": config,
              "command": ["python3", "scripts/run-rp003-audit.py", "--run-id", args.run_id],
              "execution_authorization": "User requested continuation of the published 11,100-path audit on 2026-10-11"}
    environment = {"python": sys.version, "os": platform.platform(), "processes": 1,
                   "network": "none used by the audit", "peak_memory_units": "bytes"}
    manifest = {"configuration": frozen, "seeds": config["seeds"], "environment": environment, "outputs": {}}
    # This exact frozen input snapshot exists before any research output is calculated.
    write(directory / "manifest.json", manifest)
    write(directory / "frozen-inputs.json", {"configuration": frozen, "seeds": config["seeds"], "environment": environment})

    def guard():
        if time.monotonic() - clock > config["wall_seconds"] or memory() > config["memory_bytes"]:
            raise RuntimeError("Declared resource budget exceeded")

    def timeout(*_):
        raise TimeoutError("60-second audit limit")

    status = "INCOMPLETE"
    try:
        signal.signal(signal.SIGALRM, timeout)
        signal.setitimer(signal.ITIMER_REAL, config["wall_seconds"])
        fixtures = json.loads((ROOT / "research/RP003/FIXTURES.json").read_text())
        check_fixtures(fixtures)
        for case in fixtures["cases"]:
            if independent_measure(case["states"]) != case["expected"]:
                raise ValueError("Independent fixture replay failed")
        with (directory / "paths.jsonl").open("x") as stream:
            summary = enumerate_paths(config, stream, guard)
        with (directory / "paths.jsonl").open() as stream:
            verified = replay(stream, config, guard)
        if summary != verified or summary["path_count"] != config["expected_path_count"]:
            raise ValueError("Independent aggregate/witness mismatch")
        write(directory / "summary.json", summary)
        write(directory / "replay.json", {"status": "PASS", "rows_verified": verified["path_count"],
                                          "fixtures_verified": 4, "coverage_order_verified": True,
                                          "all_measurements_counts_and_first_witnesses_match": True})
        guard()
        status = "COMPLETE"
    except Exception as exc:
        (directory / "failure.txt").write_text(type(exc).__name__ + ": " + str(exc) + "\n")
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        write(directory / "timing.json", {"status": status, "started_at": started, "ended_at": utc(),
                                          "elapsed_monotonic_seconds": time.monotonic() - clock,
                                          "peak_resident_memory_bytes": memory()})
        manifest["outputs"] = {p.name: digest(p) for p in sorted(directory.iterdir()) if p.name != "manifest.json"}
        write(directory / "manifest.json", manifest)
    print(json.dumps({"run": args.run_id, "status": status, "source_commit": commit}))
    if status != "COMPLETE":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
