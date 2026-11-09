# TomTom 1ME09 / MFD2.x — diagnostic service families

## 1. Definition basis

`MFD v5.4` (2019-02-28) has 192 requests and 688 data objects. The vehicle unit is
`259156244R` / `1ME0.001.45`; the FCC reference unit is different. The counts below
describe the definition, not a device capability test.

| Service family | Requests |
|---|---:|
| Diagnostic session control | 2 |
| ECU reset | 5 |
| Clear diagnostic information | 1 |
| Read DTC information | 4 |
| Read data by local identifier | 5 |
| Read data by identifier | 71 |
| Write data by identifier | 49 |
| Input/output control | 53 |
| Write data by local identifier | 1 |
| Tester present | 1 |

There is no SecurityAccess, upload/download, or routine-control service in this
definition. It defines a diagnostic session and an after-sales session, but no
programming session. These are definition facts; they do not prove that the device
cannot support another service.

## 2. Confirmed vehicle observations

- A read-only query returned the vehicle part number `259156244R`.
- The configuration byte `0x6C1C` was `0x38`, changed to `0x78` in the after-sales
  session, and read back as `0x78`.
- The identity record read returned 26 bytes; the first ASCII field is `5104R`. The
  exact build is not encoded in this record.
- The version screen names `11.346.3206684-8060`.

The `0x6C1C` write is the **only** deliberately published activation case. It is
documented as one unit, one software state, with no verified recovery path. It is
not a universal recipe.

## 3. Sessions and access

The definition contains a diagnostic session and an after-sales session. The default
session rejected the `0x6C1C` write; the after-sales session accepted it. That
establishes a session requirement for this case, not a general write permission.

The unit has an external USB port and an SD slot. USB can expose an ADB gadget and
an ECM gadget; ADB is gated by the device-class property. No ADB session, root
filesystem, or memory read is part of this public reference.

## 4. What the diagnostics do not establish

- A configuration read is not a memory read.
- A definition without upload/download is not proof that a bench read is impossible.
- A write to `0x6C1C` is not a firmware change.
- A menu entry is not a working projection.
- A missing CarPlay code path in an incomplete image is not proof of device-wide
  absence.
