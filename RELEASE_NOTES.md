# Research snapshot — 2026.11.09

**Status:** documented research snapshot candidate. No Git tag, push or GitHub
release has been created for this snapshot.

## Scope

The snapshot consolidates the public Smart 453 reference for:

- EMM-T4/EDISON `231A07278R`, autoident `8/414/C132/4022`, definition
  `EMM_EDISON_DDT2000_SW13_1_V1_3`;
- TomTom 1ME09 / MFD2.x head unit `259156244R`, software line
  `11.346.3206684-8060`;
- 429 catalogued diagnostic requests (237 EMM + 192 head unit);
- 9 L1 vehicle events (8 reads, 1 historical head-unit write with read-back);
- the documented Android Auto configuration change on the head unit.

**The activation is one historical case on one unit/software state, not a supported
retrofit procedure.** The write and read-back are confirmed; Android Auto projection
with a phone was not tested, and no recovery path is verified.

## Included public data

| Item | Value |
|---|---:|
| Evidence entries | 60 |
| Claims | 35 |
| Sources | 44 |
| Reference files | 53 |
| Offline tests | 40/40 |
| Public validator | 0 errors, 0 warnings |

The 429 requests are DDT-definition entries. They are not a claim that all commands
are implemented or available on a vehicle. Only the nine L1 events have archived raw
evidence; the raw archive remains private.

## Explicit non-claims

- No full OBD2 firmware dump for either ECU.
- No identification of the executable EMM firmware from the DDT definition.
- No proof that the head-unit update container is a full flash image.
- No proof that Android Auto projection works; menu visibility and projection are
  separate.
- No claim that the head-unit multimedia CAN is present on OBD pins 12/13.
- No universal diagnostic allowlist.

## Firmware and licence

No vendor firmware, update package, root filesystem, extracted application or DDT
database is included. Documentation is CC BY 4.0; original code is MIT. Third-party
rights are stated in `NOTICE.md`.

## Historical disclosure

The already-public `0x6C1C` activation case is the only published raw
request/response case. The new `reference/` tree adds no raw request pair. The
historical 16 raw-identifier matches outside `reference/` are retained, not
expanded; see `PUBLICATION_AUDIT.md` section 12.

## Validation

```bash
cd reference
python3 tools/validate_public.py
cd ..
python3 -m unittest discover -s tests -v   # 40/40 with pyserial
```

## Next research goals

EMM MCU/flash and censorship state from a documented donor; exact installed head-unit
build; multimedia-CAN pins 12/13; Android Auto projection test; CarPlay adapter
assessment. No vehicle access is authorised by this release note.
