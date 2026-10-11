# RP004 — Pre-execution implementation review

2026-10-11. Explicit internal self-review before observing the complete target corpus audit. The user requested continuation of the published RP004 audit. The preparation protocol, disclosed expectations and frozen baseline are unchanged.

## Reviewed execution contract

The configuration fixes six constructions (G0–G4 and auxiliary C4), handles a,b,c, R0–R3, three binary query families on all nine ordered pairs and three unary query families on all three entities. This is 216 construction/query answers and 864 representation/query rows. Row order is case inventory, query family, lexicographic argument tuple, then representation. Every row saves its ordinal, case, query, construction truth, complete projection, decoder answer and correct/unknown/wrong score. All UNKNOWN answers remain in denominators.

All 15 unordered case pairs are compared under each representation (60 records). Equal projections are checked against all 36 aligned queries; every differing truth answer is saved as a collision witness. Reports distinguish matching projection pairs, pairs with at least one conflicting query, and the number of conflicting queries. Unequal projections have no collision witnesses. Decoder abstention alone is not an information-loss certificate or a proof of minimal representation.

The producer uses the reviewed construction and parent-traversal implementation. Independent replay imports no producer, truth, projection or ancestry function. It rebuilds entities, parent sets, birth kinds and consumed inputs from the event logs, computes reachability by Boolean matrix closure, reconstructs projections and decodes them separately. It checks exact serialized types, coverage/order, all rows, all 60 pair comparisons, every witness and every per-representation/per-family denominator. Input validation independently checks live inputs, freshness, operation arities, equal-state copy/fork and the acyclic construction contract.

## Pre-execution verification and provenance

Engineering tests use only the previously disclosed 54 fixture answers and decoder controls, one disclosed merge-loss row, trivial early same-state rows and deliberately incomplete/duplicated data. They do not produce the target complete-corpus aggregate counts or collision inventory. Tests exercise guard termination, malformed logs, type coercion, source hint leakage, configuration drift, truncation and ordinal mismatch.

Before computing outputs, the runner requires Python >=3.11 and a clean tracked source, checks all 15 input files byte-for-byte against the source commit, and creates the frozen input snapshot and manifest. Inputs include protocol, fixtures, prior-art, preparation review, original lineage code, configuration, producer, independent replay, this review, Test registration, runner, audit checker, preparation checker and both unit-test files. The exact command is `python3 scripts/run-rp004-audit.py --run-id audit-20261011-001`. The runner refuses any existing run directory.

One process and one attempt; no random seed and no network in the audit. A 60-second timer and monotonic guards bound generation plus replay, with process peak resident memory <=128 MiB. Guards run at startup, every row/comparison/query and completion. Save measured elapsed time and memory. Seven completed-run files are declared: manifest, frozen-inputs, answers, collisions, summary, replay and timing. Six output hashes are finalized in the manifest after writing; original committed run bytes must remain immutable.

An exception preserves partial files plus failure metadata with INCOMPLETE status. Do not overwrite or automatically retry a failed run or create a VALID Result without complete provenance, resource, coverage and independent replay checks. After execution, a separate outcome review may accept a bounded Result. Test registration and an ACTIVE package do not resolve a Cycle obligation. Q-0 and Q-4 remain ACTIVE; Cycle 01 remains ACTIVE at 2/13 (15.4%).

Read the [operational protocol](https://autorite.net/sources/rp004-operational-protocol/) and [targeted prior-art review](https://autorite.net/sources/rp004-prior-art/).
