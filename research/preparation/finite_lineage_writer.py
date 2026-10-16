"""Proposed bounded writer for a separately authorized finite-lineage package.

This module does not generate or accept candidate cases by itself. Callers must
provide the answer-free event domain, producer bundle, passing independent
verifier receipt, and exact source hashes. The serialization contract remains
subject to entry review.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
RESOURCE_PATH = ROOT / "scripts/check-finite-lineage-resource-shape.py"
_spec = importlib.util.spec_from_file_location("finite_lineage_writer_resource", RESOURCE_PATH)
if _spec is None or _spec.loader is None:
    raise RuntimeError("Cannot load finite-lineage resource caps")
_resource = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_resource)

TOTAL_CAP = _resource.MAX_EVIDENCE_BYTES
NON_ROW_CAP = _resource.MAX_NON_ROW_ARTIFACT_BYTES
ROW_CAP = _resource.MAX_ROW_BYTES
ROW_LIMITS = {
    "truth.jsonl": 4_440,
    "projections.jsonl": 440,
    "pairs.jsonl": 6_712,
    "conflicts.jsonl": 1_077_936,
}
ROW_BUNDLE_KEYS = {"truth.jsonl": "truth", "projections.jsonl": "projections",
                   "pairs.jsonl": "pairs", "conflicts.jsonl": "conflicts"}
ROW_FILES = tuple(ROW_LIMITS)
NON_ROW_FILES = ("certificates.json", "summary.json", "verifier-receipt.json")
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def canonical_bytes(value: Any, *, pretty: bool = False) -> bytes:
    if pretty:
        text = json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False)
    else:
        text = json.dumps(value, sort_keys=True, separators=(",", ":"),
                           ensure_ascii=False, allow_nan=False)
    return (text + "\n").encode("utf-8")


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def _write_artifact(root: Path, name: str, data: bytes, *, row_total: int,
                    non_row_total: int) -> tuple[int, int]:
    path = root / name
    size = _resource.write_capped_artifact(
        path, (data,), artifact_cap=NON_ROW_CAP - non_row_total,
        total_cap=TOTAL_CAP, total_before=row_total + non_row_total,
    )
    return size, row_total + non_row_total + size


def _receipt(root: Path, name: str, value: dict[str, Any]) -> bytes:
    data = canonical_bytes(value, pretty=True)
    path = root / name
    partial = path.with_name(path.name + ".partial")
    fd = os.open(partial, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(partial, path)
    directory_fd = os.open(root, os.O_RDONLY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)
    return data


def _compact_pair(pair: dict[str, Any]) -> dict[str, Any]:
    """Avoid duplicating every witness ordinal in potentially large pair rows."""
    if "conflict_index" in pair:
        return pair
    result = {key: value for key, value in pair.items() if key != "conflict_ordinals"}
    ordinals = pair["conflict_ordinals"]
    result["conflict_index"] = {
        family: {"count": len(values), "first_ordinal": values[0] if values else None}
        for family, values in sorted(ordinals.items())
    }
    return result


def _compact_certificate(certificate: dict[str, Any]) -> dict[str, Any]:
    """Index all conflict rows without repeating their IDs in every supermask."""
    if all("conflict_index" in item for item in certificate["proper_submasks"]):
        return certificate
    result = dict(certificate)
    compact = []
    for item in certificate["proper_submasks"]:
        ordinals = item["conflict_ordinals"]
        compact.append({"mask": item["mask"], "sufficient": item["sufficient"],
                        "conflict_index": {"count": len(ordinals),
                                           "first_ordinal": ordinals[0] if ordinals else None}})
    result["proper_submasks"] = compact
    return result


def write_bundle(outdir: str | Path, domain: dict[str, Any], bundle: dict[str, Any],
                 verifier: dict[str, Any], source_hashes: dict[str, str], *,
                 stratum: str, source_commit: str, guard=lambda: None) -> dict[str, Any]:
    """Write a verified bundle under proposed row, reserve, and total caps.

    The destination must be a new directory. On any failure, preserve the
    already-written partial/final artifacts and attempt one INCOMPLETE receipt;
    this function never retries computation or promotes a partial package.
    """
    root = Path(outdir)
    root.mkdir(mode=0o700, parents=True, exist_ok=False)
    row_total = 0
    non_row_total = 0
    try:
        guard()
        if verifier.get("status") != "PASS":
            raise ValueError("A passing independent verifier receipt is required")
        if stratum not in {"F4", "F5", "TOY"}:
            raise ValueError("Explicit F4/F5 stratum required (TOY is reserved for synthetic checks)")
        if not re.fullmatch(r"[0-9a-f]{40}", source_commit):
            raise ValueError("Source commit must be a full lowercase Git commit hash")
        if not source_hashes or any(not SHA256.fullmatch(v) for v in source_hashes.values()):
            raise ValueError("Source identities must be lowercase SHA-256 values")
        if set(bundle) != {"truth", "projections", "pairs", "conflicts", "certificates", "summary"}:
            raise ValueError("Unexpected producer artifact inventory")

        domain_bytes = canonical_bytes(domain, pretty=True)
        size, non_row_total = _write_artifact(root, "input-domain.json", domain_bytes,
                                               row_total=row_total, non_row_total=non_row_total)
        input_record = {"path": "input-domain.json", "bytes": size,
                        "sha256": hashlib.sha256(domain_bytes).hexdigest()}

        row_inventory: dict[str, dict[str, Any]] = {}
        for name in ROW_FILES:
            rows: Iterable[dict[str, Any]] = bundle[ROW_BUNDLE_KEYS[name]]
            if name == "pairs.jsonl":
                rows = (_compact_pair(row) for row in rows)
            def guarded_rows(values):
                for index, row in enumerate(values):
                    if index % 256 == 0:
                        guard()
                    yield row
            count, size = _resource.write_capped_jsonl(
                root / name, guarded_rows(rows), row_cap=ROW_CAP,
                file_cap=TOTAL_CAP if name == "conflicts.jsonl" else ROW_LIMITS[name] * ROW_CAP,
                total_cap=TOTAL_CAP, total_before=row_total,
                row_count_cap=ROW_LIMITS[name],
            )
            row_total += size
            row_hash = digest(root / name)
            verified_hash = verifier.get("verified_artifact_sha256", {}).get(name)
            if verified_hash is not None and row_hash != verified_hash:
                raise ValueError(f"Written {name} differs from the independently verified bytes")
            row_inventory[name] = {"rows": count, "bytes": size, "sha256": row_hash}

        non_row_inventory: dict[str, dict[str, Any]] = {}
        compact_certificates = [_compact_certificate(row) for row in bundle["certificates"]]
        for name, value in (("certificates.json", compact_certificates),
                            ("summary.json", bundle["summary"])):
            guard()
            data = canonical_bytes(value, pretty=True)
            size, non_row_total = _write_artifact(root, name, data, row_total=row_total,
                                                   non_row_total=non_row_total)
            non_row_inventory[name] = {"bytes": size, "sha256": hashlib.sha256(data).hexdigest()}

        manifest = {
            "format": "autorite-finite-lineage-evidence-v1",
            "status": "COMPLETE",
            "stratum": stratum,
            "source_commit": source_commit,
            "source_hashes": dict(sorted(source_hashes.items())),
            "input": input_record,
            "evidence": {"jsonl": row_inventory, "artifacts": non_row_inventory},
            "conflict_index_format": {
                "pair_rows": "per-family count and first witness ordinal",
                "certificate_submasks": "count and first witness ordinal",
                "complete_witnesses": "conflicts.jsonl",
            },
            "counts": bundle["summary"],
            "caps": {"row_bytes": ROW_CAP, "non_row_bytes": NON_ROW_CAP,
                     "total_bytes": TOTAL_CAP},
            "exclusions": ["manifest.json", "verifier-receipt.json"],
        }
        manifest_bytes = canonical_bytes(manifest, pretty=True)
        guard()
        size, non_row_total = _write_artifact(root, "manifest.json", manifest_bytes,
                                               row_total=row_total, non_row_total=non_row_total)
        manifest_hash = hashlib.sha256(manifest_bytes).hexdigest()
        receipt = {
            "status": "PASS",
            "basis": verifier.get("basis"),
            "verified_artifacts": verifier.get("verified_artifacts"),
            "counts": verifier.get("counts"),
            "input_sha256": input_record["sha256"],
            "manifest_sha256": manifest_hash,
            "source_hashes": dict(sorted(source_hashes.items())),
        }
        receipt_bytes = canonical_bytes(receipt, pretty=True)
        guard()
        size, non_row_total = _write_artifact(root, "verifier-receipt.json", receipt_bytes,
                                               row_total=row_total, non_row_total=non_row_total)
        return {"status": "COMPLETE", "manifest_sha256": manifest_hash,
                "input_sha256": input_record["sha256"],
                "row_bytes": row_total, "non_row_bytes": non_row_total,
                "total_bytes": row_total + non_row_total}
    except BaseException as exc:
        failure = {"status": "INCOMPLETE", "failure": f"{type(exc).__name__}: {exc}",
                   "automatic_retry": False, "promotion": False,
                   "preserved_files": sorted(p.name for p in root.iterdir() if p.is_file())}
        try:
            _receipt(root, "INCOMPLETE.json", failure)
        except OSError:
            pass
        raise
