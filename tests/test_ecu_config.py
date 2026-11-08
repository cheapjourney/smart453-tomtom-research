"""Tests for the configuration byte, the allowlist and the transport guard.

No hardware, no serial port. Run from the repository root:

    python -m unittest discover -s tests -v
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import ecu_config as ec  # noqa: E402
import obd_transport as t  # noqa: E402


class DecoderTest(unittest.TestCase):
    def decode(self, value: int) -> dict:
        return ec.decode_ecu_config(bytes([value]))

    def test_measured_byte_0x38(self):
        """0x38 = MirrorLink + MW + LW, Android Auto absent."""
        d = self.decode(0x38)
        self.assertFalse(d["android_auto"])
        self.assertTrue(d["mirrorlink"])
        self.assertTrue(d["fields"]["MW activation"]["set"])
        self.assertTrue(d["fields"]["LW activation"]["set"])
        self.assertFalse(d["fields"]["SPVR_IPhone"]["set"])
        self.assertFalse(d["fields"]["SPVR_OtherPhones"]["set"])

    def test_target_byte_0x78(self):
        """0x78 = the same byte with Android Auto added, nothing else moved."""
        d = self.decode(0x78)
        self.assertTrue(d["android_auto"])
        self.assertTrue(d["mirrorlink"])
        self.assertEqual(
            {k: v["set"] for k, v in d["fields"].items()},
            {k: v["set"] for k, v in self.decode(0x38)["fields"].items()
             if k != "Android Auto feature"} | {"Android Auto feature": True},
        )

    def test_only_android_auto_differs(self):
        a, b = self.decode(0x38)["fields"], self.decode(0x78)["fields"]
        diff = [k for k in a if a[k]["set"] != b[k]["set"]]
        self.assertEqual(diff, ["Android Auto feature"])

    def test_masks_are_msb_first(self):
        masks = {name: info["mask"] for name, info in self.decode(0x00)["fields"].items()}
        self.assertEqual(masks["SPVR_IPhone"], "0x80")
        self.assertEqual(masks["Android Auto feature"], "0x40")
        self.assertEqual(masks["Mirrorlink feature"], "0x20")
        self.assertEqual(masks["MW activation"], "0x10")
        self.assertEqual(masks["LW activation"], "0x08")
        self.assertEqual(masks["SPVR_OtherPhones"], "0x04")

    def test_unused_bits_reported(self):
        self.assertEqual(self.decode(0x03)["unused_bits"], "00000011")

    def test_empty_payload_rejected(self):
        with self.assertRaises(ValueError):
            ec.decode_ecu_config(b"")

    def test_target_value(self):
        self.assertEqual(ec.target_value(0x38), 0x78)
        self.assertEqual(ec.target_value(0x00), 0x40)
        with self.assertRaises(ValueError):
            ec.target_value(0x100)


class AllowlistTest(unittest.TestCase):
    def test_allowed_reads(self):
        for req in (bytes.fromhex("22 F1 87"), bytes.fromhex("22 6C 1C")):
            self.assertEqual(ec.validate_read_request(req), req)

    def test_everything_else_blocked(self):
        for hexstr in ("2E 6C 1C 78", "2E 6C 1C 00", "10 C0", "10 81", "11 01",
                       "14 FF FF FF", "2F 01", "30 00", "31 01", "3B 81",
                       "22 F1 90", "22 F1 87 00"):
            with self.subTest(request=hexstr):
                with self.assertRaises(ec.BlockedRequest):
                    ec.validate_read_request(bytes.fromhex(hexstr))


class TransportGuardTest(unittest.TestCase):
    def test_session_and_reset_commands_refused(self):
        class FakePort:
            def write(self, data):  # pragma: no cover - must not be reached
                raise AssertionError("port must not be used")

        for cmd in ("10 C0", "1081", "11 01", "14 FF", "12 00"):
            with self.subTest(command=cmd):
                with self.assertRaises(t.Blocked):
                    t.send(FakePort(), cmd)

    def test_unknown_adapter_command_refused(self):
        with self.assertRaises(t.Blocked):
            t.send(object(), "ATMA")

    def test_read_answer_refuses_non_read_services(self):
        class NoPort:
            def write(self, data):  # pragma: no cover
                raise AssertionError("port must not be used")
            def flush(self):         # pragma: no cover
                raise AssertionError("port must not be used")

        for req in ("10C0", "1081", "1101", "2E6C1C78", "2701", "31 01", "14 FF FF"):
            with self.subTest(request=req):
                with self.assertRaises(t.Blocked):
                    t.read_answer(NoPort(), req, 0.0)

    def test_read_answer_allows_only_asked_service(self):
        class Port:
            def __init__(self):
                self.sent = []

            def write(self, data):
                self.sent.append(data)

            def flush(self):
                pass

        ok = Port()
        t.read_answer(ok, "10C0", 0.0, allow_services={"10"})
        self.assertEqual(ok.sent, [b"10C0\r"])

        write = Port()
        t.read_answer(write, "2E6C1C78", 0.0, allow_services={"2E"})
        self.assertEqual(write.sent, [b"2E6C1C78\r"])

    def test_isotp_single_frame(self):
        self.assertEqual(t.payload("62 6C 1C 38\r\r>"), bytes.fromhex("626C1C38"))

    def test_isotp_multi_frame(self):
        raw = ("10 0D 62 F1 87 32 35 39 \r"
               "21 31 35 36 32 34 34 52 \r\r>")
        self.assertEqual(t.payload(raw).hex(" ").upper(),
                         "62 F1 87 32 35 39 31 35 36 32 34 34 52")

    def test_classify(self):
        self.assertEqual(t.classify(b""), "NO_ANSWER")
        self.assertEqual(t.classify(bytes.fromhex("7F2E7F")), "NEGATIVE")
        self.assertEqual(t.classify(bytes.fromhex("6E6C1C")), "POSITIVE")
        self.assertEqual(t.nrc_of(bytes.fromhex("7F2E7F")), "0x7F")


if __name__ == "__main__":
    unittest.main(verbosity=2)
