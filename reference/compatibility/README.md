# Compatibility and scope

## 1. What the reference covers

This reference is for one **2016 Smart 453 / W453** with:

- EMM-T4 / EDISON, part number `231A07278R`, identity tuple `8/414/C132/4022`;
- TomTom Smart Media System `1ME09`, part number `259156244R`, hardware
  `1ME0.001.45`, application `11.346.3206684-8060`.

It is not a general Smart 453 compatibility list. A different model year, part
number, or software version may behave differently.

## 2. What does not transfer

| Item | Why it does not transfer |
|---|---|
| FCC reference unit `259154108R` / `1ME0.001.27` | different part numbers; board equality unproven |
| Other EMM definitions (`SW14`, `SW15`, …) | different identity sets; definition is not firmware |
| Other head-unit part numbers | different software/aspects; no per-unit verification |
| Other Renault head units | different platform and service set |
| Other model years | wiring, gateway, and software may differ |
| The `0x78` value | target is `current | 0x40`, not a constant |
| Multimedia-CAN pins 12/13 | not physically confirmed on this vehicle |

## 3. What is version-independent

The following are infrastructure statements, not ECU-specific facts:

- the CAN IDs and functional addresses used by the two units in this vehicle;
- the need to distinguish a diagnostic definition from executable firmware;
- the evidence-level rules;
- the publication policy.

Even these should be re-checked before applying them to another vehicle.

## 4. Compatibility claims that are not made

- “All Smart 453 units have the same head unit.”
- “All 1ME09 units accept the same configuration byte.”
- “The FCC board is the vehicle board.”
- “A DDT definition named SW15 is a firmware update.”
- “Android Auto works because the menu is visible.”
- “CarPlay can be enabled by coding.”

None of these is supported by the evidence in this reference.
