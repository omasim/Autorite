"""Exercise RP006 producer -> independent verifier -> capped writer on toy data.

This is a software integration check only. Its temporary three-entity domain
is not a proposed Cycle 03 case; outputs are checked for integrity and removed
without inspecting query answers or sufficiency/conflict findings.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def event(kind, parents, *outputs):
    return {"kind": kind, "parents": list(parents), "outputs": [
        {"id": ident, "state": state} for ident, state in outputs
    ]}


def main() -> None:
    producer = load("finite_lineage_toy_producer", ROOT / "research/RP006/producer.py")
    verifier = load("finite_lineage_toy_verifier", ROOT / "research/RP006/verifier.py")
    writer = load("finite_lineage_toy_writer", ROOT / "research/preparation/finite_lineage_writer.py")
    guard = load("finite_lineage_toy_guard", ROOT / "scripts/check-finite-lineage-execution-guard.py")
    domain = {"cases": [
        {"id": "TOY-01", "events": [
            event("root", [], ("a", "A")), event("continue", ["a"], ("b", "B")),
            event("root", [], ("c", "C")),
        ]},
        {"id": "TOY-02", "events": [
            event("root", [], ("a", "A")), event("copy", ["a"], ("b", "A")),
            event("root", [], ("c", "C")),
        ]},
    ]}
    del producer  # The actual producer executes inside the supervised child below.

    producer_child = r'''
import importlib.util, json, pathlib, sys
root, domain_path, bundle_path = map(pathlib.Path, sys.argv[1:])
spec = importlib.util.spec_from_file_location("toy_worker_producer", root / "research/RP006/producer.py")
producer = importlib.util.module_from_spec(spec); spec.loader.exec_module(producer)
domain = json.loads(domain_path.read_text(encoding="utf-8"))
bundle = producer.produce(domain)
bundle_path.write_text(json.dumps(bundle, sort_keys=True, separators=(",", ":"), allow_nan=False), encoding="utf-8")
'''

    with tempfile.TemporaryDirectory(prefix="autorite-finite-lineage-writer-") as temp:
        output = Path(temp) / "package"
        domain_path = Path(temp) / "toy-domain.json"
        bundle_path = Path(temp) / "toy-bundle.json"
        domain_path.write_text(json.dumps(domain, sort_keys=True), encoding="utf-8")
        supervised = guard.supervise([sys.executable, "-c", producer_child,
                                      str(ROOT), str(domain_path), str(bundle_path)],
                                     timeout_seconds=30)
        if supervised.get("status") != "COMPLETE" or not bundle_path.is_file():
            raise RuntimeError(f"Supervised synthetic producer failed: {supervised.get('reason')}")
        bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
        replay = verifier.verify(bundle, domain)
        if replay.get("status") != "PASS":
            raise RuntimeError("Toy domain did not pass the independent RP006 verifier")

        source_paths = [ROOT / "research/RP006/producer.py",
                        ROOT / "research/RP006/verifier.py",
                        ROOT / "research/preparation/finite_lineage_writer.py",
                        ROOT / "scripts/check-finite-lineage-execution-guard.py"]
        source_hashes = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                         for path in source_paths}
        result = writer.write_bundle(output, domain, bundle, replay, source_hashes,
                                     stratum="TOY", source_commit="0" * 40)
        if result["status"] != "COMPLETE":
            raise RuntimeError("Toy package was not completed")
        manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
        receipt = json.loads((output / "verifier-receipt.json").read_text(encoding="utf-8"))
        if manifest["status"] != "COMPLETE" or receipt["status"] != "PASS":
            raise RuntimeError("Terminal package records are invalid")
        if receipt["manifest_sha256"] != hashlib.sha256((output / "manifest.json").read_bytes()).hexdigest():
            raise RuntimeError("Verifier receipt does not bind exact manifest bytes")
        for name, record in manifest["evidence"]["jsonl"].items():
            path = output / name
            if hashlib.sha256(path.read_bytes()).hexdigest() != record["sha256"]:
                raise RuntimeError(f"Manifest hash mismatch for {name}")
        if result["total_bytes"] > writer.TOTAL_CAP:
            raise RuntimeError("Writer exceeded the configured total evidence cap")
        print(json.dumps({"status": "PASS", "purpose": "SUPERVISED_SYNTHETIC_PRODUCER_VERIFIER_WRITER_INTEGRATION",
                          "candidate_inputs_read": False, "candidate_answers_generated": False,
                          "supervisor": "process-group/deadline/log controls passed",
                          "toy_rows_written": sum(r["rows"] for r in manifest["evidence"]["jsonl"].values()),
                          "total_bytes": result["total_bytes"], "temporary_artifacts_removed": True},
                         sort_keys=True))


if __name__ == "__main__":
    main()
