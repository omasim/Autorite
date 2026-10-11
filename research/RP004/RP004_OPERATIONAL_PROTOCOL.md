# RP004 — Operational branching lineage protocol v0.1

2026-10-11. Preparation supplement to the frozen `baseline/v0.1/RP004_PROTOCOL.md`, under PC01 and PC02. The baseline is unchanged. RP-004 remains PLANNED; Q-0 and Q-4 remain ACTIVE. These controls disclose expected outcomes, not a completed research audit.

## Question and finite subject

Which distinctions must a representation retain to answer specified continuation inquiries under copying, branching and merging? The subject is a synthetic entity construction, not a person, organism, metaphysical identity or human judgment. “Continuation” is operationalized only through the six queries below. No single identity predicate is introduced.

Entities have opaque unique handles and immutable nonempty string states. An ordered construction log produces a finite DAG: every input must already exist and be live; every output must be fresh. The validator permits at most 12 entities. Edges point conceptually from input to output; storage lists immediate parents on each output. Ancestry is strict, so an entity is not its own ancestor. A root set includes the entity itself when it has no parents.

## Construction and merge semantics

| Operation | Inputs | Fresh outputs | Effect on input availability |
| --- | --- | --- | --- |
| root | 0 | 1 | Creates an independent lineage origin |
| continue | 1 | 1 | Consumes the input; output state may differ |
| copy | 1 | 1, equal state | Input remains live |
| fork | 1 | 2, both equal state | Consumes the input; neither output is preferred |
| merge | 2 distinct live inputs | 1 | Consumes both inputs |

Consumption means unavailable for later construction, not deletion from historical records. All fresh outputs start live. A merge declares both inputs as structural contributors; its output state is explicitly supplied. No averaging, conflict resolution, inheritance weight, content attribution or physical fusion is inferred from that state. The merge output descends from both parents, and its root set is their union. The parents do not become ancestors of each other. Parent order has no semantic role. This deliberately small two-input model excludes multiway merges, unavailable inputs and cycles.

Copy/fork state equality is exact. Other operations may change the state. Equal strings never create an ancestry edge. Ground truth follows solely from executing the construction log and its consumption rules. Fixture names, row order and human intuition are unavailable to a representation decoder.

## Disclosed cases

All six controls use the same handles `a,b,c`, each with state `A`. Handles align query arguments across cases but contain no root, operation or case labels.

| Case | Construction after roots | Final live entities | Purpose |
| --- | --- | --- | --- |
| G0 | root a; continue a to b; continue b to c | c | Linear succession |
| G1 | root a; copy a to b; copy a to c | a,b,c | Two copies while the original survives |
| G2 | root a; symmetric fork a to b,c | b,c | No privileged branch |
| G3 | independent roots a,b,c | a,b,c | Equal state without shared lineage |
| G4 | independent roots a,b; merge a,b to c | c | Two contributing parents |
| C4 | independent roots a,b; continue a to c | b,c | Extra one-parent collision control for G4 |

`RP004_FIXTURES.json` stores the logs and manually disclosed expectations. C4 is an auxiliary calibration control, not a sixth baseline case. Nine selected queries per case give 54 construction answers and 216 representation/decoder checks. They are engineered examples, not sampled data or an estimate of real-world frequencies.

## Representations and permitted collapse

For a fair query-domain comparison, all representations receive the same known entity universe and each entity's current immutable state. Historical entity states are retained in this controlled snapshot; R0 is not merely the terminal live frontier. The universe itself is thus shared side information. Claims do not extend to representations where entities disappear or handles encode chronology. No case name, event order, final live list or expected answer is encoded.

| Representation | Encoded information | Deliberately removed |
| --- | --- | --- |
| R0 | Handle to state map | All parents and operation types |
| R1 | R0 plus one immediate parent, or empty for a root | Other parents; all operation types |
| R2 | R0 plus complete immediate parent sets | Operation types |
| R3 | R2 plus each entity's birth operation type | Event chronology and fork event grouping |

R1 chooses the lexicographically smallest parent handle, including at a merge. Its single pointer is a retained edge, not an assertion that no other parent existed. This arbitrary tie-break is label-sensitive and gives no preferred original or biological meaning. Parent/root queries must not treat missing edges as negative facts. R3 retains the type on every derived entity, sufficient for the declared availability query; fork event grouping is unnecessary for this query family. It is not a complete event-log encoding.

## Exact inquiry family and decoder contract

| Query | Arity | Construction answer |
| --- | --- | --- |
| same_state(x,y) | 2 | Exact equality of strings |
| ancestor(x,y) | 2 | A positive-length parent-to-child path from x to y |
| shared_root(x,y) | 2 | Nonempty intersection of their full root sets |
| parents(x) | 1 | Sorted complete list of immediate parent handles |
| birth_kind(x) | 1 | root, continue, copy, fork or merge |
| alive(x) | 1 | Not subsequently consumed by continue, fork or merge |

All query handles must be present. Invalid names, arities and handles are errors, not UNKNOWN. `lineage.py` has a construction-derived truth function and a separate decoder taking only its projected data. UNKNOWN is JSON null / Python None, never False or an empty list.

All representations answer same_state. Strict self-ancestry is False and self shared_root is True under the acyclic rooted construction contract. R0 abstains on other lineage queries. R1 certifies ancestry/shared-root positives found in its retained forest, abstains on negatives, returns the empty parent set and root type for pointer-free entities, and abstains on all availability queries. Omitted merge edges can hide consumption of a retained-forest leaf. R2 answers all topological queries exactly, identifies root birth types, and certifies live leaves; it abstains on other operation and availability questions. R3 answers all six queries exactly through complete parents and types.

These are conservative decoders, not maximal inference algorithms. An abstention alone establishes neither impossibility nor minimality. There are intentionally recoverable negatives on which the R1 policy abstains. Nonrecoverability requires an admissible same-projection/different-truth witness, with aligned queries and handles.

## Disclosed information-loss witnesses

Three controls have identical serialized projections and different answers:

- R0: G0 versus G3, ancestor(a,c) is True versus False.
- R1: G4 versus C4, ancestor(b,c) is True versus False; the retained pointer for c is a in both cases.
- R2: G1 versus G2, alive(a) is True versus False. Their topology is identical, while copy and fork consume inputs differently. birth_kind(c) also differs.

Such a witness rules out an exact decoder for that query over a domain containing both constructions, without additional information. It does not establish that the entire R3 encoding is minimal, necessary for every inquiry, novel or universally adequate. Equal-state changes and opaque renaming are tested separately; labels are not a lineage oracle.

## Scoring, acceptance and resources

Each declared decoder answer is scored as correct, wrong or unknown against construction truth, with exact output types. Bool/int coercion is rejected. Record all three counts and the total for every representation and query family; unknowns stay in the denominator. Optional descriptive ratios are correct/total and unknown/total. Abstention never becomes an incorrect negative. Information-loss certificates are reported separately from decoder performance.

Preparation acceptance requires all disclosed expectations, identical-projection collision controls, rejection of malformed constructions, symmetry and renaming checks, sound non-UNKNOWN answers, frozen-baseline integrity, typed schema and site source/link checks. `python3 scripts/check-rp004-preparation.py` checks controls only and creates no run directory. Unit checks run with `python3 -m unittest discover -s tests -p test_rp004_lineage.py`. Standard library only, Python 3.11 or later for the planned recorded audit; preparation also works on Python 3.9.

## Next recorded audit and stopping rule

Commit and review this preparation before implementing execution. The planned deterministic audit uses only these six three-entity logs. It evaluates all ordered pairs, including self pairs, for each of the three binary queries (27 queries per case), and all three entities for the three unary queries (9). There are 36 queries per case, 216 construction/query rows and 864 representation/query rows. There are 15 unordered case pairs times four projections: 60 candidate collision comparisons, with all 36 aligned queries examined when projections match. This is a complete finite corpus audit, not an exhaustive enumeration of every constructible DAG.

Before executing, freeze a new immutable manifest binding the reviewed source commit, hashes of this protocol, fixtures, checker, tests, prior-art and preparation review, audit implementation and independent replay implementation; record environment, seed policy (none; deterministic), limits and output file inventory. Budget: one attempt, 60 monotonic seconds and 128 MiB peak process memory. Record measured usage. Stop on first malformed input, mismatch, unsound answer, missing coverage, replay discrepancy or resource limit. Preserve failure artifacts; do not create a VALID Result for an incomplete audit. A new attempt requires a separately recorded reason, with the old attempt preserved.

The next audit must save every projected query answer and construction truth, per-family/per-representation denominators, every finite-corpus collision witness and an independent log-to-truth replay that does not import the producer's truth or ancestry implementation. Recompute consumption, reachability and root sets independently; verify saved projections and counts as well as answers. Preparation is not execution: no Test, Result, broad Claim, disposition or Cycle resolution is created here. Later modifications preserve the reviewed supplement and disclose already-observed outcomes.

Read the [targeted prior-art review](https://autorite.net/sources/rp004-prior-art/) and [preparation review](https://autorite.net/sources/rp004-execution-review/).

Machine-readable [construction fixtures](https://github.com/omasim/Autorite/blob/main/research/RP004/RP004_FIXTURES.json) and [control implementation](https://github.com/omasim/Autorite/blob/main/research/RP004/lineage.py) are versioned in GitHub.
