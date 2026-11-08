# End-to-end guide — from a blank Mac to a verified Android Auto activation

This is the whole job in one page: hardware, both repositories, the Bluetooth
bridge, the diagnostic tools, the activation and the verification. It is written
for someone who has never seen the project and has no access to the notes it grew
out of.

**Read the status column of every step.** Only some of them can be reproduced
without a car, and only some of them were ever verified on a vehicle.

| Legend | Meaning |
|---|---|
| **OFFLINE-VERIFIED** | executed for this guide on a fresh clone, no vehicle involved |
| **VEHICLE-VERIFIED** | performed on the reference vehicle on 2026-11-08, with logged answers |
| **MOCK-TESTED** | the software path is exercised only against the mock head unit in `tests/` |
| **HARDWARE** | needs the adapter and the car; not reproducible on a desk |
| **NOT TESTED** | never performed anywhere |

---

## Step 0 — What you need

| Item | Detail |
|---|---|
| Car | Smart 453 (W453) with the factory TomTom MFD head unit |
| Head unit part number | must read `259156244R` over diagnostics — see step 8 |
| Adapter | OBDLink MX+ (STN2255) or another STN-based ELM327-compatible device |
| Mac | macOS 10.13+, Intel or Apple Silicon; developed on 12.7.6 Intel |
| Toolchain | Xcode Command Line Tools (`xcode-select --install`), `brew`, `socat`, `python3` |
| Access | the OBD socket in the driver's footwell |

```bash
xcode-select -p || xcode-select --install
brew install socat
python3 --version        # 3.9 or newer
```

---

## Step 1 — Identify the hardware  ·  **OFFLINE-VERIFIED** (documented), **HARDWARE** (read)

The head unit identifies itself over diagnostics. Nothing about the car's
appearance tells you whether it is the right unit; the part number does.

Do not continue past step 8 unless the part number matches. Everything in this
repository is based on one unit.

Reference: [`docs/01-compatibility.md`](docs/01-compatibility.md).

---

## Step 2 — Clone both repositories  ·  **OFFLINE-VERIFIED**

```bash
mkdir -p ~/smart453 && cd ~/smart453
git clone https://github.com/cheapjourney/obdlink-macos-rfcomm-bridge.git
git clone https://github.com/cheapjourney/smart453-tomtom-research.git
```

Two repositories, on purpose:

- **obdlink-macos-rfcomm-bridge** — Bluetooth transport only. It moves bytes
  between the adapter and a local serial port. It does **not** filter or allowlist
  anything.
- **smart453-tomtom-research** — the diagnostic tools, the guide and the tests.
  This is where the read allowlist and the write locks live.

Neither repository needs anything from the other besides the PTY path.

---

## Step 3 — Build the Swift bridge  ·  **OFFLINE-VERIFIED**

```bash
cd ~/smart453/obdlink-macos-rfcomm-bridge
make
make test
```

Expected:

```
swiftc -O Sources/obdlink-rfcomm/main.swift -o build/obdlink-rfcomm
…
PASS  port released after close  [re-bound 56896]

9 passed, 0 failed
```

`make test` needs no adapter and no Bluetooth. If it fails, stop here — the
transport is not usable.

---

## Step 4 — Pair the adapter and make it exclusive  ·  **HARDWARE**

1. Ignition on. The adapter is powered from the OBD socket.
2. *System Settings → Bluetooth*, pair the OBDLink MX+. Some units only become
   visible while their pairing button is held — that is a security feature.
3. **Do not press that button later to "wake" an adapter that already worked.**
   It starts a new pairing and can invalidate the link key.
4. **Turn Bluetooth off on your phone, or forget the adapter there.** The MX+
   accepts one client. If a phone holds it, the Mac's connection attempt dies
   after about 15 seconds with a page timeout while the adapter still looks
   available. This is the most common failure in the whole procedure.

Find the adapter's address if you do not have it:

```bash
system_profiler SPBluetoothDataType | grep -A2 "OBDLink"
# Address: 00:04:3E:8A:DB:7C   → use 00-04-3E-8A-DB-7C below
```

---

## Step 5 — Start the bridge with the right PTY name  ·  **HARDWARE**

**The bridge defaults to `/tmp/obdlink`. This project uses `/tmp/obdlink-mx`.**
Pass the path explicitly, or every later command will point at a device that does
not exist:

```bash
cd ~/smart453/obdlink-macos-rfcomm-bridge
./scripts/start.sh --address 00-04-3E-8A-DB-7C --pty /tmp/obdlink-mx
```

Expected:

```
bridge ready
  tcp : 127.0.0.1:35100 (loopback only)
  pty : /tmp/obdlink-mx -> /dev/ttys004
```

Two failure signatures worth recognising:

| Message | Cause |
|---|---|
| `baseband connection failed` after ~15 s | adapter asleep, unpowered, or held by a phone |
| `error: bridge already running` | an earlier run is still up; stop it first |

Leave this terminal open for the whole session. Stop it at the end with the same
path named in the environment — `stop.sh` otherwise looks for its default and
leaves the link behind:

```bash
OBDLINK_PTY=/tmp/obdlink-mx ./scripts/stop.sh
```

`verify.sh` also takes the path from the environment, not from a flag:

```bash
OBDLINK_PTY=/tmp/obdlink-mx ./scripts/verify.sh --address 00-04-3E-8A-DB-7C
```

It sends one local `ATI`, which never reaches a vehicle bus, and exits 0 if the
adapter answered.

Reference: [`docs/04-obdlink-connection.md`](docs/04-obdlink-connection.md).

---

## Step 6 — Prove the adapter answers  ·  **HARDWARE**

Before any diagnostic request, confirm the transport with adapter-only queries.
Install the tools first (step 7) if you have not; `read_config.py` does this
automatically, but a manual check isolates the two layers.

The tools print what they see. If nothing answers, it is a bridge or adapter
problem, not a car problem — see `docs/troubleshooting.md` §1–§4.

---

## Step 7 — Install and test the diagnostic tools  ·  **OFFLINE-VERIFIED**

```bash
cd ~/smart453/smart453-tomtom-research
python3 -m venv .venv
source .venv/bin/activate
pip install -r tools/requirements.txt
python -m unittest discover -s tests -v
```

Expected:

```
Ran 36 tests in 12.3s
OK
```

The suite needs `socat` (step 0) and nothing else. It starts a mock head unit and
talks to it through a pseudo-terminal, so it exercises the same code path as the
real thing.

| Script | Purpose |
|---|---|
| `tools/read_config.py` | read-only: part number and configuration byte |
| `tools/write_config.py` | one write frame, locked twice, verifies everything first |
| `tools/ecu_config.py` | the bit table, the decoder, the read allowlist |
| `tools/obd_transport.py` | adapter command guard, ISO-TP reassembly |
| `tests/mock_ecu.py` | mock head unit with switchable failure modes |

---

## Step 8 — Confirm the ECU and the software version  ·  **HARDWARE**

```bash
cd ~/smart453/smart453-tomtom-research
./tools/read_config.py --port /tmp/obdlink-mx
```

Expected on the reference vehicle:

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

**Stop if the part number is not `259156244R`.** The tool exits 4 on a mismatch.
Other variants differ in software, and this project has no data for them.

The application version is shown on the head unit itself (*Settings → version
information*, field "Application"). The reference vehicle runs
`11.346.3206684-8060`; that is the only version on which the activation is
confirmed.

Reference: [`docs/05-headunit-identification.md`](docs/05-headunit-identification.md).

---

## Step 9 — Read and record the original value  ·  **HARDWARE**

```bash
./tools/read_config.py --port /tmp/obdlink-mx --json logs/before.json
```

Write the byte down **offline**, not only in that file. On the reference vehicle
it was `0x38`. That value is your only way back.

The configuration byte:

| DDT4All offset | conventional bit | mask | field |
|---|---|---|---|
| 0 | 7 | `0x80` | SPVR for iPhone |
| **1** | **6** | **`0x40`** | **Android Auto** |
| 2 | 5 | `0x20` | MirrorLink |
| 3 | 4 | `0x10` | MW activation |
| 4 | 3 | `0x08` | LW activation |
| 5 | 2 | `0x04` | SPVR for other phones |

`0x38` = MirrorLink + MW + LW. Adding Android Auto only is `0x38 | 0x40 = 0x78`.

**The target is computed, never copied:** `target = current | 0x40`. A unit that
reports a different value needs a different target; writing `0x78` there could
clear flags it needs.

---

## Step 10 — The activation  ·  **VEHICLE-VERIFIED** (procedure) · **MOCK-TESTED** (published tool)

### What was learned the hard way

In the default diagnostic session the write is refused:

```
2E 6C 1C 78  →  7F 2E 7F      serviceNotSupportedInActiveSession
```

`10 C0` is session type `0x40` with the `suppressPosRspMsgIndicationBit` set. After
it, the same write is accepted. Two consequences:

- a **missing** answer to `10 C0` proves nothing — it must be logged as
  *unconfirmed*, never as success;
- a **negative** answer always comes and is a hard stop.

This session requirement is confirmed for this unit at this software version. It
is **not** documented vendor behaviour and not a rule for every Smart 453.

### Run it

```bash
cp config/aa_write.example.json config/aa_write.json
# edit config/aa_write.json: "enabled": true     (the first of two switches)

./tools/write_config.py \
    --port /tmp/obdlink-mx \
    --arm \
    --session-after-sales \
    --expect-current 38 \
    --confirm-target 78 \
    --min-voltage 12.5
```

Before it sends anything the tool checks, in order: adapter configuration, supply
voltage, part number, current value, and that the target equals `current | 0x40`.
Then it sends **one** `10 C0` and **one** `2E 6C 1C 78`, reads the value back once,
and stops. There is no retry, no rollback, no reset.

Typical output:

```
session : no positive answer (suppress bit) - UNCONFIRMED
write   : 2E6C1C78
accepted: 6E 6C 1C
readback: 0x78
log: …/logs/write_20261108_164552.jsonl
```

`accepted` and `readback` are different facts. The first means the unit took the
frame; only the second means it stored it.

**Validation status of the published tool: MOCK-TESTED.** It has never been run on
a vehicle. The activation on 2026-11-08 was performed with the project's own tool
of that day, which speaks the same protocol in a less strict implementation.

Always set the gate back afterwards and stop the bridge:

```bash
# config/aa_write.json → "enabled": false
OBDLINK_PTY=/tmp/obdlink-mx ./scripts/stop.sh
```

Reference: [`docs/06-android-auto-activation.md`](docs/06-android-auto-activation.md).

---

## Step 11 — Judge the answer  ·  **HARDWARE**

| Observation | Meaning |
|---|---|
| `6E 6C 1C` then read-back `0x78` | stored; continue to step 12 |
| `7F 2E 7F` | session did not take effect; nothing changed |
| `7F 2E 22` / `31` / `33` | refused before execution; nothing changed |
| `NO DATA` | transport; re-read the value before doing anything else |
| read-back still `0x38` | accepted but not stored — do not silently retry |

Exit codes: `0` ok, `2` identity, `3` value, `4` voltage, `5` gate, `6` negative
response, `7` no answer, `8` read-back mismatch, `9` transport.

Reference: [`docs/07-verification.md`](docs/07-verification.md).

---

## Step 12 — Restart and look at the menu  ·  **VEHICLE-VERIFIED** (reported)

The head unit caches the vehicle configuration and reloads it at startup. Without
a restart the menu will not change, even with `0x78` stored.

1. Ignition off, wait ~30 s, ignition on.
2. Let the unit finish booting.
3. Open *Smartphone Screen*.

After the reference activation it showed Android Auto settings, an Android Auto
tutorial entry and the automatic-start setting, with MirrorLink still present.
That observation comes from the owner, not from an instrument.

If the menu does not change, re-read `0x6C1C` first: `0x78` with no menu means the
software did not reload; `0x38` means it was never stored.

---

## Step 13 — Android Auto over USB  ·  **NOT TESTED**

Never performed. This is the next thing to establish:

1. Connect an Android phone with the Android Auto app over USB.
2. Accept the projection offer, or set it to start automatically.
3. Check, separately: video, touch, audio, microphone, navigation, reconnect.

A menu entry proves configuration, not projection.

---

## Step 14 — CarPlay through a CarLinkit T-Box Lite S  ·  **NOT TESTED**

The unit contains no CarPlay stack. The plan is an adapter that presents itself to
the head unit as an Android Auto phone and talks CarPlay to the iPhone:

```
iPhone ─ wireless CarPlay ─▶ T-Box ─ USB/Android Auto ─▶ head unit
```

Nothing about this has been verified — not the recognition, not the pairing, not
touch, audio or microphone. Step 13 is its precondition: if a plain phone cannot
project, the box cannot either.

Reference: [`docs/08-carplay-adapter.md`](docs/08-carplay-adapter.md).

---

## Troubleshooting map

| Symptom | Go to |
|---|---|
| connection dies after ~15 s | `docs/troubleshooting.md` §1 (phone holds the adapter) |
| `/dev/cu.*` opens but returns nothing | `docs/troubleshooting.md` §3 — use the bridge |
| `NO DATA` on every request | `docs/troubleshooting.md` §4 (timeout) |
| wrong CAN speed | `docs/troubleshooting.md` §5 |
| `7F 2E 7F` | `docs/troubleshooting.md` §7 (session) |
| menu unchanged after a write | `docs/troubleshooting.md` §9 (cache, restart) |
| PTY missing after start | step 5 — `--pty /tmp/obdlink-mx` and `OBDLINK_PTY` |
| anything about recovery | `docs/recovery-and-risks.md` |

## What this guide cannot promise

1. It describes **one** part number (`259156244R`) at **one** software version
   (`11.346.3206684-8060`). Other variants may differ in the data identifier, the
   bit layout or the session requirement.
2. The published writer is **MOCK-TESTED**; only the tool of 2026-11-08 ran on a
   car.
3. Android Auto projection over USB and CarPlay are **NOT TESTED**.
4. There is **no verified recovery path** beyond writing the original value back
   over the same diagnostic channel, and that only works while the unit answers.
   `tools/write_config.py` cannot write the original value back — it only sets the
   Android Auto bit. A restore needs a tool that can send an arbitrary payload.

## Offline rehearsal

Everything that does not need a car can be rehearsed end to end: build the bridge,
run its self-test, install the tools, run the 36 tests, then point `read_config.py`
and `write_config.py` at a mock head unit behind a PTY at `/tmp/obdlink-mx`. That
is exactly how the commands in this guide were checked, including the write path
and the read-back, without touching a vehicle.
