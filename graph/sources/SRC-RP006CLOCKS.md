---
schema_version: '0.1'
id: SRC-RP006CLOCKS
type: Source
title: Suspend-aware clocks and process resource measurements
created_at: '2026-10-12'
updated_at: '2026-10-12'
source_refs: []
relations: []
citation: Apple Developer Documentation, `mach_continuous_time`; Python 3.12 documentation, `time` and `resource` modules; Linux man-pages, `clock_gettime(3)`.
url: https://developer.apple.com/documentation/kernel/1646199-mach_continuous_time
---

Official platform and Python references used for the engineering supervisor review: Apple documents that `mach_continuous_time` advances while the system sleeps; Python documents Linux `CLOCK_BOOTTIME` as including suspend and `resource.getrusage`'s `ru_maxrss` high-water field. The citations inform clock and measurement semantics only; they do not review or validate RP006's implementation.
