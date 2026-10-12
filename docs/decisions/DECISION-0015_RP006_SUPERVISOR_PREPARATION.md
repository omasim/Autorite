# Decision D-0015 — RP006 recorded-attempt supervisor preparation

Date: 2026-10-12. Status: ACTIVE.

Accept the fail-closed parent-worker supervisor and the reviewed two-process attempt profile as engineering preparation. The supervisor waits for the worker at each computation guard, checks a suspend-aware deadline and a conservative whole-process memory bound, and preserves an incomplete attempt on failure. It refuses to start until a later execution freeze, registered Test and actual pre-execution Decision are accepted.

The entry blueprint proposed one process for the known-domain preflight. The separately reviewed execution profile uses two processes so the parent can revoke a worker lease after a host suspension. This adjustment is recorded before outcomes. The six known constructions, exact families, masks and side information do not change.

RP006 stays PLANNED. Cycle 02 stays OPEN at 0/9. No Test, Result, scientific support edge, source freeze or run authorization is created. D-0015 is an engineering preparation Decision, not the actual pre-execution checkpoint.
