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
