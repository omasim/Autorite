"""Reconstruct a historical structural graph review; never infer scientific support."""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess

import yaml

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "cycles/cycle-01/reviews/GRAPH_REVIEW_001.json"
REFERENCE_FIELDS = ("question_refs", "target_refs", "package_ref", "test_ref", "affected_refs",
                    "assumption_refs", "invalidation_decision_ref")


def make_snapshot(records, provenance, manifest, source_commit, manifest_sha256):
    """Separate declared semantic relations from typed storage references."""
    relations, references = [], []
    for identifier, record in sorted(records.items()):
        for edge in record["relations"]:
            if edge["target"] not in records:
                raise ValueError("Unknown relation target")
            relations.append({"source": identifier, **edge})
        for field in REFERENCE_FIELDS:
            values = record.get(field, [])
            if isinstance(values, str):
                values = [values]
            for target in values:
                if target not in records:
                    raise ValueError("Unknown typed reference")
                references.append({"source": identifier, "field": field, "target": target})
    relations.sort(key=lambda e: (e["source"], e["relation"], e["target"]))
    references.sort(key=lambda e: (e["source"], e["field"], e["target"]))
    questions = []
    for identifier, record in sorted(records.items()):
        if record["type"] != "Question":
            continue
        packages = sorted(k for k, d in records.items() if identifier in d.get("question_refs", []))
        tests = sorted(k for k, d in records.items() if d["type"] == "Test" and identifier in d["target_refs"])
        results = sorted(k for k, d in records.items() if d["type"] == "Result" and d["test_ref"] in tests)
        direct = sorted(e["source"] for e in relations if e["relation"] == "informs" and e["target"] == identifier)
        questions.append({"id": identifier, "status": record["status"], "packages": packages,
                          "tests": tests, "results_via_test_ref": results, "declared_informs": direct})
    backward = []
    for identifier, record in sorted(records.items()):
        if record["type"] != "Result":
            continue
        test = records[record["test_ref"]]
        if test["type"] != "Test" or test["package_ref"] != record["package_ref"]:
            raise ValueError("Result/Test/package mismatch")
        backward.append({"result": identifier, "status": record["status"], "test": test["id"],
                         "package": record["package_ref"], "question_or_claim_targets": test["target_refs"],
                         "protocol_ref": test["protocol_ref"], "run_ref": record["run_ref"],
                         "artifact_refs": record["artifact_refs"]})
    ledger = []
    for obligation in manifest["obligations"]:
        if obligation["resolved"]:
            ledger.append({k: obligation[k] for k in ("key", "resolution", "decision_ref", "evidence_refs")})
    incoming = {identifier: {"relations": [e for e in relations if e["target"] == identifier],
                            "typed_references": [e for e in references if e["target"] == identifier]}
                for identifier in sorted(records)}
    return {"version": "0.1", "reviewed_source_commit": source_commit,
            "cycle_manifest_sha256": manifest_sha256, "record_inputs": provenance,
            "type_counts": dict(sorted(Counter(d["type"] for d in records.values()).items())),
            "declared_relations": relations, "typed_references": references,
            "incoming_index": incoming, "forward_question_trace": questions,
            "backward_result_trace": backward, "resolved_obligation_evidence": ledger,
            "no_automatic_transitive_inference": True}


def reconstruct(source_commit, root=ROOT):
    if not re.fullmatch(r"[0-9a-f]{40}", source_commit):
        raise ValueError("Full reviewed source commit required")
    def git(*args):
        return subprocess.check_output(["git", *args], cwd=root)
    files = git("ls-tree", "-r", "--name-only", source_commit, "--", "graph", "research").decode().splitlines()
    records, provenance = {}, {}
    for name in files:
        if not ((name.startswith("graph/") and name.endswith(".md")) or name.endswith("/RECORD.md")):
            continue
        raw = git("show", source_commit + ":" + name)
        record = yaml.safe_load(raw.decode().split("---", 2)[1])
        identifier = record["id"]
        if identifier in records:
            raise ValueError("Duplicate historical ID")
        records[identifier] = record
        provenance[identifier] = {"path": name, "sha256": hashlib.sha256(raw).hexdigest()}
    raw = git("show", source_commit + ":cycles/cycle-01/manifest.json")
    return make_snapshot(records, provenance, json.loads(raw), source_commit, hashlib.sha256(raw).hexdigest())


def verify_snapshot(saved, expected):
    if json.dumps(saved, sort_keys=True, allow_nan=False) != json.dumps(expected, sort_keys=True, allow_nan=False):
        raise ValueError("Historical graph review differs from committed source")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-from", help="Create a new exclusive snapshot; never overwrite")
    args = parser.parse_args()
    if args.write_from:
        snapshot = reconstruct(args.write_from)
        ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
        with ARTIFACT.open("x") as stream:
            stream.write(json.dumps(snapshot, indent=2, sort_keys=True) + "\n")
    saved = json.loads(ARTIFACT.read_text())
    verify_snapshot(saved, reconstruct(saved["reviewed_source_commit"]))
    relative = ARTIFACT.relative_to(ROOT).as_posix()
    history = subprocess.check_output(["git", "log", "--diff-filter=A", "--format=%H", "--", relative], cwd=ROOT).decode().splitlines()
    if history:
        original = subprocess.check_output(["git", "show", history[-1] + ":" + relative], cwd=ROOT)
        if ARTIFACT.read_bytes() != original:
            raise ValueError("Committed historical graph snapshot is immutable")
    # Current schema/integrity is a separate check, not a historical status rewrite.
    spec = importlib.util.spec_from_file_location("schema", ROOT / "packages/research-schema/validate.py")
    schema = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(schema)
    schema.validate(ROOT)
    print(f"PASS: historical graph review: {len(saved['record_inputs'])} records, "
          f"{len(saved['declared_relations'])} declared relations, "
          f"{len(saved['typed_references'])} typed references, "
          f"{len(saved['backward_result_trace'])} Result provenance traces; current schema/integrity passes.")


if __name__ == "__main__":
    main()
