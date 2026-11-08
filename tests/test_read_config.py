"""End-to-end tests for tools/read_config.py against a mock ECU.

Same harness shape as the writer tests: a mock head unit, bridged to a PTY with
socat, and the tool run as a subprocess. No vehicle, no adapter.

The regression this file exists for: `--json logs/before.json` must work on a
fresh clone, where `logs/` does not exist yet because it is git-ignored.
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

TOOL = ROOT / "tools" / "read_config.py"
PY = sys.executable


class Harness:
    def __init__(self, behavior: str = "positive"):
        self.mock = MockEcu(behavior).start()
        self.tmp = Path(tempfile.mkdtemp(prefix="readcfg_"))
        self.pty = self.tmp / "serial"
        self.socat = subprocess.Popen(
            ["socat", f"PTY,link={self.pty},raw,echo=0",
             f"TCP:127.0.0.1:{self.mock.port}"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(100):
            if self.pty.exists():
                break
            time.sleep(0.05)

    def run(self, *extra: str) -> subprocess.CompletedProcess:
        return subprocess.run([PY, str(TOOL), "--port", str(self.pty), *extra],
                              capture_output=True, text=True, timeout=60)

    def close(self):
        try:
            self.socat.terminate()
            self.socat.wait(timeout=5)
        except Exception:
            pass
        self.mock.stop()
        try:
            self.pty.unlink()
        except OSError:
            pass


class ReadConfigTest(unittest.TestCase):
    def test_reads_identity_and_config(self):
        h = Harness()
        try:
            res = h.run()
        finally:
            h.close()
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn("259156244R", res.stdout)
        self.assertIn("0x38", res.stdout)
        self.assertIn("NOT PRESENT", res.stdout)     # Android Auto
        self.assertIn("PRESENT", res.stdout)         # MirrorLink

    def test_part_number_mismatch_exits_4(self):
        h = Harness()
        try:
            res = h.run("--expect-part", "999999999R")
        finally:
            h.close()
        self.assertEqual(res.returncode, 4)

    def test_json_creates_missing_parent_directory(self):
        """Regression: --json logs/before.json on a fresh clone (no logs/ dir)."""
        h = Harness()
        target = h.tmp / "logs" / "before.json"
        self.assertFalse(target.parent.exists(), "precondition: no logs/ directory")
        try:
            res = h.run("--json", str(target))
        finally:
            h.close()
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertTrue(target.is_file(), "the tool must create the parent directory")

        data = json.loads(target.read_text())
        self.assertEqual(data["identity"]["result"], "POSITIVE")
        self.assertIn("259156244", data["identity"]["ascii"])
        self.assertEqual(data["config"]["decoded"]["raw_byte"], "38")
        self.assertFalse(data["config"]["decoded"]["android_auto"])
        self.assertTrue(data["config"]["decoded"]["mirrorlink"])

    def test_json_with_existing_directory_still_works(self):
        h = Harness()
        target = h.tmp / "reports" / "out.json"
        target.parent.mkdir()
        try:
            res = h.run("--json", str(target))
        finally:
            h.close()
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertTrue(target.is_file())


if __name__ == "__main__":
    unittest.main(verbosity=2)
