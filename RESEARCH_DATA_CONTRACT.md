# Research Data Contract v0.1
Cycle 1 uses Markdown + YAML frontmatter.

## Object namespaces
Q-, C-, A-, TST-, R-, D-, SRC-, RP-.

## MVP object types
Question, Claim, Assumption, ResearchPackage, Test, Result, Decision, Source.

## Invariants
- IDs unique repository-wide.
- Referenced IDs must exist.
- Status must belong to object type.
- Superseded objects remain stored.
- Public claims require scope and `does_not_imply`.
- Result statuses are VALID/INVALIDATED; SUPPORTED/FALSIFIED belong to claims.
- No automatic transitive edge inference.
- Invalidated evidence cannot silently remain sole support for a supported current claim.

## Projection
Shared content code parses canonical records into:
1. stable/public projection for autorite.org;
2. live/operational projection for autorite.net.
Neither website writes canonical research records at runtime.

## Implementation profile
This profile completes serialization rules without adding scientific object types, epistemic statuses or relations. Validate living records only; baseline and historical packages are source documents, not duplicate graph records.

### Common fields
Every graph record requires `schema_version: "0.1"`, `id`, `type`, `title`, `created_at`, `updated_at`, `source_refs` and `relations`, followed by a non-empty Markdown body. Dates use ISO 8601; `updated_at` cannot precede `created_at`. `source_refs` contains repository-relative file paths with optional headings; `relations` contains `{relation, target}` entries referencing graph IDs.

IDs use the listed namespace followed by an uppercase alphanumeric suffix. Preserve existing labels such as Q0 and RP002A in `aliases`; use Q-0 and RP-002A as graph IDs. Existing DECISION-0001/0002 documents may be referenced through `source_refs` by D-0001/0002 records. Aliases must be unique and cannot shadow IDs. Filenames and titles do not determine identity.

| Type | Prefix | Status | Additional required fields |
| --- | --- | --- | --- |
| Question | Q- | OPEN, ACTIVE, PARTIALLY_RESOLVED, RESOLVED, REFORMULATED | `question`, `scope` |
| Claim | C- | Empirical: PROPOSED, SUPPORTED, FALSIFIED, INDETERMINATE; formal: CONJECTURED, PROVED, DISPROVED | `claim_kind` (empirical/formal), `statement`, `scope`, `assumption_refs`, `does_not_imply`, `limitations`, `change_conditions` |
| Assumption | A- | No status field in v0.1 | `statement`, `scope` |
| ResearchPackage | RP- | PLANNED, ACTIVE, BLOCKED, CLOSED | `question_refs`, `scope`, `protocol_ref`, `cycle_ref` |
| Test | TST- | No status field in v0.1 | `package_ref`, `protocol_ref`, `target_refs` |
| Result | R- | VALID, INVALIDATED | `test_ref`, `package_ref`, `run_ref`, `artifact_refs`, `observations` |
| Decision | D- | ACTIVE, SUPERSEDED, REOPENED | `decision`, `rationale`, `affected_refs` |
| Source | SRC- | No status field in v0.1 | `citation`, at least one of `url` or `repository_path` |

Arrays must be explicit, including empty arrays. Required strings cannot be empty; unknown values must be disclosed in the body and cannot satisfy an execution gate. Interpretations that do not fit empirical/formal Claim remain typed editorial prose linked to records. Do not invent a third claim kind.

`status` is required only for types with a baseline vocabulary; it is forbidden on Assumption, Test and Source. Their absence of status is not evidence of validity. Workflow metadata must not substitute for epistemic status. Unknown keys fail validation so spelling errors cannot silently alter semantics.

### Relations
An edge reads `source relation target`. `tests`: Test → Claim/Question; `supports` and `challenges`: Result/Claim → Claim; `depends_on`: any graph record → any graph record; `derived_from`: any graph record → any graph record; `supersedes`: same type → same type; `informs` and `inspired_by`: any graph record → any graph record. These are permitted serialization endpoints, not assertions that an edge is scientifically justified. Every edge requires an explanation in the record body. No self-edges, duplicate edges or cycles in `supersedes` chains.

Non-edge reference fields also require existing records of the indicated type. `question_refs` targets Questions; `assumption_refs` targets Assumptions; `package_ref` targets ResearchPackage; `test_ref` targets Test. File references must exist inside the repository and cannot traverse outside it. A Result's Test must belong to the same ResearchPackage. `source_refs` establishes provenance without generating graph edges.

SUPPORTED/PROVED Claims require a non-empty justification in the body and explicit supporting records or proof artifact references. A validator checks presence and references, not scientific truth. INVALIDATED Results require `invalidation_reason` and `invalidation_decision_ref`; retain their original observations and artifacts. A claim losing its only valid support must be flagged for explicit review and must block publication of the current supported projection until resolved. Never promote or demote a claim automatically.

### Cycles and runs
Cycles are governance manifests under `cycles/cycle-NN/`, using the lifecycle already specified by baseline, not a ninth graph object type. Required manifest fields: `schema_version`, `cycle_number`, `title`, `status`, `package_refs`, `obligations`, `close_decision_ref`, `snapshot_ref`, `publication_refs`. The last three may be null/empty before their lifecycle gates. `cycle_ref` is a manifest path, not a graph ID.

Run metadata and review/publication artifacts are repository files referenced by records, not new graph types. Each run has a unique repository-relative directory, an immutable configuration/seed/environment manifest, and checksums for outputs. Corrections create a new run directory. Invalidation is recorded in a Decision/Result record rather than editing original run artifacts.

### Validation boundary
The implementation uses optional `proof_artifact_refs` on Claim records and a nonempty `## Justification` body section for SUPPORTED/PROVED claims. Run directories contain `manifest.json` with nonempty `configuration`, `seeds`, `environment` and `outputs` (relative output path to SHA-256). Once a run manifest enters Git, its complete directory is compared with that first committed snapshot; corrections use a new directory. These serialization choices add no scientific types or statuses.

Validate schema, unique IDs/aliases, all graph/file references, status compatibility, relation endpoints, supersession chains, Result/Test package agreement, claim limitations/support, run artifact checksums, and Cycle lifecycle gates. Both site projections consume the same validated records. Scientific review remains explicit and is never inferred from a successful build.
