# Finite-lineage conflict-row bound clarification — 2026-10-21

**Status: preparation-only arithmetic clarification.** This note uses only the registered RP006 query definitions, fixed F4/F5 inventory counts, and projection semantics. It reads no candidate corpus, produces no answer-bearing output, and changes no research authorization.

## Finding

The configured `1,077,936` conflict-row figure is a deliberately loose inventory-derived upper bound, not a semantically attainable target. The separate placeholder test that writes that many rows validates the writer's configured row-count and byte caps; it does not model a possible RP006 result.

For every mask that retains a field, equality of the corresponding projection fixes the answers to queries determined by that field. Such answers cannot become conflict witnesses:

| Retained field | Family | Queries fixed when projections are equal | Per-pair query rows excluded for each such mask |
| --- | --- | --- | ---: |
| `state` | `FULL` | `same_state` | `n²` |
| `parents` | `FULL` | `ancestor`, `shared_root`, `parents` | `2n² + n` |
| `birth_kind` | `FULL` | `birth_kind` | `n` |
| `parents` + `birth_kind` | `FULL` | `alive` | `n` |
| `state` | `TOPOLOGY_STATE` | `same_state` | `n²` |
| `parents` | `TOPOLOGY_STATE` | `ancestor`, `shared_root`, `parents` | `2n² + n` |

There are four masks retaining each field and two masks retaining both `parents` and `birth_kind` (`011` and `111`). In the RP004 semantics, an entity is consumed exactly when it is a parent of a non-`copy` event; the direct-parent map and each child's birth kind therefore determine `alive`. Thus those two masks also rule out `FULL` conflicts on `alive`.

Applying only these necessary exclusions to the fixed inventory gives:

| Stratum | Raw inventory upper bound | Rows ruled out by retained-field determinacy | Remaining conservative upper bound |
| --- | ---: | ---: | ---: |
| F4 (`n=4`, 136 unordered pairs) | `1,088 × (60 + 52) = 121,856` | 59,840 | 62,016 |
| F5 (`n=5`, 703 unordered pairs) | `5,624 × (90 + 80) = 956,080` | 471,010 | 485,070 |
| Total | **1,077,936** | **530,850** | **547,086** |

The remaining `547,086` is still only a conservative upper bound: it assumes every other counted comparison has equal projections and conflicts on every query. This note does not claim that the bound is attainable. More event-semantic dependencies may lower it further.

The existing `1,077,936` hard row ceiling and its placeholder-cap test may remain as a conservative defensive limit. The full-package estimate based on that ceiling also remains valid, though loose. A semantic workload at `1,077,936` rows is impossible under the registered projection/query rules and must not be requested as a research acceptance condition.

## Reproduction arithmetic

Let `p4=17 choose 2=136`, `p5=38 choose 2=703`, and let `n` be the aligned entity count. For each stratum, subtract four masks per retained field:

```text
excluded(n,p) = p × {4 × [FULL: n² + (2n²+n) + n
                           + TOPOLOGY_STATE: n² + (2n²+n)]
                       + 2 × FULL: n (alive from parents and birth_kind)}
remaining(n,p) = 8p × [FULL: (3n²+3n) + TOPOLOGY_STATE: (3n²+n)]
                  - excluded(n,p)
```

This is a counting argument over query types, not an execution, sample, or result. It should be reviewed alongside the exact-hash supplemental engineering packet.
