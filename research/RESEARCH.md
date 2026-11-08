# Smart 453 — TomTom head unit: research notes

Every statement carries an evidence tag from `README.md`: **[LIVE]**, **[OFFLINE]**,
**[PUBLIC]**, **[REPORTED]**, **[OPEN]**. If a sentence has no tag at all, treat it as
an open question.

---

## 1. Goal

Determine whether the factory head unit of a Smart 453 can be reached over the
vehicle's diagnostic connector, and whether its phone-projection capability can be
understood well enough to reason about further work — without writing to any
control unit. **[REPORTED]**

The work split into three parts:

1. establish a stable transport from a laptop to an OBD-II adapter,
2. read only identification data from the head unit over diagnostics,
3. analyse a firmware image the vendor publishes publicly, offline.

Until 2026-11-08 the work was read-only: identification reads and offline image
analysis. On that date a single configuration byte in the head unit was written,
by the owner of the vehicle, with the sequence documented in section 9. No other
control unit was written to, no firmware was flashed and no adaptation of a
safety-relevant system was performed.

---

## 2. Environment

### Vehicle

| Item | Value | Evidence |
|---|---|---|
| Model | Smart 453 (W453), petrol engine | **[REPORTED]** |
| Head unit | Factory TomTom-based unit, model `1ME09` | **[PUBLIC]** |

### Diagnostic transport

| Item | Value | Evidence |
|---|---|---|
| Adapter | OBDLink MX+, chipset STN2255, firmware v5.10.3 | **[LIVE]** |
| Adapter identity string | `ATI` → `ELM327 v1.4b`, `STI` → `STN2255 v5.10.3` | **[LIVE]** |
| Host | macOS 12.7.6, Intel x86_64 | **[LIVE]** |
| Link | Classic Bluetooth 3.0 SPP, RFCOMM channel 1 | **[LIVE]** |
| Protocol | ISO 15765-4, 11-bit CAN, 500 kbit/s | **[LIVE]** |
| Addressing | Normal (29-bit not used for this unit) | **[LIVE]** |

The adapter's persisted `/dev/cu.*` device proved unreliable on this host: after
the first session the port object opened instantly and returned no data while the
adapter itself kept answering over RFCOMM. A direct RFCOMM-to-TCP/PTY bridge solved
it; that bridge is a separate project and not part of these notes. **[LIVE]**

### Firmware under analysis

| Item | Value | Evidence |
|---|---|---|
| Source | Vendor-published update image, downloaded from the vendor's public host | **[PUBLIC]** |
| Container | Signed update package inside an ext3 delivery image, SHA-256 verified against the vendor's manifest | **[OFFLINE]** |
| Platform | Android 2.2 (API 8), Linux 2.6.32.9, ARMv7 / TI OMAP3 | **[OFFLINE]** |
| Product string | `ro.product.model` = "TomTom Strasbourg" | **[OFFLINE]** |

The image is **not redistributed** with these notes. Only conclusions drawn from it
are published; see `PUBLICATION_AUDIT.md`.

---

## 3. Confirmed findings about the head unit

### 3.1 Identity

The unit answers the standard UDS ReadDataByIdentifier request for the part
reference and returns a 10-character Renault-style part number, `259156244R`.
**[LIVE]**

The vendor's certification document for this product family lists that exact part
number in its part-number table. The same table maps it to TomTom part
`1ME0.001.45`, Daimler part `4539002904`, model name `1ME09` and the internal
project name "Strasbourg". **[PUBLIC]**

That is the single strongest result of the project: a value read from the car and a
value in a public document agree exactly, so the unit in the vehicle is identified
with certainty, not by inference.

### 3.2 A second identification service

The unit also answers a legacy KWP-style "read data by local identifier" request
and returns a longer structured identification record containing calibration and
software references. The record is 26 bytes and arrives as an ISO-TP multi-frame
response. **[LIVE]**

The individual field boundaries of that record are **not** documented publicly, so
the fields are not decoded here. Publishing a half-guessed layout would be worse
than publishing none.

### 3.3 Diagnostic addresses

Requests are addressed to `0x747`, replies arrive on `0x767`, using normal 11-bit
addressing. Both are outside the legislated OBD range. **[LIVE]**

Because the response offset is `0x20` rather than the legislative `+8`, the
adapter's automatic flow-control filter does not match and has to be configured
explicitly. A detail worth recording: with the adapter's factory default request
timeout of 102 ms, the unit's answer was missed entirely; a 2000 ms timeout (with
adaptive timing disabled) produced a reliable reply. **[LIVE]**

### 3.4 What is not on the diagnostic bus

A passive capture of the diagnostic bus at the connector showed 59 distinct
11-bit identifiers, all in the `0x0xx`–`0x6xx` range, and **none** in `0x7xx`.
**[LIVE]**

No diagnostic traffic for the head unit was observed passively. That is expected,
not contradictory: diagnostic addresses normally answer only when addressed. The
absence of a unit's traffic in a passive capture says nothing about whether it can
be reached.

### 3.5 Diagnostic access that exists — and its limit

Over the diagnostic connector the unit exposes identification reads only. There is
no memory-read service in its diagnostic description, no upload service and no
security-access service. **[OFFLINE]** (from the unit's own diagnostic description)

So the diagnostic connector is a legitimate way to *identify* the unit, and not a
way to extract its file system.

---

## 4. Phone-projection architecture (high level)

The firmware contains **two** independent phone-projection implementations, both
shipped as add-on applications rather than as part of the core navigation
software. **[OFFLINE]**

### 4.1 Common shape of both stacks

Both follow the same integration pattern:

```
add-on application (own package, own signature)
    → background service exposing a binder/AIDL interface
    → menu entry contributed to the HMI framework
    → native library for the transport, video and audio path
```

Both declare themselves as trusted third-party add-ons, both request the
permission that marks an app as **hidden from the app manager**, and both are
signed with the same development certificate as the rest of the system software.
**[OFFLINE]**

### 4.2 MirrorLink stack

A third-party MirrorLink implementation (licensed technology, sold under the
"MirrorLink™" name) provides:

- a service plus a companion application,
- integration with the HMI dialog system and with hardware media keys,
- policy and security sub-packages (MirrorLink restricts which applications may be
  used while driving),
- its own transport, display and audio handling. **[OFFLINE]**

### 4.3 Android Auto stack

A second stack from the same third-party supplier provides Android Auto:

- a companion service declared as an application component,
- native transport modules for USB accessory mode (AOA), a video sink with decoder,
  audio sender and sink, and a Bluetooth endpoint,
- vehicle sensor data supplied through the platform's sensor service. **[OFFLINE]**

Both stacks were implemented completely in the image — this is not a stub or a
licence placeholder. **[OFFLINE]**

### 4.4 There is no CarPlay

No CarPlay stack, no AirPlay implementation and no CarPlay-related strings exist
anywhere in the analysed applications. **[OFFLINE]**

The unit does contain an Apple accessory authentication chip and an iPod/iAP
implementation (media playback and remote control of a connected Apple device).
**[OFFLINE]** That is Apple accessory support, not CarPlay: CarPlay uses a different
protocol on the same physical link.

### 4.5 Why the head unit is not user-modifiable

Three independent gates were identified. **[OFFLINE]**

| Gate | Mechanism |
|---|---|
| Debug shell | ADB and the serial console are only started when a factory-data value marks the device as a development unit |
| App installation | The package installer is reachable through a service that requires a signature-level permission |
| Update | The update package and its job list are signed; the signature is verified before installation |

None of the three was circumvented, and no attempt was made to bypass them.

---

## 5. DDT4All configuration structure

DDT4All and its DDT2000 heritage describe each ECU in a declarative file rather
than in code. The structure, as it applies to this unit: **[PUBLIC] [OFFLINE]**

- **ECU identity**: a logical diagnostic address (this unit uses `0x58`), a name
  and a supplier/version tuple. The CAN request and response identifiers are
  derived from the address by a fixed rule stored alongside it.
- **Requests**: a catalogue of named requests, each with a service identifier, a
  payload and a description of the expected reply.
- **Field definitions**: the reply payload is described as a set of fields, each with
  a bit offset, a bit length, an interpretation (unsigned, signed, ASCII) and a
  scale/offset for physical units. The offset counts from the most significant bit —
  see section 6.1 for the exact mapping.
- **Bit-field enumerations**: individual bits inside a field are named, so a single
  configuration byte can carry several independent flags.

This is why the same byte can be read as a number *and* as a set of switches — and
why the bit-numbering convention matters, which is the next section.

The vendor-specific database that fills this structure is **not** redistributed
here; its licensing is unclear. See `PUBLICATION_AUDIT.md`.

---

## 6. Bit encoding: MSB-first, and the 0x38 → 0x78 example

### 6.1 Two numbering systems, and why they get mixed up

DDT descriptors carry a `bitoffset` that is counted **from the most significant
bit**: offset `0` is the leftmost bit of the byte. Conventional bit numbering counts
the other way round, from the least significant bit. Both describe the same byte, so
the two series run in opposite directions:

| DDT4All offset | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|---|
| conventional bit | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
| mask | 0x80 | 0x40 | 0x20 | 0x10 | 0x08 | 0x04 | 0x02 | 0x01 |

For a field one byte wide the mask follows directly:

```
mask = 1 << (7 - ddt_bitoffset)
```

**Verified against the ddt4all implementation [PUBLIC].** In `ecu_data.py` the read
path converts the response bytes into an MSB-first binary string and slices it with
`hextobin[startBit : startBit + bits]`; the write path assigns
`requestasbin[start_bit + i] = valueasbin[i]`. In both, `bitoffset 0` lands on the
leftmost — most significant — bit. The little-endian branch uses
`lastbit = 7 - startBit + 1`, which is the same mapping expressed in conventional
bit numbers.

The practical trap: **"bit 6" and "DDT offset 6" are different bits.** Bit 6 is mask
`0x40`; DDT offset 6 is mask `0x02`. Reading a descriptor as if the two matched
shifts the mask by one position at a time, which yields a value that differs from
the intended one and still looks like a plausible hex number.

### 6.2 The arithmetic

Take the starting byte:

```
0x38 = 0b0011_1000
       ^^^ ^^^^
       │   └── bits 3,4,5 set   (0x08 + 0x10 + 0x20)
       └────── bits 6,7 clear
```

Setting conventional bit 6 — DDT4All offset 1, mask `0x40` — with a logical OR:

```
0x38      0011 1000
0x40  OR  0100 0000
-------------------
0x78      0111 1000
```

So `0x38 | 0x40 = 0x78`. In descriptor terms this sets **bitoffset 1** of that byte;
the delta is exactly `0x40`, one bit position. **[REPORTED]**

**Android Auto = DDT4All offset 1 = conventional bit 6 = mask `0x40`.**
**[REPORTED]**

### 6.3 What this example turned out to be

`0x38` is the value the head unit reported for data identifier `0x6C1C` on
2026-11-08; `0x78` is the value after setting that single bit, written to the unit
and read back. **[LIVE]**

The example is no longer hypothetical. It is documented as a case, not as a
recipe:

- the write was performed once, on one vehicle, by its owner, and confirmed by
  read-back and by the user interface after a restart — see section 9,
- the byte's location, owning unit and bit layout are stated there because that is
  the finding,
- whether another unit of the same family accepts the same value is unknown; the
  value depends on the flags already set in the byte.

A related trap, and this one is verifiable in the implementation: the little-endian
switch in a descriptor changes **byte order**, not the bit-numbering convention. The
offset still counts from the most significant bit; only the byte sequence is
reversed. Do not read an endian flag as a statement about bit direction. **[PUBLIC]**

---

## 7. Evidence summary

| Finding | Level |
|---|---|
| Unit identity `259156244R`, matching the public certification table | **[LIVE] [PUBLIC]** |
| Diagnostic pair `0x747`/`0x767`, 11-bit normal addressing | **[LIVE]** |
| 2 s adapter timeout required, 102 ms default misses the reply | **[LIVE]** |
| 59 bus identifiers observed passively, none in `0x7xx` | **[LIVE]** |
| Android 2.2 / API 8, kernel 2.6.32.9, ARMv7 OMAP3 | **[OFFLINE]** |
| Two complete projection stacks (MirrorLink, Android Auto) | **[OFFLINE]** |
| No CarPlay / AirPlay stack present | **[OFFLINE]** |
| Apple accessory (iAP) support present, media role only | **[OFFLINE]** |
| Three software gates: factory device class, signed installer, signed update | **[OFFLINE]** |
| DDT descriptor structure | **[PUBLIC] [OFFLINE]** |
| MSB-first offset convention, verified in `ecu_data.py` | **[PUBLIC]** |
| `0x38 | 0x40 = 0x78` (DDT offset 1, conventional bit 6) | **[LIVE]** — written and read back on 2026-11-08 |
| `2E` to `0x6C1C` refused in the default session with `7F 2E 7F` | **[LIVE]** |
| Accepted after `10 C0` (`50 C0`), answered `6E 6C 1C`, read-back `0x78` | **[LIVE]** |
| Android Auto entries visible in the UI after a restart | **[REPORTED]** |
| Projection over USB / CarPlay via an external box | **[OPEN]** |

---

## 8. Open questions

### 8.1 Diagnostic session

- Does the unit require a diagnostic session before answering the legacy
  identification service? A negative response would tell, but that requires an
  active request. **[OPEN]**
- Which session values does it accept, and does it enforce a timeout that closes
  the session again? **[OPEN]**

### 8.2 ECU compatibility

- The public part-number table lists several variants that differ, per the document
  itself, only in software. Whether a diagnostic description for one variant is
  valid for another is unknown. **[OPEN]**
- Whether the two identification services are answered identically across those
  variants. **[OPEN]**

### 8.3 Recovery

- No recovery image and no documented service mode were found in the analysed
  material. A failed modification may therefore be unrecoverable without
  desoldering. **[OFFLINE] [OPEN]**
- Whether the unit exposes a bootloader-level console on any external connector is
  unknown; no accessible test points were identified in the public teardown photos.
  **[OPEN]**

### 8.4 Android Auto activation

- Whether the installed Android Auto add-on is enabled on a retail unit: **answered
  for this unit on 2026-11-08.** The configuration byte carried Android Auto as
  absent; after setting the single bit and restarting, the UI shows the entries.
  **[LIVE] [REPORTED]** — see section 9.
- Whether a USB phone session actually establishes, and whether a third-party
  CarPlay box works on top of it, remains **untested**. A menu entry is not a
  working projection. **[OPEN]**
- Whether other units of the same family behave identically is unknown; the
  starting byte differs per vehicle configuration. **[OPEN]**

### 8.5 Legal and ethical questions

- What the vendor's firmware licence permits in terms of publishing *findings* (as
  opposed to code) is not settled. This repository publishes no vendor code, which
  keeps the question academic for now. **[OPEN]**

---

## 9. Confirmed Android Auto ECU configuration and UI activation — 2026-11-08

A single configuration byte of the head unit was written on this vehicle, by its
owner, after the read-only phase described above. This section records the
protocol facts; the full account, including preconditions and limits, is in
[`results/ANDROID_AUTO_ACTIVATION_2026-11-08.md`](results/ANDROID_AUTO_ACTIVATION_2026-11-08.md).

### 9.1 What changed

| | Value | Evidence |
|---|---|---|
| Data identifier | `0x6C1C` on the head unit (logical address `0x58`) | **[LIVE]** |
| Before | `0x38` | **[LIVE]** |
| After | `0x78` | **[LIVE]** |
| Delta | `0x40`, i.e. DDT4All offset 1 / conventional bit 6 | **[LIVE]** |

`0x38` = MirrorLink present, MW enabled, LW enabled, Android Auto absent.
`0x78` adds Android Auto and touches nothing else. MirrorLink and both radio bands
were already set and were carried over unchanged.

### 9.2 First attempt: rejected in the default session

`2E 6C 1C 78` answered **`7F 2E 7F`** — serviceNotSupportedInActiveSession. The
request was rejected before execution; the byte did not change. One write frame
was sent, no retry, no session change. **[LIVE]**

### 9.3 Second attempt: after-sales session

| Frame | Answer |
|---|---|
| `10 C0` | `50 C0` |
| `2E 6C 1C 78` | `6E 6C 1C` |
| `22 6C 1C` (read-back) | `62 6C 1C 78` |

One session frame, one write frame, no retry, no security access, no reset. All
three answers are **[LIVE]**. **[LIVE]**

`10 C0` is session type `0x40` with the `suppressPosRspMsgIndicationBit` set. That
bit suppresses only *positive* responses; a negative response is always sent. This
unit answered anyway, but a silent session request would have proven nothing and
must not be read as success.

**The session requirement is confirmed for this unit at this software version, not
for every Smart 453.** The vendor documents no such requirement, and a different
build may accept the write in the default session or reject it in any session.

### 9.4 User interface

After a restart of the head unit the owner reports that the Smartphone Screen menu
shows Android Auto settings and an Android Auto tutorial entry, that the automatic
start setting is reachable, and that MirrorLink is still present. **[REPORTED]**

The restart matters: the unit caches the vehicle configuration locally and
refreshes it at startup or on a vehicle-side end-of-line signal, so the byte alone
does not change the screen.

### 9.5 What this does not show

- A phone was not connected after the activation; USB projection is **untested**.
  **[OPEN]**
- A third-party CarPlay box was not tried; the firmware contains no CarPlay stack.
  **[OPEN]**
- Persistence across a full power cycle was not read back. **[OPEN]**
- Transferability to other units is unknown; the correct target value depends on
  the flags a given unit already reports. **[OPEN]**

### 9.6 Recovery

There is no verified recovery path beyond writing the original value back over the
same diagnostic channel. For this unit that value was `0x38`. If a unit stops
answering diagnostics, no documented service mode or recovery image is available
in the material analysed here. **[OFFLINE] [OPEN]**
