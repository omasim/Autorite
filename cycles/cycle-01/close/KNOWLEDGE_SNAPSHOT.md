# Cycle 01 — Canonical knowledge snapshot

Date: 2026-10-12. Accepted with the close bundle under D-0012. The snapshot is the completed CLOSED Git commit identified by the living manifest's `snapshot_ref` and the immutable `cycle-01-close` tag. The tag and reference must resolve to the same commit; the later PUBLISHED state retains this anchor.

## Evidence inventory and closed state

`KNOWLEDGE_SNAPSHOT.json` reconstructs the actual pre-close evidence cutoff `4b9916491491d3c94e251b64589c79a40b99ece4`: every retained baseline/research/graph/legacy/decision/review file hash, 38 typed records, declared semantic relations, typed references, six forward Question traces, four backward Result traces and the then-resolved twelve obligations. It remains a dated evidence inventory; it does not falsely describe that cutoff as already closed.

The completed close commit additionally contains D-0012, the close bundle and all thirteen resolved obligations. Its living graph has 39 records: six Questions, four ResearchPackages, five Tests, four Results, twelve Decisions and eight Sources. No Claim or Assumption instance is present. The historical Checkpoint A graph remains a separate 33-record snapshot, not silently expanded to this final inventory.

| Knowledge object | State at closure |
| --- | --- |
| Cycle 01 | CLOSED, 13/13 equal obligations; subsequently PUBLISHED after deployment verification |
| RP002A/RP003/RP004/RP005A | CLOSED finite commitments |
| R-RP002A002/R-RP003001/R-RP004001/R-RP005A001 | VALID, with their original scope, protocols, raw artifacts and interpretation limits |
| First RP002A confirmation attempt | INCOMPLETE, no Result and no aggregate decisions; clock/suspension discrepancy preserved |
| Q-0/Q-2/Q-3/Q-4 | ACTIVE; scoped evidence does not resolve the foundational questions |
| Q-1/Q-5 | OPEN; no executed revision/relational package |
| PC01–03 / PC04–06 | FROZEN / DRAFT, retained under Foundation Review 1 |
| DAM X | Completed secondary-report pilot, not original-model validation; two S4/one S5 provisional candidates and seven unresolved survival assessments |
| Next direction | Query-relative lineage field-ablation preparation selected; Cycle 02 entry and execution still require separate review |

The four outcome families and every negative, equivalent and indeterminate observation are indexed in the close bundle. No common success rate, novelty clearance, validated legacy theory, broad transfer or promoted scientific Claim follows from the snapshot. Internal review and source checks are not external scientific review.

## Reconstruct and verify

- [Immutable close source](https://github.com/omasim/Autorite/tree/cycle-01-close)
- [Resolved manifest](https://github.com/omasim/Autorite/blob/cycle-01-close/cycles/cycle-01/manifest.json)
- [Complete evidence inventory](https://github.com/omasim/Autorite/blob/cycle-01-close/cycles/cycle-01/close/KNOWLEDGE_SNAPSHOT.json)
- [Close bundle](https://autorite.net/sources/cycle01-close-bundle/) and [D-0012](https://autorite.net/sources/cycle01-close-decision/)

`python3 scripts/check-cycle01-close.py` reconstructs historical hashes and graph structure from Git, checks the completed snapshot's manifest and close outputs, and verifies any existing close tag. The initial assembled commit points to the already existing evidence cutoff; before publication the living reference is pinned to the completed CLOSED commit. The tag is created after the checked merge, and subsequent checks reject any mismatched tag. Source-history binding is separate from scientific truth.

Publication provenance is recorded only after actual deployments succeed. Later corrections or new evidence use new records and Decisions; the close anchor and this dated evidence inventory are retained.
