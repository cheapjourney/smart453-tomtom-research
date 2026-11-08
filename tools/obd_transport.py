"""Thin transport layer for an ELM327/STN adapter on ISO 15765 CAN.

Shared by the reader and the writer. It owns the adapter command allowlist, the
ISO-TP reassembly and one-shot request/answer handling.

Deliberate limits:

  * only the commands in ``ADAPTER_COMMANDS`` can be emitted,
  * any command starting with ``10``, ``11``, ``12`` or ``14`` is refused —
    no session change, no reset, no DTC clearing, ever,
  * ``request()`` sends exactly once; there is no retry anywhere in this file.
"""
from __future__ import annotations

import time

#: Adapter setup, in this order. Verified against the OBDLink MX+ used in the
#: project; AT SP 6 selects ISO 15765-4, 11-bit, 500 kbit/s.
ADAPTER_COMMANDS = (
    "ATE0", "ATL0", "ATS1", "ATH1", "ATD0", "ATCAF1",
    "STP 33", "STCAF 0", "ATSH 747", "ATCRA 767",
    "STCFCPA 747, 767", "ATAT0", "STPTO 2000",
)

ADAPTER_TOKENS = {c.split()[0] for c in ADAPTER_COMMANDS} | {"ATRV"}

FORBIDDEN_PREFIXES = ("10", "11", "12", "14")

HEXCHARS = set("0123456789ABCDEF")


class TransportError(RuntimeError):
    pass


class Blocked(TransportError):
    pass


def send(port, command: str, timeout: float = 2.0) -> str:
    """Send one adapter command and read until the prompt."""
    token = command.split()[0]
    if token not in ADAPTER_TOKENS:
        raise Blocked(f"adapter command not allowed: {command}")
    if command.startswith(FORBIDDEN_PREFIXES):
        raise Blocked(f"session/reset command refused: {command}")
    port.write((command + "\r").encode())
    port.flush()
    buf = b""
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        chunk = port.read_until(b">")
        if not chunk:
            break
        buf += chunk
        if chunk.endswith(b">"):
            break
    return buf.decode(errors="replace")


def segments(raw: str) -> list[list[int]]:
    """Split adapter output into byte lists, one per received CAN frame."""
    segs = []
    for line in raw.replace("\r", "\n").split("\n"):
        toks = line.strip().rstrip(">").split()
        if not toks:
            continue
        if len(toks[0]) in (3, 8) and all(c in HEXCHARS for c in toks[0].upper()):
            toks = toks[1:]
        vals = []
        for t in toks:
            if len(t) == 2 and all(c in HEXCHARS for c in t.upper()):
                vals.append(int(t, 16))
            else:
                vals = []
                break
        if vals:
            segs.append(vals)
    return segs


def payload(raw: str) -> bytes:
    """Strip ISO-TP framing (single frame, first+consecutive, or CAF1)."""
    segs = segments(raw)
    if not segs:
        return b""
    b0 = segs[0][0]
    pci = b0 >> 4
    if pci == 0:
        length = b0 & 0x0F
        data = bytes(segs[0][1:])
        for s in segs[1:]:
            data += bytes(s)
        return data[:length] if length <= len(data) else data
    if pci == 1 and len(segs[0]) >= 2:
        total = ((b0 & 0x0F) << 8) | segs[0][1]
        data = bytearray(segs[0][2:])
        for s in segs[1:]:
            data += bytes(s[1:]) if s[0] >> 4 == 2 else bytes(s)
        return bytes(data[:total])
    data = bytearray()
    for s in segs:
        data += bytes(s)
    return bytes(data)


def read_answer(port, request_hex: str, timeout: float) -> tuple[bytes, str]:
    """Send one UDS payload and return (payload, raw text). No retry."""
    port.write((request_hex + "\r").encode())
    port.flush()
    buf = b""
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        chunk = port.read_until(b">")
        if not chunk:
            continue
        buf += chunk
        if chunk.endswith(b">"):
            break
    raw = buf.decode(errors="replace")
    return payload(raw), raw


def classify(data: bytes) -> str:
    if not data:
        return "NO_ANSWER"
    if data[0] == 0x7F:
        return "NEGATIVE"
    return "POSITIVE"


def nrc_of(data: bytes) -> str:
    return f"0x{data[2]:02X}" if len(data) > 2 else "?"
