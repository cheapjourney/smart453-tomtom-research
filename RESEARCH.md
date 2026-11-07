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

No coding, adaptation or programming was performed at any point.

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
- **Field definitions**: the reply payload is described as a set of fields, each
  with a bit offset, a bit length, an interpretation (unsigned, signed, ASCII) and
  a scale/offset for physical units.
- **Bit-field enumerations**: individual bits inside a field are named, so a single
  configuration byte can carry several independent flags.

This is why the same byte can be read as a number *and* as a set of switches — and
why the bit-numbering convention matters, which is the next section.

The vendor-specific database that fills this structure is **not** redistributed
here; its licensing is unclear. See `PUBLICATION_AUDIT.md`.

---

## 6. Bit encoding: MSB-first, and the 0x38 → 0x78 example

### 6.1 The convention

In DDT-style descriptors bits are numbered **MSB-first**: bit 7 is the most
significant bit of the byte, bit 0 the least significant.

```
bit    7   6   5   4   3   2   1   0
mask 0x80 0x40 0x20 0x10 0x08 0x04 0x02 0x01
```

A "bit 6" flag therefore corresponds to mask `0x40`, not `0x04`. Getting this
backwards is the classic error when translating a descriptor into a byte value,
and it produces a value that is wrong but plausible — the worst kind, because the
unit accepts it silently.

### 6.2 The arithmetic

Take the starting byte:

```
0x38 = 0b0011_1000
       ^^^ ^^^^
       │   └── bits 3,4,5 set   (0x08 + 0x10 + 0x20)
       └────── bits 6,7 clear
```

Setting bit 6 (mask `0x40`) with a logical OR:

```
0x38      0011 1000
0x40  OR  0100 0000
-------------------
0x78      0111 1000
```

So `0x38 | 0x40 = 0x78`. The delta is exactly `0x40`, one bit, MSB-first
numbering. **[REPORTED] [OFFLINE]**

### 6.3 What this example is and is not

`0x38` is the starting value used in the project's own notes for a configuration
byte associated with the Android Auto add-on; `0x78` is the arithmetic target after
setting that single bit. **[REPORTED]**

It is published here purely as an illustration of the encoding convention. It is
**not** a procedure:

- the write was never performed,
- it is not known whether the unit validates or reverts that byte,
- the byte's exact location, owning ECU and effect are not stated here on purpose.

A second operator detail is worth recording because it is a common source of
misreading: some descriptors number bits LSB-first instead. When a value "almost"
looks right, check the convention before checking the data.

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
| DDT descriptor structure and MSB-first bit numbering | **[PUBLIC] [OFFLINE]** |
| `0x38 | 0x40 = 0x78` for the AA-related configuration byte | **[REPORTED]** |

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

- Whether the installed Android Auto add-on is enabled on a retail unit was never
  verified. The stack is present and complete; whether the vehicle's configuration
  enables it is untested. **[OPEN]**
- The `0x38`/`0x78` example above is arithmetic, not a result. No activation was
  attempted or observed. **[OPEN]**

### 8.5 Legal and ethical questions

- What the vendor's firmware licence permits in terms of publishing *findings* (as
  opposed to code) is not settled. This repository publishes no vendor code, which
  keeps the question academic for now. **[OPEN]**
