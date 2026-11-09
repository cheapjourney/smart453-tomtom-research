# TomTom 1ME09 / MFD2.x — overview

## 1. Identity

| Field | Vehicle unit | FCC reference unit |
|---|---|---|
| Model | TomTom `1ME09` / MFD2.x | TomTom `1ME09` |
| Renault part number | `259156244R` | `259154108R` |
| Smart/Daimler reference | `4539002904` | `4539001301` |
| TomTom hardware | `1ME0.001.45` | `1ME0.001.27` |
| FCC ID | not applicable | `S4L1ME09` |
| Board | not verified | `TN4D M/B Rev:C` |
| CAN request / response | `0x747` / `0x767` | not verified |
| Functional address | `0x58` | not verified |

The two columns are **different units**. The FCC exhibits are useful for the family
and the board-level context, but they are not proof that the vehicle unit has the
same board, the same NOR layout, or the same software. Board equality is
`UNCONFIRMED`.

## 2. Software

The vehicle's version screen names:

| Field | Value |
|---|---|
| Application version | `11.346.3206684-8060` |
| Build | `3206684` |
| Platform source | `3198575` |
| Android | 2.2 / API 8 |
| Kernel | 2.6.32.9 |
| Product | `TomTom Strasbourg` |
| SoC | TI OMAP3 / OMAP35xx, ARMv7 |

The identity record's first ASCII field is `5104R`; it establishes the software line
but does not encode an exact build. The exact installed build (`3206684` versus
`3168863`) and the update history remain **UNCONFIRMED**.

The DDT definition `MFD v5.4` (2019-02-28) has 192 requests and 688 data objects and
21 autoidents. `MFD v4.6` has the same request and data-object count but only 3
autoidents. These are diagnostic definitions, not firmware.

## 3. Diagnostic service set

| Service family | Requests in MFD v5.4 |
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

The definition has **no** SecurityAccess, upload/download, or routine-control
service. It defines a diagnostic session and an after-sales session, but no
programming session. These are definition facts, not proof that the device cannot
support another service.

The unit exposes a diagnostic interface over CAN and a normal USB port plus an SD
slot externally. The USB gadget has an ADB mode and an ECM mode; ADB is gated by the
device-class property. No ADB session is part of this public reference.

## 4. Configuration and projection

The head unit has configuration data identifiers for branding, HMI variant, radio
features, audio quality, rear camera, gyro, and projection flags. The `0x6C1C` byte
contains the projection flags; the vehicle unit was `0x38` and was changed to `0x78`
in the already-published Android Auto case. The value is not universal: the correct
target is `current | 0x40`, based on what the unit reports.

Android Auto and MirrorLink components are present in the analysed artifacts.
Completeness and actual projection function are not proven. iAP2 media components
are present, but no CarPlay/AirPlay stack was found in the **incomplete** artifacts;
device-wide absence is not proven. See
[`../../configuration/headunit.md`](../../configuration/headunit.md).

## 5. Open questions

- Exact installed build and update history.
- Whether the vehicle board is identical to the FCC reference board.
- Whether the USB ADB path is reachable on this unit and what it exposes.
- Whether UART3/ttyO2 is the U-Boot console and where a test point is.
- Whether the NOR or eMMC can be read on a bench.
- Whether Android Auto projection works; only menu visibility is reported.
- Whether an external CarPlay adapter can provide a working path.
