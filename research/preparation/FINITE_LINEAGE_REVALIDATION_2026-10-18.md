# Finite-lineage preparation revalidation — 2026-10-18

**Scope:** Control-blind synthetic engineering checks requested by the 2026-10-18 external design review. This is not a Cycle 03 run, candidate-corpus generation, entry decision, source/input freeze, or execution authorization.

## External-review provenance

The review is preserved verbatim in `FINITE_LINEAGE_EXTERNAL_REVIEW_001_2026-10-18.md`. Its source attachment SHA-256 is `0a60071fd91d035b9f495e60a4fe44bb37645274f79399a1408f9914fa7bfccd`. The reviewer is stated as anonymous, a Principal Distributed Systems & Data Infrastructure Engineer in industry. The report declares independence and no conflicts. The reviewer’s identity and institution are withheld and have not been independently verified.

Every draft and supporting-file SHA-256 listed by the reviewer was checked at receipt and matched the local bytes. In particular, the reviewed draft remains `973ed516dc3e495002fea4ff320d2d8b084d2271112217c42aa8226e3fb66db7`. This addendum and the engineering changes below were produced after that review and therefore were not among the exact bytes the reviewer assessed.

## 55-case synthetic end-to-end stress run

`scripts/check-finite-lineage-55-case-synthetic-stress.py` passed on macOS using Python 3.12.13, with `PYTHONHASHSEED=0`. It generated 17 F4 and 38 F5 synthetic event-log cases under `STRESS-*` identifiers. These were not read from or copied as a candidate corpus. The generated topologies covered four F4 and five F5 structures; every F4 case reached depth 2 with maximum out-degree 2, and every F5 case reached depth 3 with maximum out-degree 2. Copy/fork state constraints were applied when generating events.

The run exercised the bounded producer, conflict JSONL stream, independent bounded verifier, and final capped package writer. The writer now consumes the conflict stream one canonical row at a time rather than reconstructing a witness list in memory. Both strata passed independent verification and package/hash checks. All generated inputs and answer-bearing synthetic evidence were temporary and removed after the run. No proposed candidate inputs or candidate answers were read or generated.

| Stratum | Cases / entities | Distinct synthetic topologies | Producer worker | Verifier | Package writer | Synthetic conflict rows | Package bytes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| F4 | 17 / 4 | 4 | 0.175 s | 0.151 s | 0.078 s | 3,408 | 5,176,940 |
| F5 | 38 / 5 | 5 | 0.780 s | 0.935 s | 0.229 s | 18,735 | 25,817,573 |

The writer used its configured 1,077,936-row conflict cap; the synthetic domains emitted 22,143 conflict rows in total, so this semantic end-to-end run did not fill that cap. The exact 1,077,936-row placeholder stream and row/file/total-cap boundaries remain separately covered by the existing resource-shape and streaming-memory checks.

Per-case graph-construction and truth-evaluation wall measurements are recorded in `FINITE_LINEAGE_55_CASE_SYNTHETIC_STRESS_2026-10-18.json` (SHA-256 `c8423de09606dfd4d15e85668b0d11b25b67ddda5c62e747025f78bd72669805`). Across F4 cases, producer graph-plus-truth time was 0.000049–0.000081 s per case and verifier replay-plus-truth time was 0.000395–0.003032 s. Across F5 cases, producer graph-plus-truth time was 0.000073–0.000102 s and verifier replay-plus-truth time was 0.001035–0.001428 s. These per-case timings cover each case’s event reconstruction and query-truth work; pair/mask comparison, certificate generation, and package writing are reported as full-stage timings because those operations span multiple cases.

The isolated process group contained at most two processes. Darwin `libproc` sampling at 25 ms observed a peak aggregate resident set of 52,428,800 bytes over 91 samples, below the sampled 536,870,912-byte stop threshold. The test also confirmed the verifier rejects a 449-byte witness row. These are sampled measurements and a boundary control, not a kernel-enforced bound; very short peaks between samples could be missed.

## Verifier memory bound

The bounded verifier does not retain the full conflict-witness set: `verify_bounded` compares each expected witness with one JSONL line and updates a streaming SHA-256. The producer sends conflicts to the capped sink; the final writer also reads the conflict file incrementally. Conflict-row memory is therefore bounded by one encoded row and temporary per-pair counters/indexes, rather than the total number of emitted conflicts.

The verifier is not constant-memory in the whole challenge inventory. It retains reconstructed worlds, truth rows/answers, projections, pair records, and certificates. At a high level its memory is bounded by the declared finite inventory: `O(C·(V+E) + C·Q + 8·C·V + 8·C² + 16·C·Q + V² + R)`, where `C` is case count, `V/E` are nodes/edges per case, `Q` is query count per case, and `R` is the largest conflict row. The `V²` term covers a temporary closure matrix rebuilt during query evaluation; the `C·Q` terms cover retained truth/query vectors and certificates. At fixed `C=55` and `V≤5`, this memory is independent of whether the conflict file contains a few rows or approaches its row cap. The measured 55-case process-tree peak above is consistent with this bound on the tested synthetic corpus; it is not a proof for arbitrary inputs beyond the declared caps.

## Execution controls and remaining host limitation

The execution supervisor now applies inherited `RLIMIT_FSIZE` (640 MiB per file), `RLIMIT_NOFILE` (256), and `RLIMIT_CPU` (1,800 seconds per process); fixes `PYTHONHASHSEED=0` when requested; samples aggregate process-group RSS; and terminates the process group with SIGTERM followed by SIGKILL on RSS or dual-clock wall-time breach. `scripts/check-finite-lineage-execution-guard.py` passed its synthetic controls for inherited limits, deterministic hash seed, process-group sampling/cap, timeouts, descendant teardown, bounded logs, crash preservation, and fail-closed receipts.

This macOS execution environment does not provide cgroups v2. Attempts to impose finite `RLIMIT_AS` from this sandbox fail with `ValueError: current limit exceeds maximum limit`; therefore a hard aggregate process-tree memory ceiling is **not** established. The 512 MiB process-group RSS threshold is a sampled stop control only. Before any separate entry decision, either run the reviewed supervisor on a Linux host with cgroups v2 (`MemoryMax` and `MemorySwapMax=0`) or obtain and validate an equivalent kernel-enforced process-tree memory limit. Per-process `RLIMIT_CPU` is also not an aggregate CPU budget.

## Hashes of updated implementation and check

- Synthetic 55-case stress harness: `3885e1c2fcf55d832ac3281b372f07aed6acb11b63331c242b4fc28821435692`
- Process-group and resource execution guard: `08020b30a22999c83196278c35c5d55d196c02dfbcfc2e898b07dbc9eb2fdc85`
- Streaming package writer: `4ab37dd0eee7838d58b110164e18ecf164e01b7b1b572baddbdba5bea1553e56`
- Producer (unchanged from review): `899d6b3b0e70c6b4af420fdd19b9043e790547b92caac2376586da0e27ce8868`
- Verifier with the new bounded-line guard: `a571f0b734056775c953b7ba8b158dabdf3e51ba9d7b1e7bbd8248f119979f59` (reviewed version: `9422bb99adfd45b3ab192d4750e3965b6de2569207e8b16bfc5336bb0c714a9e`)
- External review record: `f41117d9fa3725e9a8bb5a8b61a96fdeab68b581d8466d1b0ae45a3da4db13eb`

## Regression checks after the engineering changes

The following checks passed under Python 3.12.13 on macOS after adding streamed conflict-file packaging and process-group controls:

- `python3.12 -m unittest tests.test_rp006_implementation`: 24 tests passed.
- `scripts/check-finite-lineage-bounded-pipeline.py`: bounded toy producer/verifier/writer passed.
- `scripts/check-finite-lineage-writer-integration.py`: supervised toy writer integration passed.
- `scripts/check-finite-lineage-design.py`: 55 partitions and 4,440 truth rows, 440 projections, 6,712 pair/mask rows, and 32 certificates reproduced.
- `scripts/check-finite-lineage-preparation-integration.py`: preparation and failure-receipt controls passed.
- `scripts/check-finite-lineage-resource-shape.py`: 1,077,936 placeholder rows (452,733,120 bytes) and row/file/total-cap boundaries passed.
- `scripts/check-finite-lineage-execution-guard.py`: inherited OS limits, hash seed, sampled process-group RSS, termination, and existing failure controls passed.
- `scripts/check-finite-lineage-55-case-synthetic-stress.py`: the full synthetic run described above passed.

The placeholder-row test validates the configured maximum row stream independently; the 55-case semantic stress run validates actual producer/verifier/writer behavior below that maximum. Neither creates a candidate corpus or candidate answer output.

## Entry status

The reviewer’s targeted engineering revisions are substantially addressed by the synthetic end-to-end run, verifier memory analysis, streaming writer path, and inherited OS limits. A hard aggregate process-tree memory ceiling remains open on this host. The reviewer’s post-review implementation changes should be assessed against the updated hashes before a separate entry decision. The existing entry template also requires an identifiable reviewer and institution/organization; this report preserves the reviewer as anonymous, so that provenance condition remains unresolved unless the authorized decision-maker accepts an auditable confidential identity attestation. Cycle 03 remains unopened; no candidate input, Test registration, resource commitment, or research execution is authorized by this revalidation.
