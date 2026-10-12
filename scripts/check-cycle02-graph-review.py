"""Reconstruct and verify Cycle 02's forward/backward graph review snapshot."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import yaml

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "cycles/cycle-02/reviews/CYCLE02_GRAPH_REVIEW_001.json"
REFERENCE = ROOT / "scripts/check-cycle01-graph-review.py"


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def make_snapshot(source_commit):
    if len(source_commit) != 40 or any(c not in "0123456789abcdef" for c in source_commit):
        raise ValueError("Full reviewed source commit required")
    spec = importlib.util.spec_from_file_location("cycle01_graph", REFERENCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    files = git("ls-tree", "-r", "--name-only", source_commit, "--", "graph", "research").decode().splitlines()
    records, provenance = {}, {}
    for name in files:
        if not ((name.startswith("graph/") and name.endswith(".md")) or name.endswith("/RECORD.md")):
            continue
        raw = git("show", f"{source_commit}:{name}")
        record = yaml.safe_load(raw.decode().split("---", 2)[1])
        identifier = record["id"]
        if identifier in records:
            raise ValueError(f"Duplicate historical ID: {identifier}")
        records[identifier] = record
        provenance[identifier] = {"path": name, "sha256": hashlib.sha256(raw).hexdigest()}
    manifest_raw = git("show", f"{source_commit}:cycles/cycle-02/manifest.json")
    return module.make_snapshot(records, provenance, json.loads(manifest_raw), source_commit,
                                hashlib.sha256(manifest_raw).hexdigest())


def verify(saved, expected):
    if json.dumps(saved, sort_keys=True, allow_nan=False) != json.dumps(expected, sort_keys=True, allow_nan=False):
        raise ValueError("Cycle 02 graph review differs from its committed source snapshot")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-from", help="Create a new exclusive snapshot; never overwrite")
    args = parser.parse_args()
    if args.write_from:
        snapshot = make_snapshot(args.write_from)
        ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
        with ARTIFACT.open("x") as stream:
            stream.write(json.dumps(snapshot, indent=2, sort_keys=True) + "\n")
    saved = json.loads(ARTIFACT.read_text())
    verify(saved, make_snapshot(saved["reviewed_source_commit"]))
    if saved["reviewed_source_commit"] not in git("rev-list", "HEAD").decode().splitlines():
        raise ValueError("Reviewed graph snapshot source is not in current ancestry")
    relative = ARTIFACT.relative_to(ROOT).as_posix()
    history = git("log", "--diff-filter=A", "--format=%H", "--", relative).decode().splitlines()
    if history and ARTIFACT.read_bytes() != git("show", f"{history[-1]}:{relative}"):
        raise ValueError("Committed Cycle 02 graph snapshot is immutable")
    spec = importlib.util.spec_from_file_location("schema", ROOT / "packages/research-schema/validate.py")
    schema = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(schema)
    schema.validate(ROOT)
    print(f"PASS: Cycle 02 graph: {len(saved['record_inputs'])} records, "
          f"{len(saved['declared_relations'])} declared relations, "
          f"{len(saved['typed_references'])} typed references, "
          f"{len(saved['backward_result_trace'])} Result traces; current schema/integrity passes.")


if __name__ == "__main__":
    main()
