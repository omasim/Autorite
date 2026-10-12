# RP006 — result review 001

Review date: 2026-10-12. Scope: the single recorded attempt authorized by D-0016. Outcome: complete and independently replayed; accept only the finite RP006 commitment.

## Provenance and integrity

Attempt `570e92be-204b-4330-8300-bcbc4e2078d2` used Test `TST-RP006001`, source commit `b511e2234c7b59f90e4cc8cb089b58b3d3ed8d36`, freeze SHA-256 `f2e84dbdb46ebbf5c657d8a0f127c10a9c377262fa4c425c9e3dfeac6ebbbb39`, and authorization SHA-256 `756fcc3d2ee1b3ecd39bd9e73963ab0fd798eea368f1043c9edf4e446dfaf332`. The run manifest SHA-256 is `eb0066b36a1f10fddf07417459cd4b69c50be9db33e59ceb7245df90dd3b51ad`. The manifest records `COMPLETE`, no failure, the accepted source/test/checkpoint references and eight output hashes. `scripts/check-rp006-audit.py` independently checks the frozen source commit, authorization and freeze hashes, every output checksum, all rows and certificates against a fresh verifier replay. The saved replay reports `PASS`; no producer code is imported by the verifier.

The immutable run contains 216 truth rows, 48 projections, 120 case-pair/mask comparisons, 438 conflict rows and 16 family/mask certificates. Every prospective row, comparison and verdict is present. Both topology/state and full-family conflict witnesses are preserved. Output files and hashes are listed in the run manifest.

After the attempt, the Cycle 02 manifest was updated under D-0017 to record package and checkpoint completion, and the schema/supervisor validation code was extended to recognize this completed run format. The original bytes remain pinned in the frozen source commit. The new audit checker validates those committed bytes and requires the computation, domain, producer, verifier, runtime and Test sources to remain byte-identical; only the named post-run governance files are allowed to evolve.

## Observations

For FULL, sufficient masks are `001`, `011`, `101` and `111`; the sole inclusion-minimal mask is `001` (birth kind). For TOPOLOGY_STATE, sufficient masks are `001`, `010`, `011`, `101`, `110` and `111`; inclusion-minimal masks are `001` and `010` (birth kind and complete parents). The audit recorded 1,152 equality-gated FULL query checks and 960 TOPOLOGY_STATE checks. These values match the classifications already disclosed by the RP006 engineering preflight and the known RP004 cases; they do not constitute blind confirmation or fresh evidence.

The run used macOS 26.3 arm64 and Python 3.12.13. `mach_continuous_time`, monotonic and civil clocks agreed within 0.000004 seconds. Continuous elapsed time was 0.104429 seconds. The conservative sum of supervisor and worker lifetime peak RSS was 50,511,872 bytes (parent 27,721,728; worker 22,790,144), below the 128 MiB ceiling. No stop condition fired and no retry was attempted.

## Interpretation and disposition

The result supports only exact finite sufficiency and inclusion-minimality on the six known three-entity RP004 constructions under the two registered query families and eight whole-field masks. It does not establish sufficiency for unseen cases, universal representation necessity, a byte/bit optimum, novelty, metaphysical identity, or resolution of Q-3 or Q-4. The prior RP004 and engineering-preflight behavior remains disclosed.

Under D-0017, accept `R-RP006001` as VALID and close RP-006's finite commitment. Resolve Cycle 02's RP006 package and actual checkpoint obligations only; leave the final graph review and six remaining Cycle obligations open. Cycle 02 remains OPEN at 2/9. No new Claim or broad scientific support relation is created.
