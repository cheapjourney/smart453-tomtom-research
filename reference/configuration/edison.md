# EMM-T4 / EDISON — configuration fields

## 1. Cornering light

The modern EMM definition contains a cornering configuration flag,
`Nbx_Cornering_CF`, in the lighting block. The vehicle reported it as `0` in both
the single-flag read and the all-configuration record.

| Item | Meaning |
|---|---|
| Field | `Nbx_Cornering_CF` |
| Value read | `0` (disabled) |
| Evidence | L1 real reads in Phase 6.7; raw records private |
| Function test | not performed |
| Front fog | `Nbx_FR_FOG_LAMP_CF = 1`; PWM active; electrical function not tested |
| Parameters | A1 60°, A2 15°, speed 40 km/h; dimming raw 220 |

A value of `0` means the configuration flag is off. It does **not** prove that the
vehicle lacks the hardware, that the function is unavailable for another reason, or
that setting the flag would make the light work. A successful write would still need
a read-back and a physical function test.

The dimming-time scale is unresolved: 220 × 0.1 = 22 s exceeds the declared 8 s
maximum; 220 × 0.01 = 2.2 s is plausible but not independently confirmed.

The legacy and modern definitions use different lighting blocks. A value or a write
path from one generation must not be applied to the other.

## 2. Other configuration blocks

The definition contains lighting, battery-save, lock/unlock, and other body
configuration parameters. The public reference does not publish the full catalogue or
a write sequence. The full field list remains private because the DDT database's
licence is unclear.

The definition's all-configuration block grows from 295 bytes in `SW13_1` to 443
bytes in `SW15_3`. That is a definition-size difference, not a vehicle write and not
a firmware update.

## 3. What is not claimed

- The field is not a hidden “cornering light enable” that is proven to work.
- A read of `0` is not a diagnosis of the lighting hardware.
- A write path in the definition is not a safe procedure.
- A DDT definition change is not an executable firmware change.
