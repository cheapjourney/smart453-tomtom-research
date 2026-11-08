# Recovery and risks

Read this before writing anything. It is short on comfort and long on limits.

## What a write can and cannot break

The write changes **one configuration byte** in the head unit. It does not flash
firmware, does not touch the engine, braking or steering controllers, and does not
change the vehicle's immobiliser data.

What it can do:

- leave the head unit with a feature set it does not expect (a wrong byte can clear
  MW/LW or SPVR flags that were set),
- leave the unit in a state where the phone-projection menu behaves oddly,
- in the worst case, leave the unit refusing diagnostic communication, at which
  point the only channel you had is gone.

## The recovery value

For the research vehicle the value before the write was:

```
0x38
```

That is the value that would restore it. **Write it down somewhere offline**, not
only in the tool's log on the laptop you are using.

The restore frame is the same service with the original value:

```
2E 6C 1C 38
```

Two honest caveats:

1. **`tools/write_config.py` cannot perform the restore.** It is deliberately
   single-purpose: it computes `target = current | 0x40` and refuses any other
   value, so it will not clear the bit again. A restore has to be done with DDT4All
   (manual route, `06-android-auto-activation.md`) or another tool that can send an
   arbitrary payload. That is a design choice, not an oversight: a tool that can
   write both directions is a tool that can be misused to clear flags by accident.
2. **It only works while the unit still answers.** If the head unit stops
   responding to diagnostics, nothing in this repository helps. There is no
   documented service mode, no recovery image in the analysed material, and no
   independent access path.

## What "unrecoverable" would look like

- No answer to `22 F1 87` after an ignition cycle.
- The unit boots but the diagnostic address is silent.
- No response on the bus to any addressed request.

In that case: stop. Do not battery-disconnect as a "reset", do not press anything,
do not send further frames. A workshop with a manufacturer tool is the next step,
and that may not be enough either.

## Power

A voltage dip during a write leaves the outcome undetermined: the unit may have
taken the value, may not have, and there is no way to tell except by reading it
back.

| Situation | Assessment |
|---|---|
| Regulated 13.8 V supply, ≥ 20 A | recommended for any further write |
| Charged battery, engine off, ~12.2 V | worked once in this project; not a recommendation |
| Below ~11.8 V, or voltage moving | stop |

The successful activation here ran at 12.2 V on a fully charged battery, with the
risk accepted explicitly by the owner. Treat it as one data point.

## Session state

The after-sales session is not explicitly closed afterwards — that would be another
session command, and this project does not send one. The unit returns to its
default session on its own timeout or on the next ignition cycle.

## Before you write — checklist

- [ ] Part number read and matches `259156244R`
- [ ] Configuration byte read; you know its exact value
- [ ] Target computed as `current | 0x40` and confirmed
- [ ] Original value recorded offline
- [ ] Supply stable, voltage measured
- [ ] Exactly one write decided; no "let's try again" plan
- [ ] Time and place where you can stop and think if it goes wrong

## If it goes wrong

1. Read `0x6C1C`. Still answering? Good — you have options.
2. Value is the target but the UI is wrong: restart the unit, check again.
3. Value is unchanged after a positive write answer: the unit accepted but did not
   store it. Do not immediately retry; understand why first.
4. Unit silent: stop, as above.

## What this project does not claim

- That the write is safe on every unit.
- That the value `0x78` is correct anywhere else.
- That a recovery always exists.
- That Android Auto projection works — only that the configuration and the menu do.
