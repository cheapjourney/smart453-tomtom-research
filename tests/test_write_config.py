"""End-to-end tests for tools/write_config.py against a mock ECU.

Each test starts the mock, bridges it to a PTY with socat — the same shape as a
real serial link — and runs the writer as a subprocess. No vehicle, no adapter.

Asserted for every scenario: the exit code, that at most ONE write frame reached
the mock, that at most one session frame was sent, and that no other session or
reset command was ever emitted.

Needs socat and pyserial. Run from the repository root:

    python -m unittest discover -s tests -v
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tests"))

from mock_ecu import MockEcu  # noqa: E402

TOOL = ROOT / "tools" / "write_config.py"
PY = sys.executable


class Harness:
    def __init__(self, behavior: str, gate_enabled: bool = True):
        self.behavior = behavior
        self.mock = MockEcu(behavior).start()
        tmp = Path(tempfile.gettempdir())
        self.pty = tmp / f"mock_{behavior}_{os.getpid()}"
        self.gate = tmp / f"gate_{behavior}_{os.getpid()}.json"
        self.log = tmp / f"log_{behavior}_{os.getpid()}.jsonl"
        self.gate.write_text(json.dumps({"enabled": gate_enabled}))
        self.socat = subprocess.Popen(
            ["socat", f"PTY,link={self.pty},raw,echo=0",
             f"TCP:127.0.0.1:{self.mock.port}"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(100):
            if self.pty.exists():
                break
            time.sleep(0.05)

    def run(self, *extra: str, session: bool = False) -> subprocess.CompletedProcess:
        cmd = [PY, str(TOOL), "--port", str(self.pty), "--gate", str(self.gate),
               "--log", str(self.log), "--arm",
               "--expect-current", "38", "--confirm-target", "78",
               "--min-voltage", "12.2"]
        if session:
            cmd.append("--session-after-sales")
        return subprocess.run(cmd + list(extra), capture_output=True, text=True, timeout=60)

    def close(self):
        try:
            self.socat.terminate()
            self.socat.wait(timeout=5)
        except Exception:
            pass
        self.mock.stop()
        for p in (self.pty, self.gate, self.log):
            try:
                p.unlink()
            except OSError:
                pass


class WriteToolTest(unittest.TestCase):
    def scenario(self, behavior, expected_code, session=False, extra=()):
        h = Harness(behavior)
        try:
            res = h.run(*extra, session=session)
            writes, sessions = h.mock.writes, list(h.mock.sessions)
        finally:
            h.close()
        self.assertEqual(res.returncode, expected_code,
                         f"{behavior}: exit {res.returncode}, stderr={res.stderr.strip()}")
        self.assertLessEqual(writes, 1, f"{behavior}: {writes} write frames")
        self.assertLessEqual(len(sessions), 1, f"{behavior}: {sessions}")
        bad = [c for c in h.mock.commands
               if (c.startswith("10") and c != "10C0") or c.startswith("11")]
        self.assertEqual(bad, [], f"{behavior}: other session/reset sent: {bad}")
        return res, writes

    # happy path ---------------------------------------------------------
    def test_positive(self):
        res, writes = self.scenario("positive", 0)
        self.assertEqual(writes, 1)
        self.assertIn("0x78", res.stdout)

    def test_second_run_refused(self):
        h = Harness("positive")
        try:
            first = h.run()
            second = h.run()
            writes = h.mock.writes
        finally:
            h.close()
        self.assertEqual(first.returncode, 0)
        self.assertEqual(second.returncode, 3, "second run must refuse: value is 0x78")
        self.assertEqual(writes, 1)

    # refusals before any frame -----------------------------------------
    def test_wrong_identity(self):
        _, writes = self.scenario("wrong_identity", 2)
        self.assertEqual(writes, 0)

    def test_current_not_expected(self):
        _, writes = self.scenario("current_3a", 3)
        self.assertEqual(writes, 0)

    def test_low_voltage(self):
        _, writes = self.scenario("low_voltage", 4)
        self.assertEqual(writes, 0)

    def test_no_answer_identity(self):
        _, writes = self.scenario("no_answer_identity", 7)
        self.assertEqual(writes, 0)

    # negative answers ---------------------------------------------------
    def test_write_rejected_22(self):
        res, writes = self.scenario("nrc", 6)
        self.assertEqual(writes, 1)
        self.assertIn("NRC 0x22", res.stderr)

    def test_write_rejected_12(self):
        res, writes = self.scenario("nrc_12", 6)
        self.assertEqual(writes, 1)
        self.assertIn("NRC 0x12", res.stderr)

    def test_write_rejected_7f_without_session(self):
        res, writes = self.scenario("session_ok_write_7f", 6)
        self.assertEqual(writes, 1)
        self.assertIn("NRC 0x7F", res.stderr)

    # transport failures -------------------------------------------------
    def test_no_answer_after_write(self):
        _, writes = self.scenario("no_answer_readback", 7)
        self.assertEqual(writes, 1)

    def test_disconnect_after_write(self):
        _, writes = self.scenario("disconnect_after_write", 9)
        self.assertEqual(writes, 1)

    def test_readback_mismatch(self):
        _, writes = self.scenario("readback_mismatch", 8)
        self.assertEqual(writes, 1)

    # after-sales session ------------------------------------------------
    def test_session_confirmed(self):
        res, writes = self.scenario("session_ok", 0, session=True)
        self.assertEqual(writes, 1)
        self.assertIn("50 C0", res.stdout)

    def test_exact_bytes_on_the_wire(self):
        """What actually reached the ECU: one 10C0, then one 2E6C1C78."""
        h = Harness("session_ok")
        try:
            h.run(session=True)
            cmds = list(h.mock.commands)
        finally:
            h.close()
        uut = [c for c in cmds if c.startswith(("10", "2E", "11", "27", "14"))]
        self.assertEqual(uut, ["10C0", "2E6C1C78"])
        self.assertLessEqual(len([c for c in cmds if c.startswith("10")]), 1)

    def test_session_silent_is_unconfirmed(self):
        res, writes = self.scenario("positive", 0, session=True)
        self.assertEqual(writes, 1)
        self.assertIn("UNCONFIRMED", res.stdout)

    def test_session_nrc_aborts(self):
        res, writes = self.scenario("session_nrc", 6, session=True)
        self.assertEqual(writes, 0)
        self.assertIn("NRC 0x22", res.stderr)

    def test_session_wrong_answer_aborts(self):
        _, writes = self.scenario("session_wrong", 9, session=True)
        self.assertEqual(writes, 0)

    def test_session_then_write_7f(self):
        res, writes = self.scenario("session_ok_write_7f", 6, session=True)
        self.assertEqual(writes, 1)
        self.assertIn("NRC 0x7F", res.stderr)

    # gates --------------------------------------------------------------
    def test_gate_closed(self):
        h = Harness("positive", gate_enabled=False)
        try:
            res = h.run()
            writes = h.mock.writes
        finally:
            h.close()
        self.assertEqual(res.returncode, 5)
        self.assertEqual(writes, 0)

    def test_target_must_be_current_or_bit(self):
        h = Harness("positive")
        try:
            res = h.run("--confirm-target", "3E")
            writes = h.mock.writes
        finally:
            h.close()
        self.assertEqual(res.returncode, 5)
        self.assertEqual(writes, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
