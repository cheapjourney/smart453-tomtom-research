# TomTom 1ME09 — configuration fields

## 1. The `0x6C1C` projection byte

The head unit has one configuration byte at data identifier `0x6C1C` that carries
the projection flags. The bits observed in the definition and the vehicle are:

| Bit | Mask | Meaning |
|---:|---:|---|
| 7 | `0x80` | iPhone / smartphone video (SPVR iPhone) |
| 6 | `0x40` | Android Auto |
| 5 | `0x20` | MirrorLink |
| 4 | `0x10` | MW (medium wave) |
| 3 | `0x08` | LW (long wave) |
| 2 | `0x04` | other phones / SPVR other |

The vehicle unit reported `0x38` (MirrorLink, MW, LW; Android Auto off). The
after-sales session accepted a write of `0x78` (the same value with bit 6 set), and
the unit read back `0x78`. The owner reports that Android Auto entries appeared after
a restart.

The full published case, including the protocol frames, is in
[`../../research/results/ANDROID_AUTO_ACTIVATION_2026-11-08.md`](../../research/results/ANDROID_AUTO_ACTIVATION_2026-11-08.md).
That case is one unit, one software state, and has no verified recovery path. `0x78`
is **not** a universal value: the correct target is `current | 0x40`, based on what
the unit reports.

## 2. Related configuration fields

The definition also contains:

| Identifier | Field | Meaning |
|---|---|---|
| `0x6C14` | branding | 1 byte, 37 observed values; 27 Mercedes-Benz, 28 Smart, 32 JBL, 33 Car2Go |
| `0x6C15` | HMI variant | 2 bits: 0 Renault, 1 Daimler, 2 neutral, 3 reserved |
| `0x6C20` | radio configuration | TMC, USB, external premium amplifier, satellite, CD, DAB |
| `0x6C4D` | audio quality / speakers | 4-bit audio quality, rear loudspeakers, subwoofer |
| `0x6C0E` | rear camera | guidelines set |
| `0x6C23` | gyro | gyro-related bits |

These are definition-derived meanings. A field being present does not prove that the
vehicle has the hardware or that a change is safe.

## 3. Sessions

The default diagnostic session rejected the `0x6C1C` write; the after-sales session
accepted it. This is a session requirement for the published case, not a general
write permission. No programming session is defined in MFD v5.4.

## 4. What is not claimed

- A configuration byte is not firmware.
- A menu entry is not a working projection.
- A successful write is not proof of a safe or reversible change.
- A field name is not proof that the vehicle accepts a write.
- `0x78` must not be copied to another unit with a different current value.
