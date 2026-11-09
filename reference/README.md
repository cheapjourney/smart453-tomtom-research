# Smart 453 — EMM-T4 / TomTom 1ME09 technical reference

This directory is a public, evidence-tagged reference for two electronic control
units in a 2016 Smart 453 (W453):

- **EMM-T4 / EDISON** — body/energy management, part number `231A07278R`
- **TomTom Smart Media System** — head unit, model `1ME09` / MFD2.x

It records what was measured, what was derived from artifacts, what is reported by
third parties, and what remains unknown. It is **not** a repair manual and **not** a
coding guide. No vehicle communication is part of this reference.

## 1. Scope and limits

| Item | Value |
|---|---|
| Vehicle family | Smart 453 / W453, Renault Twingo III platform |
| EMM part number | `231A07278R` |
| EMM diagnostic identity | `8/414/C132/4022` |
| EMM definition | `EMM_EDISON_DDT2000_SW13_1_V1_3` |
| EMM CAN request / response | `0x74D` / `0x76D` |
| Head-unit part number | `259156244R` |
| Head-unit Smart reference | `4539002904` |
| Head-unit hardware | `1ME0.001.45` |
| Head-unit firmware | `11.346.3206684-8060` |
| Head-unit CAN request / response | `0x747` / `0x767` |

The EMM's **executable firmware version is unknown**. The DDT definition matched by
the identity tuple is a diagnostic description, not the program that runs on the
unit. The head-unit version screen names `11.346.3206684-8060`; the identity record
does not encode an exact build, so `3206684` and `3168863` cannot be separated from
that record alone.

A separately examined FCC unit uses `259154108R`, `4539001301`, and `1ME0.001.27`.
It is **reference material**, not proof that the vehicle unit has the same board or
software.

## 2. What was documented

| Area | EMM-T4 / EDISON | TomTom 1ME09 |
|---|---:|---:|
| Diagnostic requests catalogued | 237 | 192 |
| Total catalogued (Phase 8.4 consolidation) | 429 | 429 |
| Data objects | 2,111 | 688 |
| Configuration field occurrences | 3,890 | 908 |
| Unique configuration names | 2,027 | 503 |
| Real configuration record | 295-byte response payload (293 configuration bytes), 462 fields decoded (Phase 6.7; raw private) | not applicable |
| L1 vehicle observations | 5 reads (Phase 8.4 addendum) | 3 reads + 1 historical write/read-back; projection not tested |
| Full firmware image in the project | no | no |
| Complete root filesystem in the project | not applicable | no |
| Documented OBD2 full-flash read | no | no |

The counts describe the analysed definitions. They do not prove that every listed
service is implemented, that every field is writable, or that a vehicle function
works.

## 3. Evidence system

Every statement is tagged with a level and a status. The level describes **how** the
statement is supported; the status describes **how far** it is established.

| Level | Meaning |
|---|---|
| **L1** | Direct vehicle observation, archived or explicitly referenced |
| **L2** | Verified artifact: hash, parse, firmware image, definition |
| **L3** | Diagnostic-definition only |
| **L4** | External report: manufacturer, regulator, forum, community |
| **L5** | Hypothesis or conditional inference |

Statuses are `CONFIRMED`, `UNCONFIRMED`, `CONTRADICTED`, `NOT_TESTED`, and
`NOT_APPLICABLE`.

The level is always scoped to the exact statement. A confirmed read does not prove a
write; a DDT parameter does not prove a working function; a version number does not
prove executable firmware; a delta update is not a full dump; a missing service in a
definition is not proof that the device cannot support it; a missing code fragment in
an incomplete image is not proof that the whole device lacks it.

See [`methodology/evidence-levels.md`](methodology/evidence-levels.md) for the full
rules and [`evidence/evidence-register.md`](evidence/evidence-register.md) for all
entries.

## 4. Confirmed results

- The EMM identity tuple `8/414/C132/4022` matches exactly one autoidents tuple of
  `EMM_EDISON_DDT2000_SW13_1_V1_3`; the definition has 237 requests and 2,111 data
  objects. The real vehicle read in Phase 6.7 confirms this **definition match**,
  not the executable firmware version.
- A real all-configuration read returned a 295-byte response payload, of which 293
  bytes are configuration data, and 462 decoded fields. The raw payload is private.
  See [`evidence/phase6-7-validation.md`](evidence/phase6-7-validation.md).
- Phase 8.4 consolidates 429 catalogued commands: 237 EMM and 192 head unit. The
  master matrix classifies 420 as `DDT_ONLY`, 8 as `VEHICLE_READ_CONFIRMED`, and 1
  as `VEHICLE_WRITE_CONFIRMED_HISTORICAL`; all 9 L1 events have private archived raw
  records. See [`evidence/phase8-4-consolidation.md`](evidence/phase8-4-consolidation.md).
- The EMM reported the cornering configuration flag as `0` in both the single-flag
  read and the all-configuration record. This is a flag value, not a test that the
  cornering light works.
- The front-fog configuration flag is `1` and PWM configuration is active. The owner
  reports that front fog lamps are installed; electrical function is not proven.
- The cornering parameters are A1 = 60°, A2 = 15°, speed = 40 km/h, dimming raw 220.
  A 2.2 s dimming time is plausible only at 0.01 s/LSB; the definition says
  0.1 s/LSB, so the scale remains unresolved.
- A V4→V5 regression found no lost known values. The V5 narrative claim that menu
  visibility was everywhere unknown is false; V5.1 corrects the documentation
  without changing technical values.
- The head-unit part-number read returned `259156244R`, matching the TomTom
  certification for `1ME0.001.45` / `4539002904`.
- The head-unit configuration byte `0x6C1C` was `0x38`, was changed to `0x78` in the
  after-sales session, and read back as `0x78`. The owner reports that Android Auto
  entries appeared after a restart. The one published case is in
  [`../research/results/ANDROID_AUTO_ACTIVATION_2026-11-08.md`](../research/results/ANDROID_AUTO_ACTIVATION_2026-11-08.md).
- Android Auto and MirrorLink components are present in the analysed head-unit
  artifacts. Completeness and real projection function are not proven.
- The TomTom update contains a kernel image and a root filesystem delta, not a
  complete flash image. The `TOMTOM.000` container is a delivery container, not a
  dump.
- No public firmware image for `231A07278R` and no documented OBD2 full-flash read
  for either unit were found. A negative search is not proof of impossibility.

## 5. What is not claimed

This reference does **not** claim that:

- the EMM's executable firmware is `SW13_1_V1_3`;
- a DDT definition is a firmware image;
- a listed configuration field is writable on the vehicle;
- a full OBD2 dump of either ECU is possible or impossible in principle;
- the FCC reference board is identical to the vehicle board;
- Android Auto projection works, only that the menu entries were reported;
- CarPlay is absent from the whole device, only that no CarPlay/AirPlay stack was
  found in the analysed, incomplete artifacts;
- the multimedia CAN is present on OBD pins 12/13 of this vehicle.

## 6. Open questions

- Exact executable firmware and calibration of the EMM.
- Exact MCU, package, and censorship state of the EMM board.
- Whether a donor EMM can be read on a bench without bypassing protection.
- Exact installed head-unit build (`3206684` versus `3168863`) and update history.
- Whether the head-unit NOR/eMMC can be read on a bench, and at which test points.
- Whether Android Auto projection works with a phone; only the menu visibility is
  reported.
- Whether CarPlay can work through an external adapter; the factory unit has no
  proven CarPlay stack.
- Whether pins 12/13 carry the multimedia CAN on this vehicle.

## 7. Safety and legal

This is research about safety-relevant systems. Nothing here is a substitute for
manufacturer service information. A wrong configuration write can leave a unit that
no longer answers; no recovery path is verified beyond writing the original value
back over the same channel while the unit still responds.

The public repository deliberately excludes vendor firmware, application code,
database content, raw logs, VIN/identifying records, adapter identifiers, and local
paths. Only the already-published `0x6C1C` activation case contains protocol frames;
this reference does not add a second write recipe. See
[`../PUBLICATION_AUDIT.md`](../PUBLICATION_AUDIT.md) and
[`../NOTICE.md`](../NOTICE.md).

## 8. Reproduction

The public data can be checked offline, without a vehicle and without the
proprietary DDT database:

```bash
python3 tools/validate_public.py
```

The validator checks JSON/CSV structure, evidence/source references, level-specific
requirements, blocked content, privacy patterns, and relative links. It writes a
machine-readable and a human-readable report.

Rebuilding the full 237/192 request matrices requires the internal DDT database.
That database is not redistributed because its licence is unclear. See
[`methodology/reproducibility.md`](methodology/reproducibility.md).

## 9. Layout

```
reference/
  README.md
  methodology/       evidence levels and reproducibility
  evidence/          evidence and claim registers, plus Phase 6.7/8.4 addenda
  sources/           source-quality register
  ecu/edison/        EMM identity, firmware, dump feasibility
  ecu/tomtom-headunit/  head-unit identity, firmware, dump feasibility
  diagnostics/       service-family overview, no request recipes
  configuration/     feature semantics, no new write procedure
  firmware/          artifact metadata and hashes, no binaries
  compatibility/     scope and compatibility limits
  research-gaps/     open questions and read-only next steps
  schemas/           JSON schemas for the public data
  tools/             offline validator
  data/              public evidence, claims, sources, counts, metadata
```

## 10. Licence

Documentation in this directory is intended to be covered by the repository's
CC BY 4.0 text licence; code is intended to be covered by the MIT licence. Vendor
firmware, application code, databases, and trademarks remain with their owners. See
[`../NOTICE.md`](../NOTICE.md).
