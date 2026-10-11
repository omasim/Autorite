# RP004 — Audited finite branching lineage representations

2026-10-11. Run `audit-20261011-001` is COMPLETE. Test TST-RP004001 has scoped Result R-RP004001 (VALID). RP004 is ACTIVE pending package interpretation and disposition; Q-0 and Q-4 remain ACTIVE. Cycle 01 remains ACTIVE with 2/13 obligations resolved (15.4%).

## What was audited

Six fixed constructions, G0–G4 and auxiliary one-parent control C4, use the same known handles a,b,c and state A. The frozen protocol defines strict ancestry, shared roots, complete parents, birth operation and input availability alongside exact state equality. Every ordered pair, including self pairs, is queried in each binary family; every entity is queried in each unary family. There are 216 construction/query answers and 864 representation/decoder rows.

The implementation was committed and explicitly reviewed before the complete corpus was calculated: [source freeze db7f8ee475e2509cd46db665a27fc00c41ffb7a9](https://github.com/omasim/Autorite/commit/db7f8ee475e2509cd46db665a27fc00c41ffb7a9). A manifest and frozen input snapshot binding all 15 input hashes were written before outputs. The prior preparation controls already disclosed selected answers and three information-loss witnesses; this audit verifies the complete finite corpus and its record rather than discovering an independent statistical effect.

## Decoder results

| Representation | Correct | Unknown | Wrong | Total |
| --- | ---: | ---: | ---: | ---: |
| R0 state map | 90 | 126 | 0 | 216 |
| R1 single retained parent | 141 | 75 | 0 | 216 |
| R2 complete untyped DAG | 201 | 15 | 0 | 216 |
| R3 complete DAG with birth kinds | 216 | 0 | 0 | 216 |

Across representations: 648 correct, 216 UNKNOWN, zero wrong, total 864. UNKNOWN is a separate abstention, never False or an empty parent set. These counts describe the specified conservative decoders; R1 intentionally abstains on some recoverable negatives. Answer counts are not a ranking of optimal algorithms or a representation-minimality proof.

| Query family | Total per representation | R0 correct / unknown | R1 correct / unknown | R2 correct / unknown | R3 correct / unknown |
| --- | ---: | ---: | ---: | ---: | ---: |
| same_state | 54 | 54 / 0 | 54 / 0 | 54 / 0 | 54 / 0 |
| ancestor | 54 | 18 / 36 | 27 / 27 | 54 / 0 | 54 / 0 |
| shared_root | 54 | 18 / 36 | 40 / 14 | 54 / 0 | 54 / 0 |
| parents | 18 | 0 / 18 | 10 / 8 | 18 / 0 | 18 / 0 |
| birth_kind | 18 | 0 / 18 | 10 / 8 | 10 / 8 | 18 / 0 |
| alive | 18 | 0 / 18 | 0 / 18 | 11 / 7 | 18 / 0 |

All audited states are equal, so same_state has only positive answers in this corpus. Separate engineering tests cover unequal states. R0's answered ancestry/root queries are the 18 self queries in each family: strict self-ancestry is False, and sharing one's own root set is True. It answers no other lineage query. R2 answers all topological inquiries but abstains on eight non-root birth kinds and seven internal-entity availability questions. None of these counts is a population frequency or uncertainty estimate.

## Same-projection collision certificates

Every unordered case pair was compared under every representation: 15 pairs times four, 60 records. Matching projections were tested on all 36 aligned queries. A witness is a case-pair/representation/query record with identical projected data and different construction truth. Repeated witnesses across representations are counted separately.

| Representation | Compared pairs | Matching projection pairs | Pairs with conflicting truth | Witness queries |
| --- | ---: | ---: | ---: | ---: |
| R0 | 15 | 15 | 15 | 129 |
| R1 | 15 | 2 | 2 | 9 |
| R2 | 15 | 1 | 1 | 3 |
| R3 | 15 | 0 | 0 | 0 |

There are 141 witness records, not 141 independent discoveries. R0's entire corpus has the same state-only projection. Its witness families are ancestry (22), shared roots (44), parents (21), birth kind (26) and availability (16); state equality has none.

R1 has two matching pairs. G1/G2 supplies three witnesses: copy versus fork for b and c, and surviving versus consumed a. G4/C4 supplies six: ancestor(b,c), shared_root(b,c), shared_root(c,b), parents(c), birth_kind(c) and alive(b). A merge's second parent b and its consumption disappear when only a is retained. R1 therefore returns UNKNOWN, not a false denial of that second ancestry edge.

R2 retains both parents of the merge and answers every ancestry, root and parent query. Its one matching pair is G1/G2: two copies and a symmetric fork have the same parent DAG, but birth_kind(b), birth_kind(c) and alive(a) differ. Operation distinctions are required to answer those inquiries exactly over a domain containing both constructions, unless equivalent information is supplied elsewhere.

R3 has distinct projections for all six cases and answers all specified queries. Absence of a matching pair in this corpus does not establish injectivity on every valid construction. The audit establishes finite-corpus sufficiency of this implementation, not universal sufficiency or necessity of retaining the whole R3 graph.

## Independent replay, resources and artifacts

Independent replay imports no producer code. It reconstructs entities, direct parents, birth kinds and consumption from construction logs, calculates Boolean matrix reachability, rebuilds projections and decodes them independently. It verifies all 864 rows, exact types and ordering, all 216 construction/query answers, all 60 comparisons, every witness and every summary denominator. The six constructions and previously disclosed calibration controls also pass. Six output hashes and all 15 committed input hashes match. The complete seven-file run inventory is preserved.

One process, no random seed, no network in the audit. Python 3.12.14; 0.085009708 monotonic seconds and 30,343,168 bytes peak resident memory (28.94 MiB), within the fixed 60-second / 128-MiB limits. No failure or retry occurred. The first directory was created exclusively; future invocations refuse to overwrite it.

Run artifacts in the canonical repository:

- [Manifest](https://github.com/omasim/Autorite/blob/main/research/RP004/runs/audit-20261011-001/manifest.json) and [frozen input snapshot](https://github.com/omasim/Autorite/blob/main/research/RP004/runs/audit-20261011-001/frozen-inputs.json).
- [All 864 saved answers and projections](https://github.com/omasim/Autorite/blob/main/research/RP004/runs/audit-20261011-001/answers.jsonl).
- [All 60 comparisons and complete collision witnesses](https://github.com/omasim/Autorite/blob/main/research/RP004/runs/audit-20261011-001/collisions.jsonl).
- [Summary](https://github.com/omasim/Autorite/blob/main/research/RP004/runs/audit-20261011-001/summary.json), [independent replay record](https://github.com/omasim/Autorite/blob/main/research/RP004/runs/audit-20261011-001/replay.json) and [timing](https://github.com/omasim/Autorite/blob/main/research/RP004/runs/audit-20261011-001/timing.json).

Verification command: `python3 scripts/check-rp004-audit.py`. It reads the committed evidence and replays every row; it does not create a replacement run. The Test registration and complete Result are available as [TST-RP004001](https://github.com/omasim/Autorite/blob/main/research/RP004/audit-001/RECORD.md) and [R-RP004001](https://github.com/omasim/Autorite/blob/main/research/RP004/audit-001/result/RECORD.md).

## Internal outcome review and interpretation limits

The explicit internal review accepts this scoped evidence as VALID because the declared corpus, complete coverage, conservative decoder soundness, resource limits, input/source provenance and independent replay all pass. No predeclared query, representation, construction, budget or expectation was changed after outcomes. The evidence records information collapse for precisely identified inquiries, and topological versus operational distinctions in this finite synthetic domain.

The known entity universe is shared side information. Opaque handles align across cases; R1 selects a parent by arbitrary lexicographic order. R3 omits event chronology, fork grouping, ownership and contribution weights. All cases have three entities and equal states, and the six-construction corpus is not the full space of valid DAGs. Copy/fork consumption and two-input merge are operational toy rules, not physical identity or Git semantics. Conservative abstention is not itself a proof that an answer is unrecoverable. No novelty, empirical generalization, confidence interval, optimal decoder, metaphysical identity theory or universal continuation rule follows.

VALID is a Result status after this evidence review. RP004 remains ACTIVE pending a separate package interpretation/disposition review and explicit decision. No broad Claim, Q-0/Q-4 resolution or new Cycle obligation closure occurs. Next: review RP004's scoped commitment, its exclusions and any reopening conditions before deciding package disposition.

Read the [pre-outcome operational protocol](https://autorite.net/sources/rp004-operational-protocol/), [implementation review](https://autorite.net/sources/rp004-audit-execution-review/) and [targeted prior-art review](https://autorite.net/sources/rp004-prior-art/).
