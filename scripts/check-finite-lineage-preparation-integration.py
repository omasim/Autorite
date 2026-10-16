"""Answer-free integration controls for the proposed Cycle 03 run boundary.

Only synthetic placeholder rows are used. This composes the standalone process
guard with capped serialization and a final receipt; it does not read candidate
inputs, create research evidence, or authorize a challenge run.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile


HERE = Path(__file__).resolve().parent
RESOURCE_PATH = HERE / "check-finite-lineage-resource-shape.py"
GUARD_PATH = HERE / "check-finite-lineage-execution-guard.py"
FAILURE_RESERVE_BYTES = 16 * 1024


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load helper: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


resource = load_module("finite_lineage_resource_shape", RESOURCE_PATH)
guard = load_module("finite_lineage_execution_guard", GUARD_PATH)


def write_receipt(path: Path, receipt: dict[str, object]) -> None:
    temporary = path.with_name(path.name + ".partial")
    with temporary.open("x", encoding="utf-8") as stream:
        json.dump(receipt, stream, sort_keys=True, separators=(",", ":"))
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def prepare_failure_reserve(root: Path) -> Path:
    """Allocate emergency space before work so a failure receipt can be saved."""
    path = root / ".failure-receipt.reserve"
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        remaining = FAILURE_RESERVE_BYTES
        block = b"\0" * 4096
        while remaining:
            written = os.write(fd, block[:min(remaining, len(block))])
            if written <= 0:
                raise OSError("could not allocate failure-receipt reserve")
            remaining -= written
        os.fsync(fd)
    except BaseException:
        os.close(fd)
        path.unlink(missing_ok=True)
        raise
    else:
        os.close(fd)
    return path


def write_incomplete(root: Path, reason: str, reserve: Path) -> None:
    receipt = {"status": "INCOMPLETE", "failure": reason,
               "automatic_retry": False, "promotion": False}
    try:
        write_receipt(root / "INCOMPLETE.json", receipt)
    except OSError:
        # This is a receipt-persistence fallback, never a worker/run retry.
        # Releasing preallocated blocks gives the same filesystem room to save
        # the small terminal record after an evidence-write ENOSPC error.
        if not reserve.exists():
            raise
        reserve.unlink()
        write_receipt(root / "INCOMPLETE.json", receipt)
    reserve.unlink(missing_ok=True)


def run_package(root: Path, command: list[str], *, timeout: float = 3,
                row_cap: int = 448, row_count_cap: int = 4,
                writer=resource.write_capped_jsonl) -> dict[str, object]:
    """Compose worker supervision, capped evidence writing and terminal receipt."""
    reserve = prepare_failure_reserve(root)
    raw = root / "worker-output.partial"
    result = guard.supervise(command + [str(raw)], timeout_seconds=timeout)
    if result["status"] != "COMPLETE":
        write_incomplete(root, str(result["reason"]), reserve)
        return {"status": "INCOMPLETE", "reason": result["reason"]}

    evidence = root / "synthetic-evidence.jsonl"
    try:
        def rows():
            with raw.open("r", encoding="utf-8") as stream:
                for line in stream:
                    yield json.loads(line)

        count, size = writer(
            evidence, rows(), row_cap=row_cap, file_cap=4096,
            total_cap=8192, total_before=0, row_count_cap=row_count_cap,
        )
        digest = hashlib.sha256(evidence.read_bytes()).hexdigest()
        write_receipt(root / "COMPLETE.json", {
            "status": "COMPLETE", "rows": count, "bytes": size,
            "sha256": digest, "automatic_retry": False,
        })
        reserve.unlink(missing_ok=True)
        return {"status": "COMPLETE", "rows": count, "bytes": size,
                "sha256": digest}
    except BaseException as exc:
        write_incomplete(root, f"{type(exc).__name__}: {exc}", reserve)
        return {"status": "INCOMPLETE", "reason": type(exc).__name__}


WORKER = """import pathlib,sys
pathlib.Path(sys.argv[1]).write_text('{\\"synthetic\\":1}\\n{\\"synthetic\\":2}\\n', encoding='utf-8')
"""


def worker_command(code: str = WORKER) -> list[str]:
    return [sys.executable, "-c", code]


def check_success(root: Path) -> None:
    result = run_package(root, worker_command())
    receipt = json.loads((root / "COMPLETE.json").read_text())
    evidence = root / "synthetic-evidence.jsonl"
    if result["status"] != "COMPLETE" or receipt["status"] != "COMPLETE":
        raise AssertionError(f"Synthetic integrated success failed: {result}")
    if receipt["rows"] != 2 or receipt["sha256"] != hashlib.sha256(evidence.read_bytes()).hexdigest():
        raise AssertionError("Completion receipt does not bind the verified evidence bytes")
    if (root / "INCOMPLETE.json").exists() or evidence.with_name(evidence.name + ".partial").exists():
        raise AssertionError("Successful package retained incomplete markers")


def check_worker_failure(root: Path) -> None:
    failed = "import pathlib,sys; pathlib.Path(sys.argv[1]).write_text('partial'); raise SystemExit(7)"
    result = run_package(root, worker_command(failed))
    receipt = json.loads((root / "INCOMPLETE.json").read_text())
    if result["status"] != "INCOMPLETE" or receipt["promotion"] or receipt["automatic_retry"]:
        raise AssertionError("Worker failure was promoted or automatically retried")
    if (root / "COMPLETE.json").exists() or not (root / "worker-output.partial").exists():
        raise AssertionError("Worker failure lost its partial or wrote a COMPLETE receipt")


def check_cap_failure(root: Path) -> None:
    result = run_package(root, worker_command(), row_count_cap=1)
    receipt = json.loads((root / "INCOMPLETE.json").read_text())
    if result["status"] != "INCOMPLETE" or receipt["promotion"]:
        raise AssertionError("Integrated cap failure did not fail closed")
    if (root / "COMPLETE.json").exists():
        raise AssertionError("Cap failure wrote a COMPLETE receipt")


class FailWrite:
    """File wrapper that injects a deterministic OSError at the write call."""
    def __init__(self, stream):
        self.stream = stream

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.stream.close()

    def write(self, _value):
        raise OSError("injected synthetic evidence write failure")

    def __getattr__(self, name):
        return getattr(self.stream, name)


def check_injected_io_failure(root: Path) -> None:
    original_fdopen = resource.os.fdopen

    def failing_fdopen(*args, **kwargs):
        return FailWrite(original_fdopen(*args, **kwargs))

    resource.os.fdopen = failing_fdopen
    try:
        result = run_package(root, worker_command())
    finally:
        resource.os.fdopen = original_fdopen
    receipt = json.loads((root / "INCOMPLETE.json").read_text())
    if result["status"] != "INCOMPLETE" or "OSError" not in receipt["failure"]:
        raise AssertionError("Injected evidence I/O failure was not captured")
    if (root / "COMPLETE.json").exists():
        raise AssertionError("Injected evidence I/O failure wrote COMPLETE")
    if not (root / "synthetic-evidence.jsonl.manifest.json").exists():
        raise AssertionError("Capped writer did not preserve its failure receipt")


def check_failure_receipt_reserve(root: Path) -> None:
    original_write_receipt = write_receipt
    failed_once = False

    def fail_first_incomplete_write(path: Path, receipt: dict[str, object]) -> None:
        nonlocal failed_once
        if path.name == "INCOMPLETE.json" and not failed_once:
            failed_once = True
            raise OSError("injected synthetic ENOSPC while writing failure receipt")
        original_write_receipt(path, receipt)

    globals()["write_receipt"] = fail_first_incomplete_write
    try:
        failed = "import pathlib,sys; pathlib.Path(sys.argv[1]).write_text('partial'); raise SystemExit(9)"
        result = run_package(root, worker_command(failed))
    finally:
        globals()["write_receipt"] = original_write_receipt
    receipt = json.loads((root / "INCOMPLETE.json").read_text())
    if not failed_once or result["status"] != "INCOMPLETE":
        raise AssertionError("Receipt persistence fallback was not exercised")
    if receipt["promotion"] or receipt["automatic_retry"]:
        raise AssertionError("Receipt persistence failure promoted or retried the run")
    if (root / "COMPLETE.json").exists() or (root / ".failure-receipt.reserve").exists():
        raise AssertionError("Failure fallback left a completion or reserve marker")


def main() -> None:
    temp_root = Path("/private/tmp")
    if shutil.disk_usage(temp_root).free < 2 * 1024**3:
        raise RuntimeError("Need at least 2 GiB free for answer-free integration controls")
    controls = [check_success, check_worker_failure, check_cap_failure,
                check_injected_io_failure, check_failure_receipt_reserve]
    for check in controls:
        with tempfile.TemporaryDirectory(prefix="finite-lineage-integration-",
                                         dir=temp_root) as directory:
            check(Path(directory))
    print(json.dumps({
        "status": "PASS",
        "purpose": "ANSWER_FREE_SYNTHETIC_RUN_BOUNDARY_INTEGRATION",
        "candidate_inputs_read": False,
        "candidate_answers_generated": False,
        "controls": ["supervisor_to_capped_writer", "hash_bound_COMPLETE_receipt",
                     "worker_crash_partial", "cap_failure_no_promotion",
                     "injected_write_error_incomplete_receipt",
                     "preallocated_reserve_after_incomplete_receipt_enospc",
                     "no_automatic_retry"],
        "temporary_artifacts_removed": True,
        "python": sys.version.split()[0],
        "platform": sys.platform,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
