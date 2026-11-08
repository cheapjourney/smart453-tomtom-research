#!/usr/bin/env python3
"""One-shot, fail-closed writer for the Android Auto bit of the head unit.

This is the ONLY part of the project that can put a write on the bus. It is
locked by default and sends exactly one write frame, for one data identifier,
after proving identity, voltage and the value that was read a moment earlier.

Safety rules, all enforced in code
---------------------------------
  * Locked twice: ``config/aa_write.json`` must contain ``"enabled": true`` and
    the CLI needs ``--arm``. With either switch missing nothing is opened.
  * No free-form payload. The frame is ``2E 6C 1C <current | 0x40>``; anything
    else refuses to start.
  * The part number is re-read and must match ``--expect-part``.
  * The configuration byte is read immediately before the write and must equal
    ``--expect-current``.
  * Adapter supply voltage is read and must be at least ``--min-voltage``.
  * At most ONE write frame. No retry, no rollback, no reset.
  * ``10 C0`` only when ``--session-after-sales`` is given, and only once. No
    other session command is reachable: the transport refuses anything starting
    with 10, 11, 12 or 14.

Exit codes: 0 ok · 2 identity · 3 value · 4 voltage · 5 gate · 6 negative
response · 7 no answer · 8 read-back mismatch · 9 transport.

Read docs/06-android-auto-activation.md before running this. The value that is
correct on one unit can be wrong on another.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from ecu_config import (  # noqa: E402
    BIT_ANDROID_AUTO, CONFIG_REQUEST, IDENT_REQUEST, PART_NUMBER, target_value,
)
import obd_transport as t  # noqa: E402

SESSION_REQUEST = "10C0"       # session type 0x40, suppressPosRspMsgIndicationBit
SESSION_TYPE = 0x40
EXPECTED_WRITE_PREFIX = bytes.fromhex("6E6C1C")
EXPECTED_READ_PREFIX = bytes.fromhex("626C1C")


class Abort(RuntimeError):
    def __init__(self, code: int, message: str):
        super().__init__(message)
        self.code = code


def gate_path(cli_value: str | None) -> Path:
    if cli_value:
        return Path(cli_value)
    env = os.environ.get("AA_WRITE_GATE")
    if env:
        return Path(env)
    return HERE.parent / "config" / "aa_write.json"


def gate_open(path: Path) -> bool:
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("enabled") is True
    except (FileNotFoundError, json.JSONDecodeError):
        return False


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Write the Android Auto bit once, or refuse to start.")
    ap.add_argument("--port", required=True, help="serial device, e.g. /tmp/obdlink-mx")
    ap.add_argument("--gate", default=None, help="path to the gate file")
    ap.add_argument("--arm", action="store_true", help="second switch")
    ap.add_argument("--session-after-sales", action="store_true",
                    help="send exactly one 10 C0 before the write")
    ap.add_argument("--expect-part", default=PART_NUMBER)
    ap.add_argument("--expect-current", default=None, help="required value, hex, e.g. 38")
    ap.add_argument("--confirm-target", default=None, help="value to write, hex")
    ap.add_argument("--min-voltage", type=float, default=12.5)
    ap.add_argument("--timeout", type=float, default=3.0)
    ap.add_argument("--log", default=None, help="JSONL log path")
    args = ap.parse_args(argv)

    gate = gate_path(args.gate)
    if not gate_open(gate):
        print(f"REFUSED: {gate} does not set \"enabled\": true", file=sys.stderr)
        return 5
    if not args.arm:
        print("REFUSED: --arm missing (second switch)", file=sys.stderr)
        return 5
    if args.expect_current is None or args.confirm_target is None:
        print("REFUSED: --expect-current and --confirm-target are mandatory",
              file=sys.stderr)
        return 5
    expect_current = int(args.expect_current, 16)
    confirm_target = int(args.confirm_target, 16)
    if confirm_target != target_value(expect_current):
        print(f"REFUSED: target 0x{confirm_target:02X} is not "
              f"0x{expect_current:02X} | 0x{BIT_ANDROID_AUTO:02X}", file=sys.stderr)
        return 5

    log_path = Path(args.log) if args.log else (
        HERE.parent / "logs" / f"write_{dt.datetime.now():%Y%m%d_%H%M%S}.jsonl")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    steps = []

    def log(step: str, **kw):
        entry = {"ts": dt.datetime.now().astimezone().isoformat(timespec="milliseconds"),
                 "step": step, **kw}
        steps.append(entry)
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")

    try:
        import serial
    except ImportError:
        print("pyserial is required: pip install -r requirements.txt", file=sys.stderr)
        return 9

    code = 0
    port = None
    try:
        port = serial.Serial(args.port, 115200, timeout=0.2, write_timeout=2.0)
        for cmd in t.ADAPTER_COMMANDS:
            rsp = t.send(port, cmd)
            if "OK" not in rsp.upper():
                raise Abort(9, f"adapter rejected {cmd}: {rsp.strip()!r}")
        log("adapter_configured")

        rsp = t.send(port, "ATRV")
        m = re.search(r"(\d+(?:\.\d+)?)\s*V", rsp, re.I)
        volts = float(m.group(1)) if m else None
        log("voltage", volts=volts, min=args.min_voltage)
        if volts is None or volts < args.min_voltage:
            raise Abort(4, f"voltage {volts} V below {args.min_voltage} V")

        data, raw = t.read_answer(port, IDENT_REQUEST, args.timeout)
        kind = t.classify(data)
        if kind == "NO_ANSWER":
            raise Abort(7, "identity: no answer")
        if kind == "NEGATIVE":
            raise Abort(2, f"identity: NRC {t.nrc_of(data)} ({raw.strip()!r})")
        if not data.startswith(bytes.fromhex("62F187")):
            raise Abort(2, f"identity: unexpected answer {data.hex(' ').upper()}")
        part = data[3:].decode("ascii", errors="replace")
        log("identity", ascii=part)
        if args.expect_part and args.expect_part not in part:
            raise Abort(2, f"part number {part!r} != {args.expect_part}")

        data, raw = t.read_answer(port, CONFIG_REQUEST, args.timeout)
        kind = t.classify(data)
        if kind == "NO_ANSWER":
            raise Abort(7, "config read: no answer")
        if kind == "NEGATIVE":
            raise Abort(3, f"config read: NRC {t.nrc_of(data)} ({raw.strip()!r})")
        if not data.startswith(EXPECTED_READ_PREFIX):
            raise Abort(3, f"config read: unexpected answer {data.hex(' ').upper()}")
        current = data[3]
        log("current", value=f"0x{current:02X}")
        if current != expect_current:
            raise Abort(3, f"current 0x{current:02X} != expected 0x{expect_current:02X}")

        target = target_value(current)
        if target != confirm_target:
            raise Abort(3, f"target 0x{target:02X} != confirmed 0x{confirm_target:02X}")

        session_confirmed = None
        if args.session_after_sales:
            log("session_request", frame=SESSION_REQUEST)
            sdata, sraw = t.read_answer(port, SESSION_REQUEST, args.timeout)
            if not sdata:
                session_confirmed = False
                log("session_no_response",
                    meaning="suppress bit set: silence is expected, state UNCONFIRMED")
                print("session : no positive answer (suppress bit) - UNCONFIRMED")
            elif sdata[0] == 0x7F:
                raise Abort(6, f"session rejected: NRC {t.nrc_of(sdata)} ({sraw.strip()!r})")
            elif sdata[0] == 0x50 and (len(sdata) > 1 and (sdata[1] & 0x7F) == SESSION_TYPE):
                session_confirmed = True
                log("session_confirmed", raw=sdata.hex(" ").upper())
                print(f"session : {sdata.hex(' ').upper()}")
            else:
                raise Abort(9, f"session: unexpected answer {sdata.hex(' ').upper()}")

        frame = f"2E6C1C{target:02X}"
        print(f"write   : {frame}")
        log("write_request", frame=frame)
        wdata, wraw = t.read_answer(port, frame, args.timeout)
        kind = t.classify(wdata)
        if kind == "NEGATIVE":
            log("write_rejected", nrc=t.nrc_of(wdata), raw=wraw.strip())
            raise Abort(6, f"write rejected: NRC {t.nrc_of(wdata)} ({wraw.strip()!r})")
        if kind != "POSITIVE" or not wdata.startswith(EXPECTED_WRITE_PREFIX):
            raise Abort(7, f"write: no usable answer ({wraw.strip()!r})")
        log("write_accepted", raw=wdata.hex(" ").upper())
        print(f"accepted: {wdata.hex(' ').upper()}")

        data, raw = t.read_answer(port, CONFIG_REQUEST, args.timeout)
        kind = t.classify(data)
        if kind == "NO_ANSWER":
            raise Abort(7, "read-back: no answer")
        if kind == "NEGATIVE":
            raise Abort(8, f"read-back: NRC {t.nrc_of(data)} ({raw.strip()!r})")
        if not data.startswith(EXPECTED_READ_PREFIX):
            raise Abort(8, f"read-back: unexpected answer {data.hex(' ').upper()}")
        readback = data[3]
        log("readback", value=f"0x{readback:02X}", expected=f"0x{target:02X}")
        print(f"readback: 0x{readback:02X}")
        if readback != target:
            raise Abort(8, f"read-back 0x{readback:02X} != 0x{target:02X}")
        log("done", session_confirmed=session_confirmed)

    except Abort as exc:
        code = exc.code
        print(f"ABORT[{exc.code}]: {exc}", file=sys.stderr)
        log("abort", code=exc.code, message=str(exc))
    except t.TransportError as exc:
        code = 9
        print(f"ERROR: {exc}", file=sys.stderr)
        log("error", message=str(exc))
    except Exception as exc:  # noqa: BLE001
        code = 9
        print(f"ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        log("error", message=f"{type(exc).__name__}: {exc}")
    finally:
        if port is not None:
            try:
                port.close()
            except Exception:
                pass
        payload = json.dumps(steps, sort_keys=True, ensure_ascii=False)
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"step": "summary",
                                 "sha256": hashlib.sha256(payload.encode()).hexdigest(),
                                 "write_frames_sent": sum(1 for s in steps
                                                          if s["step"] == "write_request"),
                                 "session_frames_sent": sum(1 for s in steps
                                                            if s["step"] == "session_request"),
                                 "result": "success" if code == 0 else f"aborted_{code}"})
                     + "\n")
        print(f"log: {log_path}")
    return code


if __name__ == "__main__":
    sys.exit(main())
