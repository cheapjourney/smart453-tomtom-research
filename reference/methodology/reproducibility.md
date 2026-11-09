# Reproducibility

## 1. What can be reproduced publicly

The `reference/data/` files and all documentation can be checked without a vehicle
and without the proprietary DDT database:

```bash
python3 tools/validate_public.py
```

The validator uses only the Python standard library. It checks:

- every claim has at least one evidence ID;
- every evidence ID exists and has at least one source ID;
- every source ID exists;
- every L1 entry has a measurement reference or an explicit archive-gap note;
- every L2 entry has an artifact reference or a hash;
- every L4 entry has a public locator or a stated access limitation;
- ECU statements have a hardware and software scope;
- JSON and CSV files parse and required columns exist;
- no blocked binary, firmware, database, raw-log, or credential file is present;
- no absolute home path, RFC 1918 address, MAC address, VIN pattern, or credential
  value appears in public files;
- relative documentation links resolve;
- no raw diagnostic request recipe appears outside the one already-published
  `0x6C1C` case.

The output is written to `validation_report.json` and `VALIDATION_REPORT.md` in the
working directory.

## 2. What cannot be reproduced publicly

The full 237-request EMM matrix and 192-request head-unit matrix are generated from
a third-party DDT database whose licence is unclear. The database is not
redistributed. The full matrices therefore cannot be rebuilt from this public tree.

The same applies to:

- firmware and update images (`TOMTOM.000`, `.ttpkg`, rootfs delta);
- extracted application code;
- raw vehicle logs and measurement records;
- VIN/identification records;
- internal source locators.

Those inputs remain private. The public evidence statements are independently
formulated facts, with hashes and metadata where allowed. No missing proprietary input
was replaced by invented test data.

## 3. Internal reproduction

The private working tree contains the extractor, registry builders, schemas, and
validators used in Phases 8.2 and 8.3. Rebuilding the matrices requires:

- Python 3.11 or newer;
- the local DDT database (`ecu_db.zip`, SHA-256
  `b78813c23f72cae283d50aa771d86e18375921125bafa8bae7da85953dcb90a1`);
- the firmware and report artifacts listed in the private source registry;
- no vehicle connection.

The internal validator additionally checks the full CSV/JSON structure. It is not
part of the public tree because it reads internal paths and restricted data.

## 4. Environment

| Item | Value |
|---|---|
| Host | Linux x86_64, offline analysis |
| Python | 3.11+ |
| Public validator dependencies | standard library only |
| Internal extractor | Python 3.11+, local JSON/CSV tooling |
| Vehicle access in Phase 8.3 | none |
| CAN/OBD commands in Phase 8.3 | none |
| Network use | source reachability checks and public research only |

## 5. Reproducibility limits by evidence level

| Level | Public reproduction | Internal reproduction |
|---|---|---|
| L1 | Only the derived statement; raw measurement is not public | Yes, from the private measurement record if present |
| L2 | Metadata/hash and the formulated statement | Yes, with the named artifact |
| L3 | Definition name and scoped statement | Yes, with the DDT database |
| L4 | Public URL or document identifier | Yes, subject to access |
| L5 | The stated condition and missing observation | Not applicable; it is a hypothesis |

A statement that cannot meet its level's minimum requirement is downgraded in the
Phase 8.3 audit, not silently kept.
