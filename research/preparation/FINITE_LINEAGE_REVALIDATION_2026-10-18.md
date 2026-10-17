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

The macOS process group contained at most two processes. Darwin `libproc` sampling at 25 ms observed a 52,428,800-byte peak over 91 samples, below the sampled 536,870,912-byte stop threshold. This is a sampled measurement only; very short peaks between samples could be missed. The verifier also rejected a 449-byte witness row.

### Linux cgroups v2 validation

The same 55-case synthetic pipeline passed in GitHub Actions run [39072987426](https://github.com/omasim/Autorite/actions/runs/39072987426), commit `0666320fa95bc76d400bf212392ffa814a30e47e`, under Python 3.12.13. The runner used a Docker cgroups v2 memory ceiling of 536,870,912 bytes (512 MiB), set swap allowance to zero, and verified `memory.max` and `memory.swap.max` from inside the constrained container. After execution, cgroup `memory.peak` was 62,435,328 bytes, `oom_events` and `oom_kill_count` were both zero. Separate 25 ms `/proc` sampling observed a 57,212,928-byte process-group RSS peak across 180 samples and at most two processes. The hard cgroup ceiling covered the complete container process tree; sampled RSS remained supplementary.

F4 completed 17 cases across four topologies (maximum depth 2, out-degree 2); F5 completed 38 cases across five topologies (maximum depth 3, out-degree 2). The cgroup run produced 22,143 semantic conflict rows in total and passed the bounded producer, independent verifier, and capped package writer. No candidate data or answers were read or generated. The 1,077,936-row upper bound remains separately validated with answer-free placeholder rows, rather than by the semantic 55-case run.

## Verifier memory bound

The bounded verifier does not retain the full conflict-witness set: `verify_bounded` compares each expected witness with one JSONL line and updates a streaming SHA-256. The producer sends conflicts to the capped sink; the final writer also reads the conflict file incrementally. Conflict-row memory is therefore bounded by one encoded row and temporary per-pair counters/indexes, rather than the total number of emitted conflicts.

The verifier is not constant-memory in the whole challenge inventory. It retains reconstructed worlds, truth rows/answers, projections, pair records, and certificates. At a high level its memory is bounded by the declared finite inventory: `O(C·(V+E) + C·Q + 8·C·V + 8·C² + 16·C·Q + V² + R)`, where `C` is case count, `V/E` are nodes/edges per case, `Q` is query count per case, and `R` is the largest conflict row. The `V²` term covers a temporary closure matrix rebuilt during query evaluation; the `C·Q` terms cover retained truth/query vectors and certificates. At fixed `C=55` and `V≤5`, this memory is independent of whether the conflict file contains a few rows or approaches its row cap. The measured 55-case process-tree peak above is consistent with this bound on the tested synthetic corpus; it is not a proof for arbitrary inputs beyond the declared caps.

## Execution controls and host enforcement

The execution supervisor now applies inherited `RLIMIT_FSIZE` (640 MiB per file), `RLIMIT_NOFILE` (256), and `RLIMIT_CPU` (1,800 seconds per process); fixes `PYTHONHASHSEED=0` when requested; samples aggregate process-group RSS; and terminates the process group with SIGTERM followed by SIGKILL on RSS or dual-clock wall-time breach. `scripts/check-finite-lineage-execution-guard.py` passed its synthetic controls for inherited limits, deterministic hash seed, process-group sampling/cap, timeouts, descendant teardown, bounded logs, crash preservation, and fail-closed receipts.

The local macOS environment still cannot impose cgroups v2 or finite `RLIMIT_AS`; its 512 MiB process-group RSS threshold remains a sampled stop control. The separate Linux synthetic run closes the reviewer’s hard process-tree memory-ceiling requirement for this workload: the container was kernel-limited to 512 MiB with no swap, and the post-run cgroup counters confirmed no OOM event or kill. The workflow applies a 1,200-second process-group wall timeout, per-process `RLIMIT_CPU=1,800` seconds, `RLIMIT_FSIZE=640 MiB`, `RLIMIT_NOFILE=256`, `PYTHONHASHSEED=0`, and process-group teardown on supervisor timeout. Per-process CPU limits are not an aggregate CPU budget.

## Hashes of updated implementation and check

- Synthetic 55-case stress harness: `3d7532e855fbd4a6a184318bf5c014fff283217caefd9318cae9e039c7c29390`
- Linux cgroups v2 workflow: `dc371ca599436541d959f063b4efb0c979aa4c96f12a9ff461426cd78c61f084`
- Process-group and resource execution guard: `08020b30a22999c83196278c35c5d55d196c02dfbcfc2e898b07dbc9eb2fdc85`
- Streaming package writer: `4ab37dd0eee7838d58b110164e18ecf164e01b7b1b572baddbdba5bea1553e56`
- Producer (unchanged from review): `899d6b3b0e70c6b4af420fdd19b9043e790547b92caac2376586da0e27ce8868`
- Verifier with the new bounded-line guard: `a571f0b734056775c953b7ba8b158dabdf3e51ba9d7b1e7bbd8248f119979f59` (reviewed version: `9422bb99adfd45b3ab192d4750e3965b6de2569207e8b16bfc5336bb0c714a9e`)
- External review record: `f41117d9fa3725e9a8bb5a8b61a96fdeab68b581d8466d1b0ae45a3da4db13eb`

## Regression checks after the engineering changes

The local regression checks below passed under Python 3.12.13 on macOS after adding streamed conflict-file packaging and process-group controls. The separate Linux cgroups v2 run is recorded above:

- `python3.12 -m unittest tests.test_rp006_implementation`: 24 tests passed.
- `scripts/check-finite-lineage-bounded-pipeline.py`: bounded toy producer/verifier/writer passed.
- `scripts/check-finite-lineage-writer-integration.py`: supervised toy writer integration passed.
- `scripts/check-finite-lineage-design.py`: 55 partitions and 4,440 truth rows, 440 projections, 6,712 pair/mask rows, and 32 certificates reproduced.
- `scripts/check-finite-lineage-preparation-integration.py`: preparation and failure-receipt controls passed.
- `scripts/check-finite-lineage-resource-shape.py`: 1,077,936 placeholder rows (452,733,120 bytes) and row/file/total-cap boundaries passed.
- `scripts/check-finite-lineage-execution-guard.py`: inherited OS limits, hash seed, sampled process-group RSS, termination, and existing failure controls passed.
- `scripts/check-finite-lineage-55-case-synthetic-stress.py`: the full synthetic run passed on macOS and under Linux cgroups v2.
- GitHub Actions cgroups v2 job: `memory.max=536870912`, `memory.swap.max=0`, `memory.peak=62435328`, no OOM events or kills.

The placeholder-row test validates the configured maximum row stream independently; the 55-case semantic stress run validates actual producer/verifier/writer behavior below that maximum. Neither creates a candidate corpus or candidate answer output.

## Entry status

The reviewer’s host-level process-tree memory requirement is now validated for the synthetic 55-case workload under Linux cgroups v2. The full semantic run emitted 22,143 conflict rows; the 1,077,936-row ceiling was exercised separately with placeholders, so the reviewer must accept that separation or request a semantic workload that reaches the cap. Post-review implementation hashes still need supplemental assessment. The entry template asks for an identifiable reviewer and institution/organization; the report preserves the reviewer as anonymous and does not independently verify the claimed identity or organization. That condition remains unresolved unless an authorized decision-maker accepts a confidential, auditable identity attestation. Cycle 03 remains unopened; no candidate input, Test registration, resource commitment, or research execution is authorized by this revalidation.
