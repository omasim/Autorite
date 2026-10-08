# Cycle Governance v0.1

## Program status
Autorite is an **open-ended research program**. The program itself has no terminal `CLOSED` state.

\[
Autorite = C_1 \rightarrow C_2 \rightarrow C_3 \rightarrow \cdots
\]

This sequence does not assume convergence to a final theory.

## Cycle status
Individual Cycles are finite research commitments and may close.

Lifecycle:
`PLANNED → OPEN → ACTIVE → REVIEW → CLOSED → PUBLISHED`

`CLOSED` means the Cycle's declared research obligations have been resolved as completed, validly blocked, falsified, indeterminate or explicitly transferred. It does **not** mean all questions were solved.

## Mandatory Cycle close outputs
Every closed Cycle publishes:
- Cycle Manifest and initial questions;
- packages executed;
- preregistrations/protocols;
- valid negative and positive results;
- deviations and invalidated runs;
- Synthesis Review;
- Foundation Review where applicable;
- What Changed;
- What Remains Open;
- canonical knowledge snapshot;
- Transition Record for the next Cycle.

## Next Cycle
Cycle N+1 is generated from Cycle N evidence and Transition Review, not from a fixed long-range roadmap.

## Completion
Cycle completion is **not time-based**. It is derived from declared research obligations. Days elapsed may be displayed secondarily but never determine the Cycle Ring.

## Git anchors
Recommended lifecycle anchors:
- `cycle-NN-open`
- `cycle-NN-checkpoint-*`
- `cycle-NN-close`

`main` remains the living current state. `cycle-NN-close` is an immutable historical snapshot.

## Implementation: obligations and ring
Each manifest declares a fixed list of obligations before ACTIVE. Each entry has a unique local `key`, `description`, positive integer `weight`, boolean `resolved`, nullable `resolution`, `evidence_refs` and nullable `decision_ref`. These fields are governance metadata, not graph object types or epistemic statuses.

Use equal weights of 1 for Cycle 1. `resolution` is one of the baseline closure meanings: completed, validly_blocked, falsified, indeterminate, explicitly_transferred. Unresolved entries use `resolved: false`, `resolution: null`. Every resolved entry requires existing evidence; blocked, indeterminate and transferred resolutions also require an ACTIVE Decision with rationale. Transfers identify the receiving commitment and its acceptance. Negative outcomes resolve an obligation only after the declared work and review are documented.

The canonical loader computes `resolved_weight / total_weight`; sites never store their own percentage. An empty obligation list is invalid. Changing the denominator after activation requires a Decision explaining the old/new obligation list and effect on progress, with history preserved. No partial credit or time-based increments.

Cycle 1 requires separately tracked obligations for each of the four package dispositions; DAM X pilot; Checkpoint A; forward/backward graph validation; Synthesis Review 1; Foundation Review 1; What Changed; What Remains Open; Transition Record/Cycle 2 decision; and a close bundle containing the manifest, protocols, all positive/negative results, deviations, invalidations and knowledge snapshot. Review obligations must actually be completed to close the Cycle; a package being blocked does not waive reviews or documentation. DAM X remains unresolved until source material permits the pilot or an explicit documented disposition is accepted.

The close bundle is the final obligation. It requires all other obligations resolved, valid artifact references and an ACTIVE close Decision. The explicit close change sets the final obligation resolved and the Cycle to CLOSED together. Thus computed progress of 100% is valid only for CLOSED or PUBLISHED; other states must be below 100%. Publication verification moves CLOSED to PUBLISHED, requires `publication_refs`, and retains the full ring. Publication does not reopen the Cycle or erase its closed history. The close snapshot is a Git commit reference, and the later immutable close tag points to that commit; do not require a tag to exist before the commit can be validated.
