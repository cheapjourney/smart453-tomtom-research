# 05 — Identifying the head unit

Before anything else, prove that the unit in front of you is the unit this project
describes. Two reads are enough, and both are read-only.

## Run the reader

```bash
./tools/read_config.py --port /tmp/obdlink-mx
```

It sends exactly two requests and nothing else:

| Request | Service | Meaning |
|---|---|---|
| `22 F1 87` | ReadDataByIdentifier, part reference | the unit's part number |
| `22 6C 1C` | ReadDataByIdentifier, configuration | one byte of feature flags |

No session change, no write, no retry. The allowlist is in `tools/ecu_config.py`
and is enforced before a frame is built.

## Expected output on the research vehicle

```
identity : POSITIVE  62 F1 87 32 35 39 31 35 36 32 34 34 52  '259156244R'
config   : 0x38  (bits 00111000)
           0x80  SPVR_IPhone             Not present
           0x40  Android Auto feature    Not present
           0x20  Mirrorlink feature      Present
           0x10  MW activation           Yes
           0x08  LW activation           Yes
           0x04  SPVR_OtherPhones        Not present
           Android Auto: NOT PRESENT
           MirrorLink  : PRESENT
```

`TESTED` — this is the actual answer the unit gave on 2026-11-08, twice, about two
seconds each.

## What each value tells you

- **Part number `259156244R`** — matches the vendor's certification table, which
  maps it to TomTom `1ME0.001.45`, Daimler `4539002904`, model `1ME09`.
- **`0x38`** — MirrorLink is enabled, both radio bands are enabled, Android Auto is
  not. This is the starting point of the activation.
- **`0x78`** — the same byte with Android Auto added. See
  `06-android-auto-activation.md`.

## The second identification service (optional)

The unit also answers a legacy KWP-style read (`21 80`) with a 26-byte record
containing software and calibration references. It is **not** part of the tools
here, and its field boundaries are not publicly documented, so it is not decoded.
It is mentioned because it explains why some guides talk about software numbers
like `383C` or `4531`.

## If the identity does not match

Stop. Do not continue to the activation chapter.

| Symptom | Meaning |
|---|---|
| Part number differs | different variant, different software; no data here |
| `7F 22 12` | the unit does not implement that identifier in that form |
| `NO DATA` | transport problem, not an identity problem — see `troubleshooting.md` |
| Identity answers, configuration times out | try again once; then treat as a transport fault |

The tool exits with code 4 on a part-number mismatch and prints what it read.
