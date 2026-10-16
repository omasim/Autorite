"""Answer-free controls for a process-group execution guard.

This test launches only tiny synthetic workers under /private/tmp. It does not
read candidate inputs, calculate lineage answers, or create research evidence.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time


MAX_CLOCK_GAP_SECONDS = 2.0
TERMINATION_GRACE_SECONDS = 0.25
POLL_SECONDS = 0.02
MAX_CAPTURED_LOG_BYTES = 64 * 1024


class GuardStop(RuntimeError):
    pass


class BoundedCapture:
    """Drain a worker pipe continuously while retaining only a bounded prefix."""
    def __init__(self, stream, limit: int = MAX_CAPTURED_LOG_BYTES):
        self.stream = stream
        self.limit = limit
        self.parts: list[bytes] = []
        self.size = 0
        self.overflow = threading.Event()
        self.finished = threading.Event()
        self.thread = threading.Thread(target=self._drain, daemon=True)
        self.thread.start()

    def _drain(self) -> None:
        try:
            while True:
                chunk = self.stream.read(8192)
                if not chunk:
                    return
                remaining = self.limit - self.size
                if remaining > 0:
                    kept = chunk[:remaining]
                    self.parts.append(kept)
                    self.size += len(kept)
                if len(chunk) > max(remaining, 0):
                    self.overflow.set()
        finally:
            self.finished.set()

    def text(self) -> str:
        return b"".join(self.parts).decode("utf-8", "replace")


def clock_failure(start_wall: float, start_mono: float,
                  now_wall: float, now_mono: float,
                  max_gap: float = MAX_CLOCK_GAP_SECONDS) -> str | None:
    wall_elapsed = now_wall - start_wall
    mono_elapsed = now_mono - start_mono
    if wall_elapsed < 0 or mono_elapsed < 0:
        return "clock_regression"
    if abs(wall_elapsed - mono_elapsed) > max_gap:
        return "clock_gap"
    return None


def _signal_group(pgid: int, sig: int) -> None:
    try:
        os.killpg(pgid, sig)
    except ProcessLookupError:
        pass


def stop_and_reap(proc: subprocess.Popen[bytes], grace: float = TERMINATION_GRACE_SECONDS) -> None:
    """Stop every process in the isolated worker group, then reap its leader."""
    pgid = proc.pid  # start_new_session makes the leader its process-group ID.
    _signal_group(pgid, signal.SIGTERM)
    deadline = time.monotonic() + grace
    while proc.poll() is None and time.monotonic() < deadline:
        time.sleep(min(POLL_SECONDS, max(0.0, deadline - time.monotonic())))
    # Also kill descendants if the group leader exited on SIGTERM first.
    _signal_group(pgid, signal.SIGKILL)
    try:
        proc.wait(timeout=2)
    except subprocess.TimeoutExpired:
        _signal_group(pgid, signal.SIGKILL)
        proc.wait(timeout=2)


def supervise(argv: list[str], *, timeout_seconds: float,
              wall_clock=time.time, mono_clock=time.monotonic) -> dict[str, object]:
    start_wall, start_mono = wall_clock(), mono_clock()
    proc = subprocess.Popen(argv, start_new_session=True,
                            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, close_fds=True)
    stdout_capture = BoundedCapture(proc.stdout)
    stderr_capture = BoundedCapture(proc.stderr)
    reason = None
    try:
        while proc.poll() is None:
            if stdout_capture.overflow.is_set():
                reason = "stdout_log_byte_cap"
                raise GuardStop(reason)
            if stderr_capture.overflow.is_set():
                reason = "stderr_log_byte_cap"
                raise GuardStop(reason)
            now_wall, now_mono = wall_clock(), mono_clock()
            reason = clock_failure(start_wall, start_mono, now_wall, now_mono)
            if reason:
                raise GuardStop(reason)
            if now_wall - start_wall >= timeout_seconds or now_mono - start_mono >= timeout_seconds:
                reason = "deadline"
                raise GuardStop(reason)
            time.sleep(POLL_SECONDS)
        proc.wait(timeout=1)
        stdout_capture.thread.join(timeout=1)
        stderr_capture.thread.join(timeout=1)
        if stdout_capture.thread.is_alive() or stderr_capture.thread.is_alive():
            reason = "worker_pipe_not_closed"
            raise GuardStop(reason)
        if stdout_capture.overflow.is_set():
            reason = "stdout_log_byte_cap"
        elif stderr_capture.overflow.is_set():
            reason = "stderr_log_byte_cap"
        if proc.returncode != 0:
            reason = reason or f"worker_exit_{proc.returncode}"
        return {"status": "COMPLETE" if reason is None else "INCOMPLETE",
                "returncode": proc.returncode, "reason": reason,
                "stdout": stdout_capture.text(),
                "stderr": stderr_capture.text()}
    except BaseException as exc:
        if reason is None:
            reason = type(exc).__name__
        stop_and_reap(proc)
        stdout_capture.thread.join(timeout=1)
        stderr_capture.thread.join(timeout=1)
        return {"status": "INCOMPLETE", "returncode": proc.returncode,
                "reason": reason, "stdout": stdout_capture.text(),
                "stderr": stderr_capture.text()}


def write_incomplete(directory: Path, reason: str) -> None:
    receipt = {"status": "INCOMPLETE", "failure": reason,
               "automatic_retry": False, "promotion": False}
    path = directory / "INCOMPLETE.json"
    with path.open("x", encoding="utf-8") as stream:
        json.dump(receipt, stream, sort_keys=True, separators=(",", ":"))
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def check_clock_controls() -> None:
    if clock_failure(10, 20, 15, 25) is not None:
        raise AssertionError("normal elapsed clocks should pass")
    if clock_failure(10, 20, 20, 25) != "clock_gap":
        raise AssertionError("forward civil/monotonic gap was not stopped")
    if clock_failure(10, 20, 9, 21) != "clock_regression":
        raise AssertionError("clock regression was not stopped")


def check_deadline_and_group_reap(root: Path) -> None:
    # Worker creates a grandchild in the inherited isolated group and then
    # blocks. The external deadline must stop the group and reap its leader.
    child_marker = root / "descendant-terminated"
    child_code = (
        "import pathlib,signal,sys,time; "
        "signal.signal(signal.SIGTERM,lambda *_:(pathlib.Path(sys.argv[1]).write_text('term'),sys.exit(0))); "
        "time.sleep(30)"
    )
    # Keep the source expression readable while passing no project data.
    worker_code = "import subprocess,sys,time; subprocess.Popen([sys.executable,'-c',sys.argv[1],sys.argv[2]]); time.sleep(30)"
    result = supervise([sys.executable, "-c", worker_code, child_code,
                        str(child_marker)], timeout_seconds=0.15)
    if result["status"] != "INCOMPLETE" or result["reason"] != "deadline":
        raise AssertionError(f"deadline control did not stop: {result}")
    if not isinstance(result["returncode"], int) or result["returncode"] >= 0:
        raise AssertionError(f"worker leader was not signal-terminated and reaped: {result}")
    if not child_marker.is_file() or child_marker.read_text() != "term":
        raise AssertionError("process-group stop did not reach the worker descendant")


def check_crash_partial_preservation(root: Path) -> None:
    partial = root / "synthetic.partial"
    code = "from pathlib import Path; Path(%r).write_text('partial synthetic bytes'); raise SystemExit(7)" % str(partial)
    result = supervise([sys.executable, "-c", code], timeout_seconds=2)
    if result["status"] != "INCOMPLETE" or result["reason"] != "worker_exit_7":
        raise AssertionError(f"crash control status wrong: {result}")
    if not partial.is_file() or partial.read_text() != "partial synthetic bytes":
        raise AssertionError("crash control did not preserve its partial artifact")
    write_incomplete(root, str(result["reason"]))
    receipt = json.loads((root / "INCOMPLETE.json").read_text())
    if receipt["status"] != "INCOMPLETE" or receipt["automatic_retry"] or receipt["promotion"]:
        raise AssertionError("crash receipt has unsafe retry/promotion fields")


def check_large_output_does_not_block() -> None:
    # Both streams exceed common pipe buffers. The guard must keep draining,
    # preserve a bounded diagnostic prefix, and stop on its log cap rather
    # than deadlocking until the wall-clock deadline.
    code = (
        "import os; block=b'x'*65536; "
        "[os.write(1,block) for _ in range(32)]; "
        "[os.write(2,block) for _ in range(32)]"
    )
    result = supervise([sys.executable, "-c", code], timeout_seconds=5)
    if result["status"] != "INCOMPLETE" or result["reason"] not in (
            "stdout_log_byte_cap", "stderr_log_byte_cap"):
        raise AssertionError(f"Large-output worker did not fail closed at log cap: {result}")
    if len(result["stdout"].encode()) > MAX_CAPTURED_LOG_BYTES or len(result["stderr"].encode()) > MAX_CAPTURED_LOG_BYTES:
        raise AssertionError("Large-output worker exceeded the bounded log capture")

    normal = "import os; os.write(1,b'o'*4096); os.write(2,b'e'*4096)"
    result = supervise([sys.executable, "-c", normal], timeout_seconds=5)
    if result["status"] != "COMPLETE" or len(result["stdout"]) != 4096 or len(result["stderr"]) != 4096:
        raise AssertionError(f"Bounded diagnostic capture failed: {result}")


def main() -> None:
    root_dir = Path("/private/tmp")
    if shutil.disk_usage(root_dir).free < 2 * 1024**3:
        raise RuntimeError("Need at least 2 GiB free for the synthetic guard controls")
    check_clock_controls()
    check_large_output_does_not_block()
    with tempfile.TemporaryDirectory(prefix="finite-lineage-guard-", dir=root_dir) as tmp:
        root = Path(tmp)
        check_deadline_and_group_reap(root)
        check_crash_partial_preservation(root)
    print(json.dumps({
        "status": "PASS",
        "purpose": "ANSWER_FREE_SYNTHETIC_EXECUTION_GUARD_CONTROLS",
        "candidate_inputs_read": False,
        "candidate_answers_generated": False,
        "controls": ["clock_gap", "clock_regression", "dual_clock_deadline",
                     "process_group_stop", "leader_reap", "partial_preserved",
                     "INCOMPLETE_receipt", "continuous_stdout_stderr_drain",
                     "bounded_log_capture", "log_cap_fail_closed",
                     "no_automatic_retry_or_promotion"],
        "temporary_artifacts_removed": True,
        "python": sys.version.split()[0],
        "platform": sys.platform,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
