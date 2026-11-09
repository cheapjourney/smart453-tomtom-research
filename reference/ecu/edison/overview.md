# EMM-T4 / EDISON — overview

## 1. Identity

| Field | Value | Evidence |
|---|---|---|
| Vehicle | Smart 453 / W453, Renault Twingo III platform | vehicle scope |
| Part number | `231A07278R` | owner/vehicle record |
| Variant | EMM-T4 (community report; L4/Bosch attribution unconfirmed) | `EV-EMM-009` |
| Role | Body/energy management; called SAM-F in the driver footwell | owner/vehicle record |
| Diagnostic definition | `EMM_EDISON_DDT2000_SW13_1_V1_3` | `EV-EMM-002` |
| Identity tuple | `8/414/C132/4022` | `EV-EMM-003` |
| CAN request / response | `0x74D` / `0x76D` | project measurement |
| Protocol | CAN, 11-bit, 500 kbit/s | project measurement |
| Functional address | `0x27` | project measurement |
| Real configuration record | 295-byte response payload (293 configuration bytes), 462 fields decoded (Phase 6.7; raw private) | `EV-P67-001` |

The part number is known for this vehicle. The Bosch EMM-T4 L4 attribution and the
alternative numbers `A4539000403`, `3058565646`, `237105821R`, and `237107789R` come
from dead dealer/parts listings and are **not independently confirmed**; they are not
used as confirmation here. A single community report describes a 2020 replacement
`231A07278R` unit as EMM-T4; that is not an independent confirmation either. The MCU
is not confirmed; `SPC560B54L` and `SPC560B60L5` are forum candidates only.

## 2. The definition is not the firmware

`EMM_EDISON_DDT2000_SW13_1_V1_3` is a DDT2000 diagnostic description. It contains
237 requests and 2,111 data objects, and the identity tuple matches one of its
autoidents entries exactly. That proves the **definition selection**, not that the
executable program on the unit is “SW13_1_V1_3”.

The installed executable firmware and calibration remain **unknown**. No public
firmware image for `231A07278R` was found, and no public index entry for it in the
Renault Reprog V191 archive was confirmed.

## 3. What the definition contains

| Service family | Requests | Interpretation |
|---|---:|---|
| Diagnostic session control | 2 | session handling |
| ECU reset | 1 | reset service is defined |
| Clear diagnostic information | 1 | DTC clearing is defined |
| Read DTC information | 6 | fault-code reads |
| Read data by local identifier | 81 | local-identifier reads |
| Read data by identifier | 74 | data-identifier reads |
| Communication control | 1 | communication control is defined |
| Input/output control | 25 | IO-control requests |
| Write data by local identifier | 45 | configuration writes |
| Tester present | 1 | keep-alive |

The definition has **no** SecurityAccess, upload/download, or routine-control
service. That is a property of this definition, not proof that the ECU cannot support
such a service. The full request catalogue is not published because the DDT
database's licence is unclear.

## 4. Cornering-light parameter

The modern definition contains `Nbx_Cornering_CF` in the lighting configuration.
The vehicle reported the flag as `0` in both the single-flag read and the
all-configuration record. The older definition line uses a different
lighting-configuration block and a different write path; the two generations are not
interchangeable.

The real record also shows `Nbx_FR_FOG_LAMP_CF = 1`, PWM configuration active, and
cornering parameters A1 = 60°, A2 = 15°, speed = 40 km/h. The owner reports that
front fog lamps are installed; their electrical function is not proven. The
dimming-time scale is unresolved: raw 220 is 22 s at the documented 0.1 s/LSB but
2.2 s at 0.01 s/LSB.

This reference does **not** publish a write recipe. The flag value `0` is not a test
that the cornering light works, and the EMM may require additional hardware or
configuration that was not measured. See
[`../../configuration/edison.md`](../../configuration/edison.md) and
[`../../evidence/phase6-7-validation.md`](../../evidence/phase6-7-validation.md).

## 5. Related definition generations

The project compared eleven EMM_EDISON definitions. They differ in request counts,
data objects, and autoidents. `SW15_2` and `SW15_3` have identical request and data
sets. A higher DDT number is not a firmware update, and it is not a recommendation to
change anything on the vehicle.

The definition family includes `SW10`, `SW11_1`, `SW12`, `SW13`, `SW13_1`, `SW14`,
`SW15_1`, `SW15_2`, `SW15_3`, and `SW15_V1_1`. `SW13_1_V1_3` is newer than
`SW14_V1_3` by file date, which is one reason DDT numbers must not be read as a
chronological update chain.

## 6. Open questions

- Exact executable firmware and calibration.
- Exact MCU, package, flash size, and censorship state.
- Whether a replacement/donor unit is readable on a bench without bypass.
- Whether the front fog lamps are electrically functional.
- Whether a cornering write persists, updates the all-configuration record, and has
  a verified rollback.
- The raw reprogramming-history record and the installed software identity.
