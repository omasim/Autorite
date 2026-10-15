"""Answer-free maximum-shape serialization stress check for Cycle 03 preparation.

Writes only synthetic placeholder records under /private/tmp, never candidate
inputs or computed answers. The exact corpus, answer semantics, and outcomes are
not imported or read by this check.
"""
from hashlib import sha256
import json
import os
import shutil
import tempfile
from pathlib import Path
from time import perf_counter


MAX_WITNESS_ROWS = 1_077_936
MAX_WITNESS_FILE_BYTES = 640 * 1024 * 1024
MAX_EVIDENCE_BYTES = 640 * 1024 * 1024
MIN_FREE_BYTES = 2 * 1024 * 1024 * 1024
MAX_ROW_BYTES = 448
MAX_OTHER_ROWS = 4_440 + 440 + 6_712
MAX_NON_ROW_ARTIFACT_BYTES = 64 * 1024 * 1024


def require_free_space(free_bytes):
    if free_bytes < MIN_FREE_BYTES:
        raise RuntimeError(f"Need {MIN_FREE_BYTES} free bytes; found {free_bytes}")


def complete_evidence_upper_bound():
    # Inventory-derived witness count plus maximum truth, projection and pair
    # JSONL rows. Certificates and the two input documents are charged to the
    # separately capped non-row artifact reserve because their records can be
    # larger than one JSONL row.
    all_rows = MAX_WITNESS_ROWS + MAX_OTHER_ROWS
    return all_rows * MAX_ROW_BYTES + MAX_NON_ROW_ARTIFACT_BYTES


def encoded_line(row):
    return (json.dumps(row, sort_keys=True, separators=(",", ":"),
                        ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


class OutputCapExceeded(RuntimeError):
    pass


def write_capped_jsonl(path, rows, *, row_cap, file_cap, total_cap, total_before,
                       row_count_cap):
    """Stream canonical rows; leave partial bytes and an INCOMPLETE receipt on failure."""
    path = Path(path)
    partial = path.with_name(path.name + ".partial")
    count = size = 0
    fd = os.open(partial, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "wb") as stream:
            for row in rows:
                line = encoded_line(row)
                if len(line) > row_cap:
                    raise OutputCapExceeded("row-byte cap exceeded")
                if count + 1 > row_count_cap:
                    raise OutputCapExceeded("row-count cap exceeded")
                if size + len(line) > file_cap:
                    raise OutputCapExceeded("file-byte cap exceeded")
                if total_before + size + len(line) > total_cap:
                    raise OutputCapExceeded("total-evidence byte cap exceeded")
                stream.write(line)
                size += len(line)
                count += 1
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(partial, path)
        return count, size
    except BaseException as exc:
        try:
            with partial.open("ab") as stream:
                stream.flush()
                os.fsync(stream.fileno())
        except FileNotFoundError:
            pass
        receipt = {"status": "INCOMPLETE", "rows_written": count,
                   "bytes_written": size, "failure": type(exc).__name__ + ": " + str(exc)}
        receipt_path = path.with_name(path.name + ".manifest.json")
        with receipt_path.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        raise


def check_cap_failures(root):
    base = {"x": "y"}
    exact_row = {"x": "y" * 439}  # 448 UTF-8 bytes including JSON framing and LF.
    if len(encoded_line(exact_row)) != MAX_ROW_BYTES:
        raise RuntimeError("Exact row-cap control is malformed")
    over_row = {"x": "y" * 440}
    controls = [
        ("row", [over_row], dict(row_cap=MAX_ROW_BYTES, file_cap=4096, total_cap=4096,
                                 total_before=0, row_count_cap=2)),
        ("count", [base, base], dict(row_cap=MAX_ROW_BYTES, file_cap=4096, total_cap=4096,
                                     total_before=0, row_count_cap=1)),
        ("file", [base], dict(row_cap=MAX_ROW_BYTES, file_cap=1, total_cap=4096,
                               total_before=0, row_count_cap=2)),
        ("total", [base], dict(row_cap=MAX_ROW_BYTES, file_cap=4096, total_cap=1,
                                total_before=0, row_count_cap=2)),
    ]
    for name, rows, limits in controls:
        path = Path(root) / f"{name}.jsonl"
        try:
            write_capped_jsonl(path, rows, **limits)
        except OutputCapExceeded:
            pass
        else:
            raise RuntimeError(f"{name} cap failure was not detected")
        partial = path.with_name(path.name + ".partial")
        receipt_path = path.with_name(path.name + ".manifest.json")
        if path.exists() or not partial.exists() or not receipt_path.exists():
            raise RuntimeError(f"{name} cap failure did not preserve INCOMPLETE partial output")
        if json.loads(receipt_path.read_text())["status"] != "INCOMPLETE":
            raise RuntimeError(f"{name} cap failure did not record INCOMPLETE status")
    exact_path = Path(root) / "exact-row.jsonl"
    count, size = write_capped_jsonl(exact_path, [exact_row], row_cap=MAX_ROW_BYTES,
        file_cap=MAX_ROW_BYTES, total_cap=MAX_ROW_BYTES, total_before=0, row_count_cap=1)
    if (count, size) != (1, MAX_ROW_BYTES):
        raise RuntimeError("Exact row-cap boundary did not pass")


def main():
    temporary_root = Path("/private/tmp")
    free = shutil.disk_usage(temporary_root).free
    require_free_space(free)
    complete_bound = complete_evidence_upper_bound()
    if complete_bound > MAX_EVIDENCE_BYTES:
        raise RuntimeError("Complete evidence-package bound exceeds total evidence cap")
    require_free_space(MIN_FREE_BYTES)
    try:
        require_free_space(MIN_FREE_BYTES - 1)
    except RuntimeError:
        pass
    else:
        raise RuntimeError("Low-disk boundary control was not rejected")

    # Long but schema-shaped placeholders, deliberately unrelated to the
    # candidate IDs, query keys, masks, state values, or outcomes.
    row = {
        "case_pair": ["synthetic-case-000", "synthetic-case-001"],
        "family": "SYNTHETIC_FAMILY",
        "mask": "111",
        "query_key": {"left": "synthetic-entity-000", "right": "synthetic-entity-001"},
        "answers": [
            [f"synthetic-entity-{index:03d}" for index in range(5)],
            [f"synthetic-entity-{index:03d}" for index in range(5)],
        ],
    }
    line = encoded_line(row)
    if len(line) > MAX_ROW_BYTES:
        raise RuntimeError(f"Synthetic witness row is {len(line)} bytes; cap is {MAX_ROW_BYTES}")

    start = perf_counter()
    with tempfile.TemporaryDirectory(prefix="finite-lineage-shape-", dir=temporary_root) as root:
        check_cap_failures(root)
        path = Path(root) / "synthetic-conflicts.jsonl"
        digest = sha256()
        def rows():
            for _ in range(MAX_WITNESS_ROWS):
                digest.update(line)
                yield row
        count, written = write_capped_jsonl(path, rows(), row_cap=MAX_ROW_BYTES,
            file_cap=MAX_WITNESS_FILE_BYTES, total_cap=MAX_EVIDENCE_BYTES,
            total_before=0, row_count_cap=MAX_WITNESS_ROWS)
        if count != MAX_WITNESS_ROWS or path.stat().st_size != written:
            raise RuntimeError("Synthetic output count/byte verification failed")
        if written > MAX_EVIDENCE_BYTES:
            raise RuntimeError("Synthetic evidence set exceeded the total byte cap")
        reread = sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                reread.update(chunk)
        if digest.hexdigest() != reread.hexdigest():
            raise RuntimeError("Streaming and reread SHA-256 differ")

    print(json.dumps({
        "status": "PASS",
        "purpose": "ANSWER_FREE_SYNTHETIC_OUTPUT_SHAPE_STRESS",
        "candidate_inputs_read": False,
        "candidate_answers_generated": False,
        "synthetic_witness_rows": count,
        "max_witness_rows": MAX_WITNESS_ROWS,
        "max_row_bytes": MAX_ROW_BYTES,
        "max_witness_file_bytes": MAX_WITNESS_FILE_BYTES,
        "max_other_rows": MAX_OTHER_ROWS,
        "max_non_row_artifact_bytes": MAX_NON_ROW_ARTIFACT_BYTES,
        "complete_evidence_upper_bound_bytes": complete_bound,
        "max_evidence_bytes": MAX_EVIDENCE_BYTES,
        "low_disk_boundary_controls": ["minimum_free_space_accepted", "one_byte_below_rejected"],
        "synthetic_file_bytes": written,
        "synthetic_file_sha256": digest.hexdigest(),
        "free_bytes_before_run": free,
        "cap_failure_controls": ["row", "row_count", "file_bytes", "total_evidence_bytes", "partial_preserved", "incomplete_receipt"],
        "elapsed_seconds": round(perf_counter() - start, 3),
        "temporary_output_removed": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
