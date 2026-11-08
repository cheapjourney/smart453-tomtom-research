# 01 — Compatibility

Which head units these notes apply to, and how to find out whether yours is one
of them.

## What this project is about

The factory head unit that Smart fitted to the 453 (fortwo / forfour, including
the electric versions) is a TomTom-built navigation and media unit. TomTom calls
the platform **MFD**, model **1ME09**, internal project **"Strasbourg"**. It runs
a TomTom-specific Android 2.2 build on a TI OMAP3 SoC.

Two phone-projection stacks ship inside that firmware: a **MirrorLink** stack and
an **Android Auto** stack. Both are add-ons; whether they are usable depends on a
configuration byte in the head unit, which this project reads and — in one
documented case — changed.

## Confirmed on this project

| Item | Value | How it was established |
|---|---|---|
| Vehicle | Smart 453, petrol | owner |
| Part number reported over diagnostics | `259156244R` | read from the unit |
| Matches vendor document | TomTom `1ME0.001.45`, Daimler `4539002904`, model `1ME09` | vendor certification document |
| Application version | `11.346.3206684-8060` | version screen of the unit, matches the analysed update image |
| Diagnostic pair | `0x747` request / `0x767` response, 11-bit CAN, 500 kbit/s | read from the unit |

## How to check your own unit

You do not need to write anything to find out whether your head unit is a
candidate. The read-only tool answers the two questions that matter:

```bash
./tools/read_config.py --port /tmp/obdlink-mx
```

It prints the part number and the configuration byte. If the part number is not
`259156244R`, **stop** — this project has no data for your variant.

## When this does not apply

- **Different part number.** The vendor's own table lists variants that differ,
  per the document, "in the software aspects". A different part number can mean a
  different bit layout, a different data identifier or no Android Auto stack at
  all.
- **Different application version.** The activation here was performed on
  `11.346.3206684-8060`. Older builds may not accept the write; newer builds may
  move the flag.
- **Radio variants (MW/LW).** The configuration byte also carries medium-wave and
  long-wave activation. Those bits were already set on this vehicle and were left
  alone. A unit with different flags needs a different target value.
- **Non-TomTom head units.** Smart also shipped other radios. This project says
  nothing about them.

## The rule that matters

**The target value is not a constant.** It is computed from the value your own
unit reports right now:

```
target = current | 0x40
```

On this vehicle that was `0x38 | 0x40 = 0x78`. Copying `0x78` onto a unit that
reports, say, `0x30` would clear bits that unit needs. The tool refuses to run
unless the target you confirm equals `current | 0x40`.

## Evidence tags

Throughout `docs/`, `research/` and the tool output:

| Tag | Meaning |
|---|---|
| **TESTED** | performed on the vehicle described here, with logged answers |
| **DOCUMENTED** | described by a third party (vendor manual, forum guide); not executed by this project |
| **DERIVED** | computed from a definition or from the recorded answers |
| **NOT TESTED** | planned or plausible, but never verified |
