# Cycle 03 external design review 001 — provenance record

**Review date:** 2026-10-18 (as stated in the report)  
**Reviewer:** Anonymous — Principal Distributed Systems & Data Infrastructure Engineer (industry), as stated by the submitter. The reviewer’s name and institution are withheld; identity and role have not been independently verified.  
**Independence/conflict disclosure:** The submitted report declares independence and no institutional, financial, or collaborative affiliation with the author or laboratory, and no prior exposure to legacy RP004/RP006 outcome artifacts, fixture corpora, or answer keys. This declaration is recorded as supplied, not independently verified.  
**Source attachment SHA-256:** `0a60071fd91d035b9f495e60a4fe44bb37645274f79399a1408f9914fa7bfccd`  
**Review category:** External human review as represented by the user; anonymous and not independently identity-verified. This is not an AI review.  

The review’s declared draft and supporting-file hashes were checked against the current local files when received and matched. The exact report follows.

---

CYCLE 03 ENTRY-REVIEW — DESIGN & SYSTEMS ASSESSMENT

PROVENANCE TO COMPLETE

⚬ Reviewer name and institution/organization: Anonymous — Principal Distributed Systems & Data Infrastructure Engineer (Industry)
⚬ Review date: 2026-10-18
⚬ Independence/conflict disclosure: Independent reviewer. No institutional, financial, or collaborative affiliation with the author or the laboratory. No prior exposure to legacy RP004 or RP006 outcome artifacts, fixture corpora, or answer keys.
⚬ Exact draft SHA-256 reviewed: 973ed516dc3e495002fea4ff320d2d8b084d2271112217c42aa8226e3fb66db7 (research/preparation/FINITE_LINEAGE_CHALLENGE_DRAFT.md)
⚬ Exact supporting-file hashes reviewed:
  ⚬ Review Packet (FINITE_LINEAGE_CYCLE03_REVIEW_PACKET.md): 36540f77613a76c0638ce143d5fa2e02101883ddc9b653af2d698ca0335d63a5
  ⚬ RP004 Semantics Excerpt (FINITE_LINEAGE_RP004_SEMANTICS_EXCERPT_2026-10-16.md): 44b22c907990094983f1a11dab7f087524cfc519379f204d91c18a682fc31138
  ⚬ RP004 Structural Export: b448013d9f849f51af1bf026c9bf7b666bd5110a32aa28315c84c1e2819ff1ea
  ⚬ Bounded Producer (research/RP006/producer.py): 899d6b3b0e70c6b4af420fdd19b9043e790547b92caac2376586da0e27ce8868
  ⚬ Independent Verifier (research/RP006/verifier.py): 9422bb99adfd45b3ab192d4750e3965b6de2569207e8b16bfc5336bb0c714a9e
  ⚬ Capped Writer (research/preparation/finite_lineage_writer.py): e6b1d82134bba57b2d725ad4e2b12da5d381da4ac03690acaa54731f1fbae865
  ⚬ Toy Bounded Pipeline Integration (scripts/check-finite-lineage-bounded-pipeline.py): 321dfe89dcbc034f669295264c3b495266646c366ed412c72de779e8dc9f6732
  ⚬ Streaming Memory Check (scripts/check-finite-lineage-streaming-memory.py): fe14b6bee2f54816ab95eef233b7a727abef885b85bdebcaf3aff9a8a26dcdb1
  ⚬ Bounded Memory Shape Check (scripts/check-finite-lineage-bounded-memory-shape.py): 223642681751a8483dc4b3b32e0e57604fdbf65c55326412fc6f3dc785c7dec1
  ⚬ Revalidation Record (FINITE_LINEAGE_REVALIDATION_2026-10-16.md): 47574479d6d9572395b5bf614abc35f93c814dbd64d8d5ae0d4c9c44e5272ed5
⚬ Materials or outcome-bearing files excluded from review: Full RP004 and RP006 operational protocols, legacy control answers, fixture files, candidate corpora, and prior answer-bearing outputs.
⚬ Disposition: Revise and return (Targeted engineering revision required: complete full 55-case synthetic pipeline memory profiling and enforce host-level process/resource ceilings prior to entry authorization).

DISPOSITION AND EVIDENCE

1. Decision Value and FULL vs. TOPOLOGY_STATE Separation

The finite lineage challenge demonstrates clear architectural utility beyond basic software verification. In production data systems, teams constantly face the trade-off between maintaining full causal payload histories (FULL) versus retaining only structural DAG geometry and terminal state summaries (TOPOLOGY_STATE).

⚬ FULL directly maps to high-overhead audit logging, regulatory provenance, and deterministic replay pipelines where every intermediate state transition must be reconstructed.
⚬ TOPOLOGY_STATE maps to lightweight state convergence, metadata-only lineage tracking, and conflict-free merge resolution where historical payload retention is prohibitively expensive.

Testing whether TOPOLOGY_STATE suffices to answer specific lineage queries without degrading decision accuracy provides actionable architectural guidance. The two modes represent distinct, real-world operational footprints.

2. Event Templates, Three-Value State Bound, and Cross-Case A/B/C Alignment

Under the sanitized RP004 construction and merge semantics (44b22c90...), all eight proposed event templates are structurally sound and legal.

⚬ Bounding the state space to three values is a well-justified engineering constraint. A binary state space is insufficient to represent asymmetric merge conflicts or indeterminate/divergent states, whereas an unbounded or higher-cardinality space triggers combinatorial explosion without adding new structural failure modes.
⚬ Canonical A/B/C alignment across cases is necessary to eliminate label-isomorphism noise during evaluation. One operational detail must remain strictly enforced: tie-breaking rules during symmetric diamond merges must not rely on runtime-dependent ordering (such as unseeded hash iteration), ensuring that A/B/C canonicalization remains invariant across executions.

3. D/L/R/O Overlap Definitions, Motif Reuse, and Exclusion Rule

The D/L/R/O structural overlap classification, paired with motif reuse tracking and the exclusion rule, is well-suited for evaluating structural transfer. A common failure mode in graph and lineage benchmarks is false generalization caused by local sub-graph memorization. By explicitly categorizing disjoint, directional (left/right), and overlapping topologies—and filtering out trivial motif repetitions via the exclusion rule—the design isolates genuine compositional transfer from surface-level pattern matching. Keeping motif reuse explicitly reported alongside the primary denominator prevents silent metric inflation.

4. Prior-Art Sufficiency and Contribution Boundaries

The selective prior-art review is sufficient to justify proceeding. From a systems engineering standpoint, the value of this package does not rest on inventing a new theoretical formalism for causal histories, version vectors, or data provenance.

⚬ Required limits on novelty language: The documentation must continue to avoid claiming foundational theoretical novelty in distributed state semantics or graph theory. Contribution claims must remain strictly anchored to what the package actually delivers: a hash-bound, control-blind, deterministically verifiable empirical harness for evaluating finite lineage resolution under bounded resource constraints.

5. Denominators, Producer/Verifier Separation, and Resource Ceilings

The separation between the bounded producer (899d6b3b...), the row-at-a-time streaming writer (e6b1d821...), and the independent verifier (9422bb99...) is architecturally clean. Replacing the in-memory list accumulation—which consumed 900,333,568 and 882,343,936 bytes across 1,077,936 conflict-stream rows—with a capped streaming writer operating at 14,516,224 bytes (~14.5 MB) worker RSS solves the primary serialization bottleneck.

However, a critical operational gap remains between the current revalidation evidence and full 55-case execution readiness:

⚬ The schema-shaped placeholder check (26,116,096 bytes across 55 non-witness inventories) validates static memory shape but bypasses actual producer traversal and verifier state-reconstruction logic.
⚬ End-to-end execution of the bounded producer and independent verifier has only been demonstrated on two toy cases.
⚬ While the streaming writer operates in O(1) row memory, both producer.py and verifier.py must maintain ancestor/state lookup structures across the lineage graph. On the most complex topologies within the 55-case inventory, maintaining or verifying state transitions across 10^6+ conflict rows risks non-linear memory growth or garbage-collection thrashing that two toy cases cannot expose.

REQUIRED REVISIONS OR REMAINING GATES

Before moving to a separate entry decision to open Cycle 03, the following engineering gates must be closed and recorded in an updated revalidation artifact:

1. 55-Case Synthetic End-to-End Dry Run (Process-Tree Peak Measurement): Without touching candidate corpora or answer-bearing fixtures, execute the full producer.py -> finite_lineage_writer.py -> verifier.py pipeline across 55 synthetic, control-blind stress topologies parameterized to match the maximum structural depth, branching factor, and row caps (1,077,936 rows) of the target inventory. Measure and record the full process-tree peak RSS (parent + all worker/verifier subprocesses) and per-case wall-clock execution time under Python 3.12.13.
2. Verifier State-Table Memory Bound Verification: Confirm and document that verifier.py bounds its in-memory state/ancestor retention proportionally to active frontier width or node count rather than scaling linearly with the 1,077,936 emitted conflict rows.
3. Mandatory Host-Level Execution Controls: Bind the following OS-level guards directly into the execution runner prior to authorizing any live run:
  ⚬ Process-Tree Memory Enforcement: Wrap the execution in a Linux cgroups v2 scope (MemoryMax set to the validated ceiling, MemorySwapMax=0 to prevent swap thrashing and ensure deterministic OOM termination) or enforce equivalent prlimit --as bounds across the process group.
  ⚬ Filesystem & Descriptor Guards: Enforce a hard OS file-size limit (ulimit -f) and open file descriptor cap (ulimit -n) alongside the application-level writer row cap to prevent runaway disk exhaustion on serialization anomalies.
  ⚬ Process Group Teardown & Timeouts: Implement strict per-case wall-clock and CPU timeouts that terminate the entire process group (os.killpg / SIGTERM followed by SIGKILL) to prevent orphaned worker processes on timeout failure.
  ⚬ Runtime Determinism: Explicitly lock PYTHONHASHSEED=0 in the execution environment contract to guarantee deterministic set/dict iteration order across producer and verifier runs.
