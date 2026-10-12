# RP006 implementation and engineering preflight review

Date: 2026-10-12. Internal preparation review; package PLANNED, Cycle 02 OPEN at 0/9. No registered research Test, recorded research attempt or scientific Result is accepted here.

The checked implementation source is `670af03aa058e74238d11e00a1c948cf703cea9e`. `preparation-001/manifest.json` binds eleven input hashes to that exact commit and preserves three output hashes. The [complete bundle](https://github.com/omasim/Autorite/blob/main/research/RP006/preparation-001/bundle.json), [independent replay receipt](https://github.com/omasim/Autorite/blob/main/research/RP006/preparation-001/replay.json), [manifest](https://github.com/omasim/Autorite/blob/main/research/RP006/preparation-001/manifest.json) and [resource measurements](https://github.com/omasim/Autorite/blob/main/research/RP006/preparation-001/timing.json) are retained in the preparation directory. The implementation commit must remain reachable in canonical history; the preparation tag may identify it without changing the original entry anchor.

## Implementation and independence

The producer uses RP004's preserved lineage construction/truth code and constructs whole-map state, complete-parent and birth-kind projections. Only the common entity universe and retained fields appear inside a projection. Outer case IDs identify artifacts and never enter the projection. Missing fields remain omitted, rather than becoming empty maps or false answers. Canonical exact JSON comparisons distinguish booleans from integers.

The verifier imports RP004's separate event-log replay code, reconstructs truth using matrix reachability/root evaluation and implements its own projection, equivalence-class scan and submask checks. It does not import the producer. Both paths deliberately share the declared semantics and known domain; code-path independence does not create new data or an external peer review. Full event logs, complete merge parents and explicit query arities remain required.

The certificates preserve every conflicting pair/query witness, every projection class with its common truth vector or conflict marker, every proper-submask verdict and all incomparable inclusion-minimal masks. Monotonic sufficiency is checked. Minimality concerns field-set inclusion within eight masks; it does not optimize bytes or bits.

Twenty-four added software controls pass: exact dimensions, wrong/missing/extra truth and pair rows, bool/int coercion, missing conflict witnesses, hidden IDs, omitted-versus-empty fields, complete merge parents, false minimality, corrupt class truth and submask coverage, corrupt summary, verifier independence, opaque renaming, parent order, sidechannels, malformed consumed events, query/arity/handle rejection and injected stops. Resource controls cover deadline, clock gap, rollback and peak RSS failure. Existing research controls remain required in CI.

## Observed known-domain software outputs

This engineering preflight has already exposed the classifications below. A later recorded audit can establish reproducibility of known outputs; it cannot be described as a fresh blinded confirmation. The six constructions were already known from RP004 before implementation.

Mask order is state / complete parents / birth kind. All 216 truth rows, 48 projections, 120 case-pair/mask comparisons, 438 conflict rows and 16 family/mask certificates independently replay.

| Family | Sufficient masks | Inclusion-minimal masks | Conflict rows | Equality-gated query checks |
| --- | --- | --- | --- | --- |
| FULL | 001, 011, 101, 111 | 001 | 264 | 1,152 |
| TOPOLOGY_STATE | 001, 010, 011, 101, 110, 111 | 001, 010 | 174 | 960 |

Birth-kind patterns distinguish the six known cases, so K-only licenses a finite lookup in this declared corpus. It is not a general ancestry decoder: new logs can share the same birth-kind map and differ in parents. All state payloads here are A; conclusions about deleting state have correspondingly narrow scope. Complete parents alone suffice for the topology/state family on these examples, while FULL retains queries that distinguish birth kind/aliveness. The two minimal topology/state masks are incomparable. No unseen-domain sufficiency, universal history necessity, novelty clearance or Q-4 reduction follows.

## Preserved resource preflight and remaining execution gate

On macOS arm64 with Python 3.12.14, the measured computation took 0.026336667 monotonic seconds and 0.026336908 civil elapsed seconds, with lifetime peak process RSS 27,426,816 bytes (about 26.16 MiB). The timer starts after provenance checks/imports and includes generation, independent replay and serialization. There are no child processes inside that measured computation. These measurements establish feasibility for this small local computation, not a runtime guarantee on another host.

The engineering guard rejects elapsed time above 60 seconds, a civil/monotonic gap above two seconds, clock regression and sampled lifetime peak RSS above 134,217,728 bytes. Darwin's `getrusage(2)` reports RSS in bytes; Linux conversion uses KiB. Unsupported platforms fail. The timer policies use [Python time](https://docs.python.org/3/library/time.html) and [resource](https://docs.python.org/3/library/resource.html), with local Darwin `getrusage(2)` documentation checked for its unit.

The guard is cooperative. It does not externally terminate a blocked worker, and a suspended host cannot execute a stop instruction until it resumes. A recorded attempt therefore still needs a reviewed external supervisor, suspension-aware rejection/stop policy, whole-attempt process accounting, an exclusive attempt directory and durable failure preservation. The recorded wrapper and its stop/persistence controls are pending. Source freeze, source-bound Test registration and the actual pre-execution methods/graph/source checkpoint are also pending.

D-0014 accepts the checked implementation and this disclosed software preflight as preparation. `SOURCE_FREEZE_PROPOSAL.json` identifies the candidate source and exact receipts but keeps all execution/freeze/checkpoint gates false. The initial entry plan stays unchanged. No Cycle obligation resolves, and no scientific graph support edge or baseline amendment is introduced.
