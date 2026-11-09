# Phase 8.4/8.5 — master evidence consolidation

This addendum consolidates the Phase 8.4 evidence reconciliation into the public
reference. It publishes derived counts and statuses only. The 429-row command
catalogue, the per-command payloads, the nine raw L1 records, and the head-unit logs
remain private.

## 1. Consolidated counts

| Item | Value |
|---|---:|
| Diagnostic commands catalogued | 429 |
| EMM commands | 237 |
| Head-unit commands | 192 |
| `DDT_ONLY` rows | 420 |
| — EMM `DDT_ONLY` | 232 |
| — Head unit `DDT_ONLY` | 188 |
| `VEHICLE_READ_CONFIRMED` rows | 8 |
| — EMM read-confirmed | 5 |
| — Head unit read-confirmed | 3 |
| `VEHICLE_WRITE_CONFIRMED_HISTORICAL` rows | 1 |
| Archived L1 measurement events | 9 |
| of which reads | 8 |
| of which historical write + read-back | 1 |

The nine L1 events are five EMM reads, three head-unit reads, and one historical
head-unit write with read-back. The write is a past event; it is not a current write
permission.

## 2. EMM configuration size — 293 vs 295

The earlier Phase 6 reports used **295 bytes** for the all-configuration response.
Phase 8.4 separates the two quantities:

| Quantity | Bytes | Meaning |
|---|---:|---|
| Response payload | 295 | Complete positive response payload, 43 ISO-TP frames |
| Positive-response header | 2 | The first two response bytes |
| Configuration data | 293 | The bytes decoded into 462 fields |

The 295-byte figure is the **transport/response payload**, not the configuration
payload. Neither figure is a firmware image.

## 3. EMM / EDISON

- Part number `231A07278R`; autoident `8/414/C132/4022`.
- Definition `EMM_EDISON_DDT2000_SW13_1_V1_3`: 237 commands, 2,111 data objects.
- CAN request/response `0x74D`/`0x76D`.
- Five archived read observations: identity, part number, cornering parameters,
  cornering flag, and the all-configuration record.
- The cornering flag is `0`; front fog is configured; the electrical function and a
  future write remain unverified.
- 295 response bytes = 2 header bytes + 293 configuration bytes; 462 fields.
- The definition is not the executable firmware version.
- No full EMM flash dump is present; no full-flash read over the examined OBD/DDT
  services is documented.

## 4. TomTom / Headunit

- TomTom 1ME09 / MFD2.x; part number `259156244R`; Smart reference `4539002904`;
  hardware `1ME0.001.45`; firmware line `11.346.3206684-8060`.
- Definition MFD v5.4: 192 commands, 688 data objects.
- Three archived read observations: identity, part number, and the `0x6C1C`
  configuration byte before the historical write.
- Historical write: `0x6C1C` changed from `0x38` to `0x78`; read-back was `0x78`.
  This is a **configuration write**, not proof of Android Auto projection.
- Android Auto and MirrorLink menu visibility is documented; projection function is
  not tested.
- The analysed update artifacts are a kernel image and a root filesystem delta, not
  a complete flash image. No complete OBD2 firmware dump is documented.

## 5. Multimedia CAN — access caveat

The head unit is associated with the multimedia CAN on OBD pins **12/13**, not the
standard diagnostic pins 6/14. A standard OBD2 adapter connected to pins 6/14 does
not automatically reach the head unit. The physical access path on this vehicle is
not confirmed. This is an access/topology question before it is a software question.

## 6. Evidence

| ID | Level | Status | Statement | Sources |
|---|---|---|---|---|
| `EV-P84-001` | L2 | CONFIRMED | The catalogue contains 429 commands: 237 EMM and 192 head unit; 420 rows are DDT_ONLY. | `SRC-PHASE84` |
| `EV-P84-002` | L2 | CONFIRMED | 8 read-confirmed rows, 1 historical-write row, and 9 archived L1 events (8 reads + 1 write/read-back). | `SRC-PHASE84` |
| `EV-P84-003` | L1 | CONFIRMED | Five EMM read observations; the all-configuration response has 295 payload bytes = 2 header bytes + 293 configuration bytes, 462 fields. | `SRC-PHASE84`, `SRC-PHASE67` |
| `EV-P84-004` | L1 | CONFIRMED | Three head-unit read observations plus one historical `0x6C1C` write with read-back. | `SRC-PHASE84` |
| `EV-P84-005` | L1 | CONFIRMED | All nine L1 events have private archived raw records and SHA-256 references; none is public. | `SRC-PHASE84` |
| `EV-P84-006` | L3 | UNCONFIRMED | The head unit is on multimedia CAN pins 12/13; a standard OBD2 adapter does not automatically reach it. | `SRC-PINOUT-RENAULT`, `SRC-PHASE84` |
| `EV-P84-007` | L2 | CONFIRMED | The EMM all-configuration response spans 43 ISO-TP frames and about 893 ms; it is not firmware. | `SRC-PHASE84`, `SRC-PHASE67` |
| `EV-P84-008` | L2 | CONFIRMED | The head-unit update artifacts are a kernel and a root filesystem delta, not a complete flash image. | `SRC-FIRMWARE-INVENTORY`, `SRC-PHASE84` |

Machine-readable: [`../data/phase8_4_evidence.json`](../data/phase8_4_evidence.json).

## 7. Claims

| ID | Claim | Status | Evidence |
|---|---|---|---|
| `CLM-P84-001` | The consolidated matrix has 429 diagnostic commands: 237 EMM, 192 head unit. | CONFIRMED | `EV-P84-001` |
| `CLM-P84-002` | The matrix has 420 DDT_ONLY, 8 read-confirmed and 1 historical-write row; 9 L1 events. | CONFIRMED | `EV-P84-002` |
| `CLM-P84-003` | The EMM all-configuration response is 295 payload bytes = 2 header bytes + 293 configuration bytes. | CONFIRMED | `EV-P84-003` |
| `CLM-P84-004` | All nine L1 events have private archived raw records and hashes. | CONFIRMED | `EV-P84-005` |
| `CLM-P84-005` | The historical head-unit write changed `0x6C1C` from `0x38` to `0x78`; read-back was `0x78`. | CONFIRMED | `EV-P84-004` |
| `CLM-P84-006` | Android Auto projection is functionally confirmed. | NOT_TESTED | `EV-P84-004` |
| `CLM-P84-007` | A complete EMM firmware dump over OBD is proven. | UNCONFIRMED | `EV-P84-003`, `EV-P84-007` |
| `CLM-P84-008` | A complete head-unit firmware dump over OBD is proven. | UNCONFIRMED | `EV-P84-006`, `EV-P84-008` |
| `CLM-P84-009` | A standard OBD2 adapter on pins 6/14 automatically reaches the multimedia CAN. | UNCONFIRMED | `EV-P84-006` |

Machine-readable: [`../data/phase8_4_claims.csv`](../data/phase8_4_claims.csv).

## 8. What does not follow

- A catalogued command is not an implemented or tested command.
- A confirmed configuration write is not a confirmed vehicle function.
- A response payload of 295 bytes is not 295 bytes of firmware.
- A head-unit delta update is not a full flash image.
- A missing OBD service is not device-wide impossibility.
- A private raw record is not publishable merely because its derived fact is public.
