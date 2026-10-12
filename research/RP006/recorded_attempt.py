"""Fail-closed parent supervisor for a future, separately authorized RP006 run.

This module cannot create an attempt until a reviewed execution freeze, registered
Test, and accepted checkpoint authorization exist. It is deliberately separate
from the preserved known-domain engineering preflight.
"""
import argparse
import ctypes
import ctypes.util
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import resource
import select
import subprocess
import sys
import time
import traceback
import uuid

ROOT = Path(__file__).resolve().parents[2]
FREEZE = ROOT / 'research/RP006/EXECUTION_FREEZE.json'
AUTHORIZATION = ROOT / 'research/RP006/EXECUTION_AUTHORIZATION.json'
TEST_RECORD = ROOT / 'research/RP006/audit-001/RECORD.md'
ATTEMPTS = ROOT / 'research/RP006/attempts'
WORKER = ROOT / 'research/RP006/recorded_worker.py'
LIMIT_SECONDS = 60
LIMIT_RSS = 134217728
CLOCK_GAP_SECONDS = 2
REQUIRED_INPUTS = {
    'research/RP006/producer.py', 'research/RP006/verifier.py',
    'research/RP006/recorded_attempt.py', 'research/RP006/recorded_worker.py',
    'research/RP004/lineage.py', 'research/RP004/replay.py',
    'research/RP004/RP004_FIXTURES.json',
    'research/RP006/DOMAIN.json', 'research/RP006/ENTRY_PLAN.json',
    'research/RP006/RP006_OPERATIONAL_PROTOCOL.md',
    'research/RP006/RP006_PRIOR_ART_REVIEW.md',
    'research/RP006/RP006_EXECUTION_SUPERVISOR_REVIEW.md',
    'research/RP006/RP006_PREEXECUTION_REVIEW.md',
    'research/RP006/resources.py',
    'tests/test_rp006_implementation.py', 'tests/test_rp006_supervisor.py',
    'scripts/check-rp006-supervisor.py',
}


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def atomic_json(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + '.partial')
    payload = (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    except BaseException:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass
        raise


class SuspendAwareClock:
    """Continuous elapsed clock paired with a suspend-excluding monotonic clock."""
    def __init__(self):
        self.name = None
        self._continuous = None
        if sys.platform == 'darwin':
            library = ctypes.CDLL(ctypes.util.find_library('System') or None)
            class Timebase(ctypes.Structure):
                _fields_ = [('numer', ctypes.c_uint32), ('denom', ctypes.c_uint32)]
            info = Timebase()
            if library.mach_timebase_info(ctypes.byref(info)) != 0 or not info.denom:
                raise RuntimeError('Cannot establish Darwin continuous clock units')
            function = library.mach_continuous_time
            function.restype = ctypes.c_uint64
            self._continuous = lambda: int(function()) * info.numer // info.denom
            self.name = 'mach_continuous_time'
        elif sys.platform.startswith('linux') and hasattr(time, 'CLOCK_BOOTTIME'):
            self._continuous = lambda: time.clock_gettime_ns(time.CLOCK_BOOTTIME)
            self.name = 'CLOCK_BOOTTIME'
        else:
            raise RuntimeError('No reviewed suspend-aware clock for this platform')

    def sample(self):
        return {'continuous_ns': self._continuous(),
                'monotonic_ns': time.monotonic_ns(),
                'civil_ns': time.time_ns()}


def peak_rss_bytes():
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if sys.platform == 'darwin':
        return int(value)
    if sys.platform.startswith('linux'):
        return int(value * 1024)
    raise RuntimeError('Unsupported RSS unit contract')


def current_commit():
    return subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()


def load_record(path):
    text = Path(path).read_text()
    parts = text.split('---', 2)
    if len(parts) != 3 or parts[0].strip():
        raise ValueError('Malformed graph record: ' + str(path))
    fields = {}
    for key in ('id', 'type', 'status', 'package_ref'):
        match = re.search(r'^' + key + r':\s*([^\n]+)$', parts[1], re.MULTILINE)
        if match:
            fields[key] = match.group(1).strip().strip('"\'')
    return fields, parts[2].strip()


def authorize():
    """Check future gates; current RP006 has none, so this fails closed today."""
    if not (FREEZE.is_file() and AUTHORIZATION.is_file() and TEST_RECORD.is_file()):
        raise PermissionError('Execution freeze, registered Test and accepted checkpoint authorization are pending')
    freeze = json.loads(FREEZE.read_text())
    authorization = json.loads(AUTHORIZATION.read_text())
    test, test_body = load_record(TEST_RECORD)
    head = current_commit()
    required = {'schema_version', 'status', 'source_commit', 'input_sha256', 'test_ref', 'checkpoint_decision_ref'}
    if set(freeze) != required or freeze['schema_version'] != '0.1' or freeze['status'] != 'ACCEPTED':
        raise PermissionError('Execution freeze is not accepted or has unexpected fields')
    if not isinstance(freeze['input_sha256'], dict) or not freeze['input_sha256']:
        raise PermissionError('Execution freeze has no source inventory')
    if not isinstance(freeze['source_commit'], str) or not re.fullmatch(r'[0-9a-f]{40}', freeze['source_commit']):
        raise PermissionError('Malformed source commit in execution freeze')
    if not REQUIRED_INPUTS.issubset(freeze['input_sha256']):
        raise PermissionError('Execution freeze omits a required source or control')
    if freeze['source_commit'] not in subprocess.check_output(
            ['git', 'rev-list', head], cwd=ROOT, text=True).splitlines():
        raise PermissionError('Frozen source is not an ancestor of the authorized checkout')
    for name, checksum in freeze['input_sha256'].items():
        relative = Path(name)
        path = (ROOT / relative).resolve()
        if relative.is_absolute() or '..' in relative.parts or not path.is_relative_to(ROOT) or not path.is_file():
            raise PermissionError('Unsafe or missing frozen source path')
        if not re.fullmatch(r'[0-9a-f]{64}', checksum):
            raise PermissionError('Malformed source hash in execution freeze')
        committed = subprocess.check_output(['git', 'show', freeze['source_commit'] + ':' + name], cwd=ROOT)
        current = (ROOT / name).read_bytes()
        if sha256(committed) != checksum or sha256(current) != checksum:
            raise PermissionError('Execution source differs from the reviewed freeze: ' + name)
    if test.get('id') != freeze['test_ref'] or test.get('type') != 'Test' or test.get('package_ref') != 'RP-006':
        raise PermissionError('Frozen Test registration does not match')
    decision_path = ROOT / 'graph/decisions' / (freeze['checkpoint_decision_ref'] + '.md')
    if not re.fullmatch(r'D-[A-Z0-9]+', freeze['checkpoint_decision_ref']) or not decision_path.is_file():
        raise PermissionError('Accepted pre-execution checkpoint Decision is missing')
    decision, decision_body = load_record(decision_path)
    if decision.get('id') != freeze['checkpoint_decision_ref'] or decision.get('type') != 'Decision' or decision.get('status') != 'ACTIVE':
        raise PermissionError('Actual pre-execution checkpoint is not accepted')
    if freeze['test_ref'] not in test_body or freeze['checkpoint_decision_ref'] not in decision_body:
        raise PermissionError('Test/checkpoint cross-reference missing from its record body')
    auth_fields = {'attempt_id', 'status', 'execution_authorized', 'source_commit', 'test_ref', 'checkpoint_decision_ref'}
    if not isinstance(authorization, dict):
        raise PermissionError('Malformed execution authorization')
    try:
        if str(uuid.UUID(authorization.get('attempt_id', ''))) != authorization['attempt_id']:
            raise ValueError('Noncanonical UUID')
    except (ValueError, AttributeError, TypeError):
        raise PermissionError('Authorization must bind one unique attempt UUID')
    if set(authorization) != auth_fields or authorization != {
            'attempt_id': authorization['attempt_id'],
            'status': 'ACCEPTED', 'execution_authorized': True,
            'source_commit': freeze['source_commit'], 'test_ref': freeze['test_ref'],
            'checkpoint_decision_ref': freeze['checkpoint_decision_ref']}:
        raise PermissionError('Execution authorization does not match the accepted freeze')
    return {'attempt_id': authorization['attempt_id'], 'source_commit': freeze['source_commit'], 'source_freeze_sha256': sha256(FREEZE.read_bytes()),
            'authorization_sha256': sha256(AUTHORIZATION.read_bytes()), 'test_ref': freeze['test_ref'],
            'checkpoint_decision_ref': freeze['checkpoint_decision_ref'], 'head': head}


class Supervisor:
    def __init__(self, child, clock=None):
        self.child = child
        self.clock = clock or SuspendAwareClock()
        self.start = self.clock.sample()
        self.previous = self.start
        self.parent_peak = peak_rss_bytes()
        self.child_peak = 0

    def check(self, reported_child_peak=None):
        now = self.clock.sample()
        if any(now[k] < self.previous[k] for k in now):
            raise RuntimeError('Clock regressed; preserve this attempt as INCOMPLETE')
        self.previous = now
        elapsed = (now['monotonic_ns'] - self.start['monotonic_ns']) / 1e9
        continuous = (now['continuous_ns'] - self.start['continuous_ns']) / 1e9
        civil = (now['civil_ns'] - self.start['civil_ns']) / 1e9
        if abs(continuous - elapsed) > CLOCK_GAP_SECONDS:
            raise RuntimeError('Host suspension or clock gap detected; stop attempt')
        if abs(civil - elapsed) > CLOCK_GAP_SECONDS:
            raise RuntimeError('Civil/monotonic clock discrepancy; stop attempt')
        if max(elapsed, continuous, civil) > LIMIT_SECONDS:
            raise RuntimeError('60-second whole-attempt deadline breached')
        if reported_child_peak is not None:
            self.child_peak = max(self.child_peak, int(reported_child_peak))
        self.parent_peak = max(self.parent_peak, peak_rss_bytes())
        # Sum of the supervisor and worker lifetime peaks is a conservative upper
        # bound for this two-process tree. The worker is prohibited from spawning.
        total_peak = self.parent_peak + self.child_peak
        if total_peak > LIMIT_RSS:
            raise RuntimeError('Conservative whole-process-tree RSS bound breached')
        return {'monotonic_seconds': elapsed, 'suspend_aware_seconds': continuous,
                'civil_elapsed_seconds': civil, 'parent_peak_rss_bytes': self.parent_peak,
                'worker_peak_rss_bytes': self.child_peak,
                'conservative_process_tree_peak_rss_bytes': total_peak,
                'clock': self.clock.name, 'clock_gap_seconds': continuous - elapsed}


def read_json_lines(stream):
    while True:
        ready, _, _ = select.select([stream], [], [], 0.01)
        if not ready:
            yield None
            continue
        line = stream.readline()
        if not line:
            return
        yield line.decode().strip()


def write_jsonl(path, rows):
    path = Path(path)
    temporary = path.with_name(path.name + '.partial')
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, 'w') as stream:
            for row in rows:
                stream.write(json.dumps(row, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    except BaseException:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass
        raise


def run_attempt():
    gate = authorize()
    supported_clock = SuspendAwareClock()
    peak_rss_bytes()  # Fail closed before recording an attempt on an unsupported host.
    ATTEMPTS.mkdir(mode=0o700, exist_ok=True)
    lock = ATTEMPTS / 'active.lock'
    lock_fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    run_id = gate['attempt_id']
    directory = ATTEMPTS / run_id
    try:
        directory.mkdir(mode=0o700, exist_ok=False)
        directory_fd = os.open(ATTEMPTS, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
        os.write(lock_fd, (run_id + '\n').encode())
        os.fsync(lock_fd)
        manifest = {'schema_version': '0.1', 'run_id': run_id, 'status': 'INCOMPLETE',
                    'started_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                    'authorization': gate, 'limits': {'seconds': LIMIT_SECONDS, 'rss_bytes': LIMIT_RSS,
                    'clock_gap_seconds': CLOCK_GAP_SECONDS}, 'outputs': {}, 'failure': None}
        atomic_json(directory / 'manifest.json', manifest)
        supervisor = Supervisor(None, supported_clock)
        process = None
        worker_peak = 0
        stderr = b''
        try:
            process = subprocess.Popen([sys.executable, '-I', str(WORKER), str(ROOT), str(directory)],
                                       cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE, bufsize=0)
            supervisor.child = process
            for line in read_json_lines(process.stdout):
                timing = supervisor.check(worker_peak)
                if line is None:
                    if process.poll() is not None:
                        break
                    continue
                if line.startswith('GUARD '):
                    try:
                        worker_peak = max(worker_peak, int(line.split(' ', 1)[1]))
                        timing = supervisor.check(worker_peak)
                        process.stdin.write(b'OK\n')
                        process.stdin.flush()
                    except BaseException as exc:
                        process.stdin.write(b'STOP\n')
                        process.stdin.flush()
                        raise exc
                else:
                    raise RuntimeError('Unexpected worker control message')
            if process.poll() is None:
                process.wait(timeout=0.1)
            stderr = process.stderr.read()
            if process.returncode != 0:
                raise RuntimeError('Worker failed: ' + stderr.decode(errors='replace')[-4000:])
            timing = supervisor.check(worker_peak)
            worker = json.loads((directory / 'worker.json').read_text())
            verifier_spec = importlib.util.spec_from_file_location('rp006_recorded_verifier', ROOT / 'research/RP006/verifier.py')
            verifier = importlib.util.module_from_spec(verifier_spec)
            verifier_spec.loader.exec_module(verifier)
            domain = json.loads((ROOT / 'research/RP006/DOMAIN.json').read_text())
            replay = verifier.verify(worker, domain, lambda: supervisor.check(worker_peak))
            files = {'truth.jsonl': worker['truth'], 'projections.jsonl': worker['projections'],
                     'pairs.jsonl': worker['pairs'], 'conflicts.jsonl': worker['conflicts']}
            for name, rows in files.items():
                write_jsonl(directory / name, rows)
            for name, value in [('certificates.json', worker['certificates']),
                                ('summary.json', worker['summary']), ('replay.json', replay)]:
                atomic_json(directory / name, value)
            timing = supervisor.check(worker_peak)
            timing.update(worker_resource_source='resource.getrusage(RUSAGE_SELF); Darwin bytes, Linux KiB',
                          measurement='Parent continuous-clock supervisor; worker blocks at every producer/verifier guard; summed process lifetime peaks are a conservative two-process RSS bound.')
            atomic_json(directory / 'timing.json', timing)
            manifest['status'] = 'COMPLETE'
            manifest['outputs'] = {p.name: sha256(p.read_bytes()) for p in sorted(directory.iterdir())
                                    if p.is_file() and p.name not in {'manifest.json', 'worker.json'}}
            manifest['completed_at'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            atomic_json(directory / 'manifest.json', manifest)
            timing = supervisor.check(worker_peak)
            (directory / 'worker.json').unlink()
            print(json.dumps({'run_id': run_id, 'status': 'COMPLETE', 'counts': worker['summary']}, sort_keys=True))
        except BaseException as exc:
            if process is not None and process.poll() is None:
                process.kill()
                process.wait()
            manifest['failure'] = {'type': type(exc).__name__, 'message': str(exc),
                                   'traceback': traceback.format_exc()[-8000:],
                                   'worker_stderr': process.stderr.read().decode(errors='replace')[-4000:] if process else ''}
            manifest['status'] = 'INCOMPLETE'
            atomic_json(directory / 'failure.json', manifest['failure'])
            manifest['outputs'] = {p.name: sha256(p.read_bytes()) for p in sorted(directory.iterdir())
                                   if p.is_file() and p.name != 'manifest.json'}
            atomic_json(directory / 'manifest.json', manifest)
            raise
    finally:
        os.close(lock_fd)
        # A process crash leaves the lock behind. Recovery is a reviewed action.
        # A later attempt needs a new UUID and separately accepted authorization.
        saved = locals().get('manifest')
        if saved and (directory / 'manifest.json').is_file():
            try:
                lock.unlink()
                root_fd = os.open(ATTEMPTS, os.O_RDONLY)
                try:
                    os.fsync(root_fd)
                finally:
                    os.close(root_fd)
            except FileNotFoundError:
                pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--recorded-attempt', action='store_true', required=True)
    parser.parse_args()
    run_attempt()
