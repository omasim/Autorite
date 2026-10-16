# Finite-lineage preparation revalidation — 2026-10-16

**Purpose:** repeat the existing answer-free preparation checks using the protocol-supported Python 3.12.13 interpreter after detecting that the system-default `python3` resolves to Python 3.9.6. The 3.9.6 smoke rerun passed but is not used as the supported-runtime evidence below. This is software and placeholder validation only; it is not a Cycle 03 run, candidate-corpus generation, or entry review.

## Environment and commands

- Host: macOS (`darwin`)
- Interpreter: `/Users/omerasimozturk/.local/bin/python3.12`, Python 3.12.13
- Commands were run sequentially to avoid concurrent memory tests affecting each other's RSS observations.
- No proposed F4/F5 input corpus was read or generated, and no F4/F5 query outcomes were computed. Producer/verifier integration used only the existing synthetic `TOY` cases. Placeholder checks contained non-answer strings. All temporary files were removed by the helpers.

## Results

| Check | Result | Observed scope |
| --- | --- | --- |
| `python3.12 -m unittest tests.test_rp006_implementation` | PASS | 24 tests |
| `scripts/check-finite-lineage-design.py` | PASS | 55 equality partitions; 4,440 truth rows; 440 projections; 6,712 pair/mask rows; 32 certificates; corrected D/L/R/O overlap table; no candidate answers |
| `scripts/check-finite-lineage-bounded-pipeline.py` | PASS | Two synthetic TOY cases; 12 witness rows; 106,237-byte package; 21,643,264-byte worker peak RSS; tamper and stratum rejection controls |
| `scripts/check-finite-lineage-writer-integration.py` | PASS | Two synthetic TOY cases; 108 rows; 106,249 bytes; supervised producer/verifier/writer; temporary outputs removed |
| `scripts/check-finite-lineage-preparation-integration.py` | PASS | Synthetic success, worker crash, cap failure, injected I/O failure, ENOSPC reserve fallback, no conflicting terminal receipts and no automatic retry |
| `scripts/check-finite-lineage-execution-guard.py` | PASS | Synthetic clock gap/regression and deadlines; process-group stop/reap; partial preservation; bounded concurrent log draining; fail-closed log cap |
| `scripts/check-finite-lineage-bounded-memory-shape.py` | PASS | Placeholder shapes for 55 cases, 4,440 truths, 440 projections, 6,712 pairs and 32 certificates; 30,244,864-byte peak RSS |
| `scripts/check-finite-lineage-streaming-memory.py` | PASS | 1,077,936 placeholder rows (451,622,010 bytes); 20,463,616-byte worker peak RSS; 128 MiB limit; temporary output removed |
| `scripts/check-finite-lineage-resource-shape.py` | PASS | 1,077,936 placeholder rows at 420 bytes each (452,733,120 bytes); exact cap and one-over rejection controls; 555,217,408-byte complete-package upper bound; 6.087 seconds; temporary output removed |

The synthetic resource file SHA-256 was `ed69ae4b52da22cb932595d79af11a2ba2e2bcb4e61591610a4143deba450fad`; it is a generated placeholder artifact and was deleted after verification. The 128 MiB checks report the measurement made by each helper (worker or process RSS) and do not establish the complete future process-tree peak on semantically valid F4/F5 inputs.

## Interpretation and remaining limits

The supported-runtime rerun confirms the answer-free control suite still passes under Python 3.12.13. Run-to-run RSS varies; the measurements above are individual observations, not worst-case guarantees. The complete 55-case producer/verifier/writer, exact certificate values, full process-tree peak, host suspension, actual disk or metadata exhaustion, and persistent filesystem-sync failures remain unmeasured. An identifiable external reviewer has not been selected. No entry decision, source/input freeze, Test registration, resource commitment, candidate corpus, or research run follows from this revalidation.
