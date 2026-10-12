# RP006 recorded-attempt supervisor review

Date: 2026-10-12. Engineering review only. RP006 remains PLANNED, Cycle 02 remains OPEN at 0/9, and this review authorizes no recorded attempt.

## Why the runtime profile changes

The entry proposal measured the small preflight as one process. A recorded attempt needs a separate parent supervisor so a worker cannot continue past a suspension or deadline while waiting for a cooperative in-process check. The versioned recorded profile is `processes: 2`: one supervisor and one computation worker. The worker is prohibited from opening sockets or starting descendants. Its guard is a synchronous lease: each request blocks until the parent checks clocks and resource limits and replies. On wake from host sleep, the worker remains blocked until the parent checks the suspend-aware clock; the parent then revokes the lease and terminates it if the continuous and ordinary monotonic clocks diverge by more than two seconds.

This is a scoped engineering revision to the proposed process count, reviewed before any output. It does not change the six known cases, query families, masks, side information, or interpretation boundary. The preserved entry plan still says `processes: 1`; a later execution freeze must bind this separate reviewed profile at `processes: 2`. No historic entry file or preflight receipt is rewritten.

## Supervisor and persistence contract

`recorded_attempt.py` checks an accepted execution freeze, source hashes, a registered RP006 Test, an ACTIVE checkpoint Decision and a matching one-attempt authorization before creating an attempt directory. Those gate files do not exist yet, so invocation currently stops before creating an attempt. Each accepted authorization supplies a canonical UUID. A lock created with exclusive file creation prevents concurrent attempts; an existing run UUID, lock, or incomplete prior directory cannot be overwritten. A later correction needs a new reviewed source freeze and authorization.

The supervisor records an `INCOMPLETE` manifest and fsyncs it before launching the worker. The worker writes its intermediate bundle atomically. The parent then independently replays it and writes the full required output set with exact hashes. `COMPLETE` is written last. Exceptions keep their traceback and any partial outputs beside an `INCOMPLETE` manifest. If the host kills the parent before its failure handler runs, the fsynced manifest and stale lock remain; recovery is manual and requires a new review. The runner never chooses an earlier partial result or retries automatically.

The 60-second clock starts immediately before worker launch and covers worker import/computation/serialization, independent replay and final output persistence. Each parent guard checks civil, monotonic and suspend-aware elapsed time. Darwin uses `mach_continuous_time`; Linux uses `CLOCK_BOOTTIME`. A wall-clock regression, a civil/monotonic discrepancy above two seconds, a suspend gap above two seconds, an unsupported clock, a deadline breach or an RSS breach stops the attempt. The whole-process-tree bound is conservative: supervisor and worker lifetime `ru_maxrss` peaks are summed, using bytes on Darwin and KiB converted to bytes on Linux. The worker may not spawn a child, so this covers the only two processes. Unsupported systems fail closed.

The parent-worker lease is stronger than a periodic parent poll: a suspended worker cannot resume the computation until the supervising process acknowledges its next guard request. Between acknowledgments, the worker performs only the bounded pure operation already in progress. The protocol and stop path still need review against the actual frozen host/runtime before a Test is registered.

## Control coverage and limits

Nine focused controls cover suspend gaps, continuous deadlines, wall-clock rollback, civil-clock adjustment, conservative process-tree RSS, authorization failure before directory creation, frozen dependency coverage, exclusive durable JSON writes, and worker attempts to use sockets or spawn children. The existing 24 RP006 truth, projection, replay and certificate controls remain separate. CI runs the controls; this document does not claim a recorded research run.

The software guard cannot make the host execute its parent during sleep. It instead holds the worker at a blocking lease and detects the elapsed sleep as soon as the parent resumes. `ru_maxrss` is a process lifetime high-water measurement; summing the two peaks is an upper bound, not a simultaneous-memory trace. No result may rely on a threshold exceedance that the sampled high-water value could not observe. The run remains gated until the freeze includes these exact files, the Test fixes the input set, and the actual pre-execution Decision accepts the host, source, graph and stop behavior.

The clock contract follows [Apple's `mach_continuous_time` documentation](https://developer.apple.com/documentation/kernel/1646199-mach_continuous_time), [Python 3.12 clock documentation](https://docs.python.org/3.12/library/time.html), [Python 3.12 resource documentation](https://docs.python.org/3.12/library/resource.html), and the [Linux `clock_gettime(3)` manual](https://www.man7.org/linux/man-pages/man3/clock_gettime.3.html). These references establish clock semantics and the reported high-water field; they do not independently validate this implementation.

## Decision and remaining gates

D-0015 accepts the parent-worker supervisor as a preparation artifact and the two-process resource profile as a reviewed pre-outcome scope adjustment. It keeps source freeze, Test registration, actual checkpoint and execution authorization false. Known-domain outputs remain preparation observations; no Result or Cycle obligation is added.
