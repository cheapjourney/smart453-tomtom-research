# Android Auto activation on a Smart 453 TomTom head unit — 2026-11-08

Evidence tags follow `README.md`: **[LIVE]**, **[OFFLINE]**, **[PUBLIC]**,
**[REPORTED]**, **[OPEN]**.

This is a record of one activation performed on one vehicle, by its owner, with
full knowledge of the risks. It is **not** a general retrofit procedure and not a
claim that the same byte value behaves identically on other Smart 453 units.

---

## 1. Vehicle and head unit

| Item | Value | Evidence |
|---|---|---|
| Vehicle | Smart 453 (W453), petrol | **[REPORTED]** |
| Head unit | Factory TomTom unit, model `1ME09`, project "Strasbourg" | **[PUBLIC]** |
| Renault part number | `259156244R` | **[LIVE]** |
| Daimler part number | `4539002904` | **[PUBLIC]**, matches the unit's version screen **[REPORTED]** |
| Application version | `11.346.3206684-8060` | **[LIVE]** (version screen) and **[OFFLINE]** (matches `ngl-complete-version` of the analysed update image) |
| Diagnostic addressing | 11-bit CAN, 500 kbit/s, requests `0x747`, replies `0x767` | **[LIVE]** |
| Configuration DID | `0x6C1C` on the head unit, logical address `0x58` | **[LIVE]** |
| Configuration before | `0x38` | **[LIVE]** |
| Configuration after | `0x78` | **[LIVE]** |

The configuration byte is read with a standard UDS `ReadDataByIdentifier`
(`0x22`) request. `0x38` means MirrorLink present, MW enabled, LW enabled and
Android Auto absent; `0x78` sets only the Android Auto bit on top of that.

## 2. Technical preconditions

| Item | Value | Evidence |
|---|---|---|
| Adapter | OBDLink MX+, STN2255, firmware 5.10.3 | **[LIVE]** |
| Transport | Classic Bluetooth SPP → local RFCOMM relay → virtual serial port | **[LIVE]** |
| Request timeout | 2000 ms, adaptive timing off | **[LIVE]** |
| Supply voltage during the attempt | 12.2 V, engine off, ignition on, head unit running | **[LIVE]** |
| External power supply | **not used**; the owner accepted battery-only operation | **[REPORTED]** |

The adapter's default 102 ms timeout is too short for this unit; every attempt in
this project uses a 2 s timeout with adaptive timing disabled. That is a property
of the transport, not of the coding.

## 3. Bit encoding used

DDT4All-style descriptors number bits from the most significant bit, so the mask
for a one-byte field is `1 << (7 - offset)`:

| Field | DDT4All offset | conventional bit | mask |
|---|---|---|---|
| SPVR for iPhone | 0 | 7 | `0x80` |
| **Android Auto feature** | **1** | **6** | **`0x40`** |
| **MirrorLink feature** | **2** | **5** | **`0x20`** |
| MW activation | 3 | 4 | `0x10` |
| LW activation | 4 | 3 | `0x08` |
| SPVR for other phones | 5 | 2 | `0x04` |

```
before  0x38   0011 1000
mask    0x40   0100 0000   (Android Auto only)
-----------------------------
after   0x78   0111 1000
```

The change is exactly one bit. MirrorLink (`0x20`), MW (`0x10`) and LW (`0x08`)
are already set in `0x38` and are left untouched; SPVR for iPhone and SPVR for
other phones remain clear.

## 4. Chronology of the two write attempts

### 4.1 First attempt — default session (2026-11-08, 16:38)

| Step | Value | Evidence |
|---|---|---|
| Identity read | `259156244R` | **[LIVE]** |
| Configuration read | `0x38` | **[LIVE]** |
| Write request | `2E 6C 1C 78` | **[LIVE]** |
| Response | **`7F 2E 7F`** | **[LIVE]** |
| Interpretation | serviceNotSupportedInActiveSession | **[LIVE]** |

The unit refused the service in the default diagnostic session. No configuration
change occurred; the negative response means the request was rejected before it
was executed. One write frame was sent, no retry, no session change.

### 4.2 Second attempt — after-sales session (2026-11-08, 16:45–16:46)

| Step | Value | Time | Evidence |
|---|---|---|---|
| Identity read | `259156244R` | 16:45:55 | **[LIVE]** |
| Configuration read | `0x38` | 16:45:57 | **[LIVE]** |
| Session request | `10 C0` | 16:45:57 | **[LIVE]** |
| Session response | **`50 C0`** | 16:45:59 | **[LIVE]** |
| Write request | `2E 6C 1C 78` | 16:45:59 | **[LIVE]** |
| Write response | **`6E 6C 1C`** | 16:46:01 | **[LIVE]** |
| Read-back | **`62 6C 1C 78`** | 16:46:03 | **[LIVE]** |

One session frame, one write frame. No retry, no security access, no ECU reset,
no rollback write. The head unit was not restarted during the session.

## 5. Why the first attempt failed and the second succeeded

`10 C0` is not a separate session number: it is session type `0x40` with the
`suppressPosRspMsgIndicationBit` (bit 7) set. The supression applies to *positive*
responses only — a negative response is always sent.

What the two attempts show, on this unit:

- In the default session the head unit does **not** accept a write to `0x6C1C`
  and answers `7F 2E 7F`. This is a confirmed behaviour of this specific ECU.
- After `10 C0` the same write is accepted (`6E 6C 1C`) and the value persists
  (`62 6C 1C 78` on read-back).
- This unit answered the session request with `50 C0` although the suppress bit
  was set. A missing positive answer would have been the expected case and would
  **not** have proven anything; silence must never be read as success.

**Scope of that statement:** it is confirmed for this unit, at this software
version, on this data set. It is *not* a documented requirement of every Smart
453 variant, and the vendor publishes no such requirement. A different build may
accept the write in the default session, require a different session, or reject it
entirely.

## 6. Result

### 6.1 Immediately after the write

The configuration byte read back as `0x78`. That is a **[LIVE]** result: the
head unit itself reports Android Auto present, MirrorLink present, MW and LW
unchanged.

### 6.2 After a restart of the head unit

The owner restarted the head unit and reports: **[REPORTED]**

- the Smartphone Screen menu now shows Android Auto settings,
- an Android Auto tutorial entry appears alongside the MirrorLink ones,
- the setting for automatic Android Auto start is reachable,
- MirrorLink remains present in the menu.

This matters because the head unit does not read the configuration byte on every
screen refresh. It caches the vehicle configuration in a local database and
refreshes it at startup or when the vehicle side signals a completed EOL write —
so a change to the byte alone does not necessarily change the UI until the unit
has restarted.

## 7. Not tested

| Item | Status |
|---|---|
| Actual Android Auto projection over USB with a phone | **[OPEN]** — no phone was connected after the activation |
| CarPlay through a third-party CarLinkit T-Box | **[OPEN]** — the head unit contains no CarPlay stack; whether an external box can work is untested |
| Persistence across a battery disconnect | **[OPEN]** — no read-back after a full power cycle |
| Behaviour on other software versions or other MFD variants | **[OPEN]** |

A visible menu entry is not a working projection. The activation changed a
configuration value and the UI reacted; whether a phone session actually
establishes is a separate question and was not answered here.

## 8. Limits of transferability

- One vehicle, one head unit, one software version (`11.346.3206684-8060`).
- The configuration byte belongs to the head unit's own diagnostic description.
  Whether an arbitrary Smart 453 exposes the same DID with the same bit layout is
  unknown; the part-number table in the vendor document lists variants that differ
  in software.
- The value written depends on the value read: the byte is a set of independent
  flags, and `0x78` is only correct because the unit already reported `0x38`.
  Copying `0x78` to a unit with a different starting value can clear flags that
  were set there.
- The session behaviour is confirmed here only for the default session versus
  `10 C0`. Other session types were not tried.

## 9. Safety and recovery

- The write changes a configuration byte in the head unit. It does not flash
  firmware and does not touch the engine, braking or steering systems.
- A wrong value can leave the head unit with a configuration it does not expect.
  Whether that is recoverable by writing the original byte back depends on the
  unit still answering on the diagnostic bus.
- **No verified recovery path exists** beyond writing the original value back over
  the same diagnostic channel. There is no documented service mode, no recovery
  image in the analysed material, and no independent way to restore the unit if it
  stops answering.
- The value that would restore this unit is the one it reported before the write:
  `0x38`.
- A stable external supply is advisable for any further write. At 12.2 V the
  attempt succeeded, but a voltage dip during a write leaves the outcome
  undetermined.
- The session is not explicitly closed afterwards. The unit returns to its default
  session on timeout or on the next ignition cycle.

## 10. Reproducibility of this record

Every value in section 4 comes from a timestamped diagnostic log kept in the
private project. Those logs are deliberately **not** published: they contain
vehicle traffic and are a fingerprint of the car. What is published here is the
sequence of protocol values, which is what another researcher needs in order to
compare behaviour.
