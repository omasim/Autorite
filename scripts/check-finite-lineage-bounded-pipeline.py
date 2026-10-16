"""Toy-only end-to-end check for the bounded finite-lineage pipeline.

This uses two synthetic three-entity cases. It exercises row-at-a-time
conflict emission, a separately implemented streaming replay, and capped
package writing. It is not a Cycle 03 run and its answer-bearing toy artifacts
are removed without inspecting the answers or classifications.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
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


def jsonl(path: Path):
    with path.open("r", encoding="utf-8") as stream:
        for line in stream:
            yield json.loads(line)


def main() -> None:
    verifier = load("finite_lineage_bounded_verifier", ROOT / "research/RP006/verifier.py")
    producer = load("finite_lineage_bounded_producer", ROOT / "research/RP006/producer.py")
    writer = load("finite_lineage_bounded_writer", ROOT / "research/preparation/finite_lineage_writer.py")
    guard = load("finite_lineage_bounded_guard", ROOT / "scripts/check-finite-lineage-execution-guard.py")
    resources = load("finite_lineage_bounded_resources", ROOT / "research/RP006/resources.py")
    if shutil.disk_usage("/private/tmp").free < 2 * 1024**3:
        raise RuntimeError("Need at least 2 GiB free for the bounded toy pipeline")
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
    sink_calls = []
    try:
        producer.produce(domain, retain_conflicts=False, conflict_sink=sink_calls.append)
    except ValueError:
        pass
    else:
        raise RuntimeError("Bounded producer accepted an unspecified stratum")
    try:
        producer.produce(domain, retain_conflicts=False, conflict_sink=sink_calls.append, stratum="F4")
    except ValueError:
        pass
    else:
        raise RuntimeError("Bounded producer accepted a non-F4 inventory in the F4 stratum")
    if sink_calls:
        raise RuntimeError("Invalid stratum validation emitted a witness")

    worker = r'''
import hashlib, importlib.util, json, pathlib, resource, sys
root, domain_file, bundle_file, conflict_file = map(pathlib.Path, sys.argv[1:])
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module
producer = load("bounded_worker_producer", root / "research/RP006/producer.py")
writer = load("bounded_worker_writer", root / "research/preparation/finite_lineage_writer.py")
domain = json.loads(domain_file.read_text(encoding="utf-8"))
rp_resources = load("bounded_worker_resources", root / "research/RP006/resources.py")
guard = rp_resources.Guard(seconds=60, memory_bytes=134217728)
sink = writer.CappedJsonlSink(conflict_file, guard=guard)
try:
    bundle = producer.produce(domain, guard=guard, retain_conflicts=False, conflict_sink=sink, stratum="TOY")
except BaseException:
    sink.close(complete=False)
    raise
count, _size = sink.close(complete=True)
bundle["conflicts"] = []
bundle_file.write_text(json.dumps(bundle, sort_keys=True, separators=(",", ":"), allow_nan=False), encoding="utf-8")
print(json.dumps({"conflict_rows": count, "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (1 if sys.platform == "darwin" else 1024)}))
'''

    with tempfile.TemporaryDirectory(prefix="autorite-finite-lineage-bounded-") as temp:
        root = Path(temp)
        domain_file = root / "domain.json"
        bundle_file = root / "small-bundle.json"
        conflict_file = root / "conflicts.jsonl"
        output = root / "package"
        domain_file.write_text(json.dumps(domain, sort_keys=True), encoding="utf-8")
        supervised = guard.supervise([sys.executable, "-c", worker, str(ROOT), str(domain_file),
                                      str(bundle_file), str(conflict_file)], timeout_seconds=30)
        if supervised.get("status") != "COMPLETE":
            raise RuntimeError(f"Bounded worker failed: {supervised.get('reason')}; {supervised.get('stderr')}")
        worker_record = json.loads(supervised["stdout"])
        if worker_record["peak_rss_bytes"] >= 128 * 1024 * 1024:
            raise RuntimeError("Toy bounded worker exceeded 128 MiB RSS")
        bundle = json.loads(bundle_file.read_text(encoding="utf-8"))
        if bundle.get("conflicts") != []:
            raise RuntimeError("Worker retained conflicts in the small bundle")
        parent_guard = resources.Guard(seconds=30, memory_bytes=128 * 1024 * 1024)
        try:
            verifier.verify_bounded(bundle, conflict_file, domain,
                                    guard=parent_guard, stratum="F4")
        except ValueError:
            pass
        else:
            raise RuntimeError("Independent verifier accepted a non-F4 inventory in the F4 stratum")
        verified = verifier.verify_bounded(bundle, conflict_file, domain, guard=parent_guard,
                                           stratum="TOY")
        if verified.get("status") != "PASS":
            raise RuntimeError("Streaming independent verifier failed")
        if verified["counts"]["conflict_rows"] != worker_record["conflict_rows"]:
            raise RuntimeError("Summary witness count differs from the streamed conflict inventory")
        if sum(v["conflict_rows"] for v in verified["counts"]["families"].values()) != worker_record["conflict_rows"]:
            raise RuntimeError("Family witness counts differ from the streamed conflict inventory")
        tampered = root / "tampered-conflicts.jsonl"
        lines = conflict_file.read_text(encoding="utf-8").splitlines()
        if not lines:
            raise RuntimeError("Toy fixture must exercise at least one witness")
        lines[0] = lines[0].replace('"ordinal":0', '"ordinal":99', 1)
        tampered.write_text("\n".join(lines) + "\n", encoding="utf-8")
        try:
            verifier.verify_bounded(bundle, tampered, domain,
                                    guard=resources.Guard(seconds=30, memory_bytes=128 * 1024 * 1024),
                                    stratum="TOY")
        except ValueError:
            pass
        else:
            raise RuntimeError("Independent verifier accepted a tampered streamed witness")
        bundle["conflicts"] = jsonl(conflict_file)
        source_paths = [ROOT / "research/RP006/producer.py", ROOT / "research/RP006/verifier.py",
                        ROOT / "research/preparation/finite_lineage_writer.py",
                        ROOT / "scripts/check-finite-lineage-bounded-pipeline.py"]
        source_hashes = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                         for path in source_paths}
        source_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        try:
            writer.write_bundle(root / "wrong-stratum-package", domain, bundle, verified,
                                source_hashes, stratum="F4", source_commit=source_commit,
                                guard=resources.Guard(seconds=30, memory_bytes=128 * 1024 * 1024))
        except ValueError:
            pass
        else:
            raise RuntimeError("Package writer accepted a non-F4 inventory in the F4 stratum")
        if not (root / "wrong-stratum-package" / "INCOMPLETE.json").is_file():
            raise RuntimeError("Rejected stratum did not preserve an INCOMPLETE receipt")
        packaged = writer.write_bundle(output, domain, bundle, verified, source_hashes,
                                       stratum="TOY", source_commit=source_commit,
                                       guard=parent_guard)
        if packaged["status"] != "COMPLETE":
            raise RuntimeError("Bounded toy package did not complete")
        manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
        if manifest["evidence"]["jsonl"]["conflicts.jsonl"]["rows"] != worker_record["conflict_rows"]:
            raise RuntimeError("Streamed conflict count differs across worker/verifier/writer")
        print(json.dumps({"status": "PASS", "purpose": "TOY_BOUNDED_PRODUCER_VERIFIER_WRITER",
                          "candidate_inputs_read": False, "candidate_answers_generated": False,
                          "conflict_rows": worker_record["conflict_rows"],
                          "worker_peak_rss_bytes": worker_record["peak_rss_bytes"],
                          "package_bytes": packaged["total_bytes"],
                          "temporary_artifacts_removed": True}, sort_keys=True))


if __name__ == "__main__":
    main()
