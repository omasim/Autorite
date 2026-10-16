"""Stress bounded conflict-row streaming without lineage or answer data.

The child emits the inventory-derived maximum number of answer-free
placeholders to a capped JSONL file while checking its own 128 MiB RSS
ceiling. It demonstrates only that a streaming placeholder writer can keep
memory bounded at the proposed row count, not that the real producer and
independent verifier have the same end-to-end peak.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
MAX_ROWS = 1_077_936
MAX_RSS = 128 * 1024 * 1024


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    resource_caps = load("finite_lineage_stream_caps", ROOT / "scripts/check-finite-lineage-resource-shape.py")
    supervisor = load("finite_lineage_stream_supervisor", ROOT / "scripts/check-finite-lineage-execution-guard.py")
    if shutil.disk_usage("/private/tmp").free < 2 * 1024**3:
        raise RuntimeError("Need at least 2 GiB free for the temporary placeholder stream")
    worker = r'''
import importlib.util, json, pathlib, sys
root, output = map(pathlib.Path, sys.argv[1:])
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module
caps = load("stream_caps", root / "scripts/check-finite-lineage-resource-shape.py")
rp_resources = load("stream_rp_resources", root / "research/RP006/resources.py")
guard = rp_resources.Guard(seconds=60, memory_bytes=134217728)
def rows():
    for i in range(1077936):
        if i % 4096 == 0: guard()
        yield {"ordinal": i, "payload": "x" * 387}
count, size = caps.write_capped_jsonl(output, rows(), row_cap=448,
    file_cap=671088640, total_cap=671088640, total_before=0, row_count_cap=1077936)
measurement = guard()
print(json.dumps({"rows": count, "bytes": size, "rss": measurement["peak_process_rss_bytes"]}))
'''

    with tempfile.TemporaryDirectory(prefix="finite-lineage-stream-shape-", dir="/private/tmp") as temp:
        output = Path(temp) / "conflicts.jsonl"
        result = supervisor.supervise([sys.executable, "-c", worker, str(ROOT), str(output)],
                                      timeout_seconds=60)
        if result.get("status") != "COMPLETE":
            raise RuntimeError(f"Placeholder stream failed: {result.get('reason')}; {result.get('stderr')}")
        record = json.loads(result["stdout"])
        if record["rows"] != MAX_ROWS or record["rss"] > MAX_RSS:
            raise RuntimeError(f"Bounded placeholder stream violated count/RSS ceiling: {record}")
        if output.stat().st_size != record["bytes"] or record["bytes"] > resource_caps.MAX_EVIDENCE_BYTES:
            raise RuntimeError("Placeholder stream size disagrees with the capped writer")
        print(json.dumps({"status": "PASS", "purpose": "ANSWER_FREE_MAXIMUM_ROW_STREAM_RSS",
                          "candidate_inputs_read": False, "candidate_answers_generated": False,
                          "rows": record["rows"], "bytes": record["bytes"],
                          "worker_peak_rss_bytes": record["rss"],
                          "rss_limit_bytes": MAX_RSS, "temporary_artifacts_removed": True},
                         sort_keys=True))


if __name__ == "__main__":
    main()
