"""ECU configuration byte for the Smart 453 / TomTom MFD (DID 0x6C1C).

This module is pure: no I/O, no serial port, no side effects. It defines

  * the two read requests this project allows at all,
  * the bit table of the configuration byte, and
  * the decoder used by both the reader and the tests.

Bit numbering
-------------
DDT4All-style descriptors carry a ``bitoffset`` counted from the **most
significant** bit. Offset 0 is the leftmost bit of the byte, so the mask for a
one-bit field is ``1 << (7 - offset)``. Verified against the ddt4all
implementation, where the read path slices an MSB-first binary string and the
write path assigns into an MSB-first binary string.

For the configuration byte that means:

    offset 0 -> 0x80   SPVR for iPhone
    offset 1 -> 0x40   Android Auto
    offset 2 -> 0x20   MirrorLink
    offset 3 -> 0x10   MW activation
    offset 4 -> 0x08   LW activation
    offset 5 -> 0x04   SPVR for other phones

Reading the same numbers as LSB-first offsets is the classic mistake: it shifts
every mask and produces a value that is wrong but plausible.
"""
from __future__ import annotations

DID = "6C1C"
CONFIG_REQUEST = "226C1C"
IDENT_REQUEST = "22F187"
PART_NUMBER = "259156244R"

BIT_ANDROID_AUTO = 0x40
BIT_MIRRORLINK = 0x20

#: The only read requests this project will ever build.
ALLOWED_READ_REQUESTS = {
    bytes.fromhex("22 F1 87"): "part reference",
    bytes.fromhex("22 6C 1C"): "ECU configuration",
}

#: Service identifiers that are refused before any request is built.
BLOCKED_SERVICE_IDS = {
    0x10: "DiagnosticSessionControl",
    0x11: "ECUReset",
    0x14: "ClearDiagnosticInformation",
    0x2E: "WriteDataByIdentifier",
    0x2F: "InputOutputControlByIdentifier",
    0x30: "InputOutputControlByLocalIdentifier",
    0x31: "RoutineControl",
    0x34: "RequestDownload",
    0x35: "RequestUpload",
    0x36: "TransferData",
    0x37: "TransferExit",
    0x3B: "WriteDataByLocalIdentifier",
}

#: name, mask, labels
ECU_CONFIG_BITS = (
    ("SPVR_IPhone", 0x80, {0: "Not present", 1: "Present"}),
    ("Android Auto feature", 0x40, {0: "Not present", 1: "Present"}),
    ("Mirrorlink feature", 0x20, {0: "Not present", 1: "Present"}),
    ("MW activation", 0x10, {0: "No", 1: "Yes"}),
    ("LW activation", 0x08, {0: "No", 1: "Yes"}),
    ("SPVR_OtherPhones", 0x04, {0: "Not present", 1: "Present"}),
)


class BlockedRequest(RuntimeError):
    """Raised when a request is not on the read allowlist."""


def validate_read_request(request: bytes) -> bytes:
    """Return ``request`` if it is an allowed read, otherwise raise."""
    if not isinstance(request, (bytes, bytearray)):
        raise BlockedRequest("request must be bytes")
    request = bytes(request)
    if len(request) < 2:
        raise BlockedRequest(f"request too short: {request.hex(' ')}")
    sid = request[0]
    if sid in BLOCKED_SERVICE_IDS:
        raise BlockedRequest(
            f"service 0x{sid:02X} ({BLOCKED_SERVICE_IDS[sid]}) is blocked"
        )
    if request not in ALLOWED_READ_REQUESTS:
        raise BlockedRequest(
            f"request not on the read allowlist: {request.hex(' ').upper()}"
        )
    return request


def decode_ecu_config(payload: bytes) -> dict:
    """Decode the payload of a positive ``62 6C 1C xx`` answer.

    ``payload`` is everything after the ``62 6C 1C`` echo; only the first byte
    is used. Bits 0 and 1 (masks 0x02, 0x01) are not assigned by the definition
    and are reported separately.
    """
    if not payload:
        raise ValueError("empty payload: no configuration byte after 62 6C 1C")
    value = payload[0]
    fields = {}
    for name, mask, labels in ECU_CONFIG_BITS:
        set_bit = bool(value & mask)
        fields[name] = {
            "mask": f"0x{mask:02X}",
            "set": set_bit,
            "value": labels[1 if set_bit else 0],
        }
    return {
        "raw_byte": f"{value:02X}",
        "raw_bits": format(value, "08b"),
        "android_auto": bool(value & BIT_ANDROID_AUTO),
        "mirrorlink": bool(value & BIT_MIRRORLINK),
        "fields": fields,
        "unused_bits": format(value & 0x03, "08b"),
    }


def target_value(current: int) -> int:
    """The only value this project is willing to write: current | Android Auto."""
    if not 0 <= current <= 0xFF:
        raise ValueError("byte value must be 0..255")
    return current | BIT_ANDROID_AUTO
