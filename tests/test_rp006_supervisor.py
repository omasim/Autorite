import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('rp006_recorded_attempt', ROOT / 'research/RP006/recorded_attempt.py')
attempt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(attempt)


class Clock:
    name = 'test-clock'

    def __init__(self, values):
        self.values = iter(values)

    def sample(self):
        return next(self.values)


def sample(continuous, monotonic, civil):
    return {'continuous_ns': continuous, 'monotonic_ns': monotonic, 'civil_ns': civil}


class RP006SupervisorControls(unittest.TestCase):
    def supervisor(self, values, parent_peak=100, child_peak=200):
        value = attempt.Supervisor.__new__(attempt.Supervisor)
        value.clock = Clock(values)
        value.start = values[0]
        value.previous = values[0]
        value.parent_peak = parent_peak
        value.child_peak = 0
        return value

    def test_suspension_aware_clock_gap_stops(self):
        supervisor = self.supervisor([sample(0, 0, 0), sample(4_000_000_000, 0, 4_000_000_000)])
        with patch.object(attempt, 'peak_rss_bytes', return_value=100):
            with self.assertRaisesRegex(RuntimeError, 'suspension'):
                supervisor.check(200)

    def test_continuous_deadline_stops_even_if_monotonic_did_not_advance(self):
        supervisor = self.supervisor([sample(0, 0, 0), sample(61_000_000_000, 61_000_000_000, 61_000_000_000)])
        with patch.object(attempt, 'peak_rss_bytes', return_value=100):
            with self.assertRaisesRegex(RuntimeError, 'deadline'):
                supervisor.check(200)

    def test_wall_clock_regression_stops(self):
        supervisor = self.supervisor([sample(2, 2, 2), sample(3, 3, 1)])
        with patch.object(attempt, 'peak_rss_bytes', return_value=100):
            with self.assertRaisesRegex(RuntimeError, 'regressed'):
                supervisor.check(200)

    def test_clock_gap_from_civil_adjustment_stops(self):
        supervisor = self.supervisor([sample(0, 0, 0), sample(1_000_000_000, 1_000_000_000, 5_000_000_000)])
        with patch.object(attempt, 'peak_rss_bytes', return_value=100):
            with self.assertRaisesRegex(RuntimeError, 'Civil/monotonic'):
                supervisor.check(200)

    def test_summed_process_lifetime_rss_is_bounded(self):
        supervisor = self.supervisor([sample(0, 0, 0), sample(1, 1, 1)])
        with patch.object(attempt, 'peak_rss_bytes', return_value=80_000_000):
            with self.assertRaisesRegex(RuntimeError, 'process-tree RSS'):
                supervisor.check(60_000_000)

    def test_authorization_failure_precedes_any_attempt_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            attempts = root / 'attempts'
            with patch.multiple(attempt, FREEZE=root / 'missing-freeze.json',
                                AUTHORIZATION=root / 'missing-auth.json', TEST_RECORD=root / 'missing-test.md',
                                ATTEMPTS=attempts):
                with self.assertRaisesRegex(PermissionError, 'pending'):
                    attempt.run_attempt()
            self.assertFalse(attempts.exists())

    def test_freeze_inventory_covers_runtime_and_replay_sources(self):
        self.assertIn('research/RP004/lineage.py', attempt.REQUIRED_INPUTS)
        self.assertIn('research/RP004/replay.py', attempt.REQUIRED_INPUTS)
        self.assertIn('research/RP006/recorded_worker.py', attempt.REQUIRED_INPUTS)
        self.assertIn('tests/test_rp006_supervisor.py', attempt.REQUIRED_INPUTS)
        self.assertIn('scripts/check-rp006-supervisor.py', attempt.REQUIRED_INPUTS)

    def test_atomic_failure_record_is_exclusive_and_durable(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'manifest.json'
            attempt.atomic_json(path, {'status': 'INCOMPLETE'})
            self.assertEqual(path.read_text(), '{\n  "status": "INCOMPLETE"\n}\n')
            self.assertFalse(path.with_name(path.name + '.partial').exists())

    def test_worker_cannot_open_network_or_spawn_children(self):
        worker_spec = importlib.util.spec_from_file_location('rp006_recorded_worker', ROOT / 'research/RP006/recorded_worker.py')
        worker = importlib.util.module_from_spec(worker_spec)
        worker_spec.loader.exec_module(worker)
        for event in ('socket.__new__', 'subprocess.Popen', 'os.fork'):
            with self.subTest(event=event), self.assertRaisesRegex(PermissionError, 'prohibits network'):
                worker.no_network_or_children(event, ())


if __name__ == '__main__':
    unittest.main()
