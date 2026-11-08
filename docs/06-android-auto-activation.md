# 06 — Android Auto activation

This is the chapter the rest of the repository exists for. Read all of it before
running anything. Two routes are described; only one of them was executed by this
project.

**Status of this document**

| Route | Status |
|---|---|
| Manual route with DDT4All, as described in public guides | **DOCUMENTED** — not executed by this project |
| `tools/write_config.py` | **TESTED** on the research vehicle on 2026-11-08 |

---

## 1. What is being changed

One byte, one bit. The head unit stores its feature set in data identifier
`0x6C1C`:

| DDT4All offset | conventional bit | mask | field |
|---|---|---|---|
| 0 | 7 | `0x80` | SPVR for iPhone |
| **1** | **6** | **`0x40`** | **Android Auto feature** |
| 2 | 5 | `0x20` | MirrorLink feature |
| 3 | 4 | `0x10` | MW activation |
| 4 | 3 | `0x08` | LW activation |
| 5 | 2 | `0x04` | SPVR for other phones |

DDT4All-style descriptors count the offset **from the most significant bit**, so
offset 1 is mask `0x40` — not `0x02`. Reading the offsets as conventional bit
numbers shifts every mask and produces a plausible but wrong value.

On the research vehicle:

```
before  0x38   0011 1000   MirrorLink + MW + LW
mask    0x40   0100 0000   Android Auto only
----------------------------------------------
after   0x78   0111 1000   nothing else moved
```

**The target is computed, not fixed:** `target = current | 0x40`. The tool refuses
any other target.

## 2. Read and back up the current value

```bash
./tools/read_config.py --port /tmp/obdlink-mx --json logs/before.json
```

Note the byte it prints. On this vehicle it was `0x38`. That value is your way
back if anything goes wrong — write it down offline as well, not only on the
machine you are using.

## 3. The session question

`WriteDataByIdentifier` (`2E`) was **refused in the default diagnostic session**
on this unit:

```
2E 6C 1C 78   →   7F 2E 7F      serviceNotSupportedInActiveSession
```

`TESTED` — this is the actual first attempt, 2026-11-08 16:38.

After switching to the after-sales session it was accepted. The session request is
`10 C0`, which is session type `0x40` with the
`suppressPosRspMsgIndicationBit` (bit 7) set.

Two consequences worth understanding:

- That suppression bit applies to **positive** responses only. A negative response
  is always sent. So a rejected session is visible, but a missing answer to
  `10 C0` proves nothing — it must be recorded as *unconfirmed*, never as success.
- On this unit the session request was answered anyway (`50 C0`). That is a
  property of this ECU, not a guarantee.

**Scope:** the session requirement is confirmed for this unit at application
version `11.346.3206684-8060`. It is not a documented requirement of every Smart
453. A different build may accept the write without a session, or reject it in
every session.

## 4. Route A — our tool (TESTED)

### Prepare the gate

The tool is locked twice: a config flag and a command line switch.

```bash
cp config/aa_write.example.json config/aa_write.json
# edit config/aa_write.json: "enabled": true
```

Leave it `false` at all other times.

### Run it

```bash
./tools/write_config.py \
    --port /tmp/obdlink-mx \
    --arm \
    --session-after-sales \
    --expect-current 38 \
    --confirm-target 78 \
    --min-voltage 12.5
```

What it does, in order, and refuses to continue if any step disagrees:

1. configure the adapter (no session command, no reset),
2. read `ATRV` and compare with `--min-voltage`,
3. read the part number, compare with `259156244R`,
4. read `0x6C1C`, compare with `--expect-current`,
5. compute `target = current | 0x40`, compare with `--confirm-target`,
6. send **one** `10 C0` (only with `--session-after-sales`),
7. send **one** `2E 6C 1C 78`,
8. read `0x6C1C` once and compare with the target,
9. print and log every answer; exit non-zero on any deviation.

There is no retry, no rollback, no reset and no second session in the code.

### What the successful run looked like

```
identity : 62 F1 87 '259156244R'         16:45:55
config   : 0x38                          16:45:57
session  : 10C0 → 50 C0                  16:45:59
write    : 2E6C1C78 → 6E 6C 1C           16:46:01
readback : 0x78                          16:46:03
```

`TESTED`. Exit code 0.

### Exit codes

| Code | Meaning |
|---|---|
| 0 | written and read back |
| 2 | identity mismatch |
| 3 | current value or target mismatch |
| 4 | voltage below the floor |
| 5 | gate closed or arguments inconsistent |
| 6 | negative response (session or write) |
| 7 | no answer |
| 8 | read-back differs from the target |
| 9 | transport error |

## 5. Route B — manual with DDT4All (DOCUMENTED, not tested here)

Public guides for this activation use DDT4All with a Renault/DDT2000 database.
The description below is what those guides say; **this project did not execute
it**, so treat every step as unverified.

- Select the vehicle project, open the navigation unit, choose the **MFD v4.6**
  description, then the configuration screen.
- Select the **after-sales** session in the session dropdown (this is `10 C0`).
- Set *Android Auto feature* to *Present* — and, in most guides, *Mirrorlink
  feature* as well. Note that MirrorLink was already present on this vehicle.
- Enable **Expert Mode** and press *Write ECU config*.
- Some guides then perform an ECU reset and let the unit reboot.

Three cautions, all from the code of DDT4All rather than from opinion:

1. DDT4All sends `10 C0` **automatically** when an ECU is opened, and re-sends it
   after four seconds of silence as a keep-alive. Two session frames instead of
   one.
2. In **demo/editor mode** the write path produces log lines but sends nothing.
   One public report of a "seemingly unsuccessful write" is exactly this.
3. Guides that set *both* feature bits produce a different target value than this
   project used, and can also switch off MW/LW if those were on.

If you use DDT4All, verify with the read-only tool afterwards — do not trust the
application's own log.

## 6. Which route should you take

Use the tool if you can: it is small, it has one dependency, it enforces the
preconditions in code, and it sends exactly one frame. Use DDT4All if you need its
screen editor or if you are working on a unit whose description this project has
not covered — but then treat the read-only tool as your ground truth.

## 7. After the write

The unit does **not** refresh its menus immediately. It caches the vehicle
configuration locally and reloads it at startup or when the vehicle side signals a
finished end-of-line write. Restart the head unit (ignition off, wait, ignition on)
and see `07-verification.md`.
