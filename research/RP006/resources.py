"""Cooperative engineering preflight guard; external execution supervisor still pending."""
import resource
import sys
import time


def peak_rss_bytes():
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if sys.platform == 'darwin':
        return int(value)
    if sys.platform.startswith('linux'):
        return int(value * 1024)
    raise ValueError('RSS unit contract supports Darwin/Linux only')


class Guard:
    def __init__(self, seconds=60, memory_bytes=134217728, clock_gap=2,
                 monotonic=time.monotonic, civil=time.time, rss=peak_rss_bytes):
        self.monotonic, self.civil, self.rss = monotonic, civil, rss
        self.seconds, self.memory_bytes, self.clock_gap = seconds, memory_bytes, clock_gap
        self.start_mono, self.start_civil = monotonic(), civil()
        self.previous_mono, self.previous_civil = self.start_mono, self.start_civil

    def __call__(self):
        mono, civil = self.monotonic(), self.civil()
        if mono < self.previous_mono or civil < self.previous_civil:
            raise ValueError('Clock regression invalidates preflight')
        self.previous_mono, self.previous_civil = mono, civil
        elapsed, wall = mono - self.start_mono, civil - self.start_civil
        memory = self.rss()
        if max(elapsed, wall) > self.seconds:
            raise ValueError('Elapsed deadline breached')
        if abs(wall - elapsed) > self.clock_gap:
            raise ValueError('Civil/monotonic clock discrepancy')
        if memory > self.memory_bytes:
            raise ValueError('Peak process RSS breached')
        return {'monotonic_seconds': elapsed, 'civil_elapsed_seconds': wall, 'peak_process_rss_bytes': memory}
