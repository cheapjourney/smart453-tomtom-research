#!/usr/bin/env python3
"""Read the head unit's identity and configuration byte — read-only.

VALIDATION: mock-tested only. Behaviour is verified against the mock head unit in
tests/; this file has never been run against a vehicle.

Sends exactly two requests, both ``ReadDataByIdentifier``:

    22 F1 87   part reference  (must return the expected part number)
    22 6C 1C   configuration byte

No session change, no write, no reset, no retry. The allowlist lives in
``ecu_config.py`` and is enforced before a frame is built.

Usage:
    ./read_config.py --port /dev/cu.OBDSERIAL
    ./read_config.py --port /tmp/obdlink-mx --json out.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ecu_config import (  # noqa: E402
    CONFIG_REQUEST, IDENT_REQUEST, PART_NUMBER,
    decode_ecu_config, validate_read_request,
)
import obd_transport as t  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Read-only ECU identity and configuration.")
    ap.add_argument("--port", required=True, help="serial device, e.g. /tmp/obdlink-mx")
    ap.add_argument("--timeout", type=float, default=3.0, help="answer window in seconds")
    ap.add_argument("--expect-part", default=PART_NUMBER, help="expected part number")
    ap.add_argument("--json", default=None, help="write the result to this file")
    args = ap.parse_args(argv)

    try:
        import serial
    except ImportError:
        print("pyserial is required: pip install -r requirements.txt", file=sys.stderr)
        return 2

    for req in (IDENT_REQUEST, CONFIG_REQUEST):
        validate_read_request(bytes.fromhex(req))

    result: dict = {"timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "steps": []}
    port = None
    code = 0
    try:
        port = serial.Serial(args.port, 115200, timeout=0.2, write_timeout=2.0)
        for cmd in t.ADAPTER_COMMANDS:
            rsp = t.send(port, cmd)
            if "OK" not in rsp.upper():
                raise t.TransportError(f"adapter rejected {cmd}: {rsp.strip()!r}")
        result["steps"].append({"step": "adapter_configured"})

        data, raw = t.read_answer(port, IDENT_REQUEST, args.timeout)
        kind = t.classify(data)
        ascii_part = data[3:].decode("ascii", errors="replace") if kind == "POSITIVE" else ""
        result["identity"] = {"request": "22 F1 87", "result": kind,
                              "raw": data.hex(" ").upper(), "ascii": ascii_part,
                              "expected": args.expect_part}
        print(f"identity : {kind}  {data.hex(' ').upper()}  {ascii_part!r}")
        if kind != "POSITIVE":
            print(f"           unexpected answer: {raw.strip()!r}", file=sys.stderr)
            return 3
        if args.expect_part and args.expect_part not in ascii_part:
            print(f"           part number mismatch (expected {args.expect_part})", file=sys.stderr)
            return 4

        data, raw = t.read_answer(port, CONFIG_REQUEST, args.timeout)
        kind = t.classify(data)
        result["config"] = {"request": "22 6C 1C", "result": kind,
                            "raw": data.hex(" ").upper()}
        if kind != "POSITIVE":
            print(f"config   : {kind}  {data.hex(' ').upper()}", file=sys.stderr)
            return 5

        decoded = decode_ecu_config(data[3:])
        result["config"]["decoded"] = decoded
        print(f"config   : 0x{decoded['raw_byte']}  (bits {decoded['raw_bits']})")
        for name, info in decoded["fields"].items():
            print(f"           {info['mask']}  {name:<24}{info['value']}")
        print(f"           Android Auto: {'PRESENT' if decoded['android_auto'] else 'NOT PRESENT'}")
        print(f"           MirrorLink  : {'PRESENT' if decoded['mirrorlink'] else 'NOT PRESENT'}")

    except t.Blocked as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        code = 6
    except t.TransportError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        code = 7
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        code = 8
    finally:
        if port is not None:
            try:
                port.close()
            except Exception:
                pass
        if args.json:
            Path(args.json).write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
            print(f"written: {args.json}")
    return code


if __name__ == "__main__":
    sys.exit(main())
