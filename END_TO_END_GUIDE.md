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

- **obdlink-macos-rfcomm-bridge** — Bluetooth transport between the adapter and a
  local serial port. The legacy v0.1.0 TCP/PTY path used by this guide is ungated;
  the v0.2.0 secured Unix socket adds an adapter-only/vehicle-readonly gate, but
  that gate blocks the `2E` write this guide uses. It does **not** provide the
  read/write policy of this repository.
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
# Address: XX:XX:XX:XX:XX:XX
```

Put **your own** address into a shell variable once, and use the variable from
there on. Angle brackets are deliberately avoided: `--address <FOO>` is not a
placeholder in bash, it is a redirection, and the command fails in a confusing way.

```bash
ADDR="ADAPTER-ADDRESS"         # ← replace ADAPTER-ADDRESS with YOUR adapter's address
                             #   dashes (AA-BB-…) and colons both work
```

Keep the quotes. Every command below uses `"$ADDR"`.

---

## Step 5 — Verify, then start the bridge  ·  **HARDWARE**

**The bridge defaults to `/tmp/obdlink`. This project uses `/tmp/obdlink-mx`.**
Pass the path explicitly everywhere, or later commands will point at a device that
does not exist.

Two commands, **in this order**:

### 5a — one-shot verification first

`verify.sh` starts a bridge, sends one local `ATI`, checks the prompt, and stops the
bridge again when it exits (its `trap` calls `stop.sh`). It therefore needs the
adapter free and **no other bridge running**:

```bash
cd ~/smart453/obdlink-macos-rfcomm-bridge
OBDLINK_PTY=/tmp/obdlink-mx ./scripts/verify.sh --address "$ADDR"
```

- exit 0 — the adapter answered; the bridge has already been stopped again and the
  PTY link removed.
- `error: bridge already running` (exit 4) — something is still up; run
  `OBDLINK_PTY=/tmp/obdlink-mx ./scripts/stop.sh` and try again.

Running `verify.sh` *after* starting the bridge in 5b cannot work, because the
bridge refuses a second instance.

### 5b — then start the long-running bridge

```bash
cd ~/smart453/obdlink-macos-rfcomm-bridge
./scripts/start.sh --address "$ADDR" --pty /tmp/obdlink-mx
```

Expected:

```
bridge ready
  tcp : 127.0.0.1:35100 (loopback only)
  pty : /tmp/obdlink-mx -> /dev/ttys004
```

Leave this terminal open for the whole session.

Two failure signatures worth recognising:

| Message | Cause |
|---|---|
| `baseband connection failed` after ~15 s | adapter asleep, unpowered, or held by a phone |
| `error: bridge already running` | an earlier run is still up; stop it first |

### 5c — stop it at the end, from the bridge directory

`stop.sh` reads the PTY path from the environment, not from a flag, and it looks for
its own scripts relative to the current directory. Run it **inside the bridge
repository** — or call it by absolute path — and name the path:

```bash
cd ~/smart453/obdlink-macos-rfcomm-bridge
OBDLINK_PTY=/tmp/obdlink-mx ./scripts/stop.sh
# bridge stopped
```

Equivalently, from anywhere:

```bash
OBDLINK_PTY=/tmp/obdlink-mx ~/smart453/obdlink-macos-rfcomm-bridge/scripts/stop.sh
```

Without `OBDLINK_PTY` the script looks for `/tmp/obdlink` and leaves
`/tmp/obdlink-mx` behind. The pid files still stop the processes, but the stale
symlink survives and confuses the next start.

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
cd ~/smart453/smart453-tomtom-research
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
cd ~/smart453/smart453-tomtom-research
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
# 1) lock the tool again
#    ~/smart453/smart453-tomtom-research/config/aa_write.json → "enabled": false

# 2) stop the bridge — its script lives in the bridge repository
cd ~/smart453/obdlink-macos-rfcomm-bridge
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

---

## Appendix — rehearse the whole thing without a car

Everything except steps 4, 5b and 8–14 can be exercised on a desk. This is how the
commands above were checked.

**1. Bridge, offline part**

```bash
cd ~/smart453/obdlink-macos-rfcomm-bridge
make && make test          # 9 passed, 0 failed
```

Starting the bridge without a paired adapter fails cleanly, and leaves nothing
behind — worth seeing once so you recognise it later:

```bash
cd ~/smart453/obdlink-macos-rfcomm-bridge
# replace ADAPTER-ADDRESS with a deliberately non-existent address
ADDR="ADAPTER-ADDRESS"
./scripts/start.sh --address "$ADDR" --pty /tmp/obdlink-mx
# error: bridge exited during startup:
# device: ADAPTER-ADDRESS paired=false
# error: baseband connection failed - is the device awake and in range?
# exit code 5, no pidfile left, no /tmp/obdlink-mx
```

`verify.sh` behaves the same way and exits 1; its cleanup runs regardless:

```bash
cd ~/smart453/obdlink-macos-rfcomm-bridge
ADDR="ADAPTER-ADDRESS"
OBDLINK_PTY=/tmp/obdlink-mx ./scripts/verify.sh --address "$ADDR"
# RESULT: FAIL (bridge did not start)      exit code 1
OBDLINK_PTY=/tmp/obdlink-mx ./scripts/stop.sh
# bridge was not running
```

**2. Tools, offline part**

```bash
cd ~/smart453/smart453-tomtom-research
python3 -m venv .venv && source .venv/bin/activate
pip install -r tools/requirements.txt
python -m unittest discover -s tests -v     # 36 tests, OK
```

**3. The diagnostic sequence against a mock head unit**

The mock in `tests/mock_ecu.py` speaks the adapter protocol. Put it behind a PTY at
the same path the real bridge uses, and the tools cannot tell the difference:

```bash
cd ~/smart453/smart453-tomtom-research
# terminal A: mock ECU on 127.0.0.1:35999
python3 - 35999 <<'PY'
import sys, time, socket, threading
sys.path.insert(0, "tests")
from mock_ecu import MockEcu
m = MockEcu("positive"); m._srv.close()
m._srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
m._srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
m._srv.bind(("127.0.0.1", 35999)); m._srv.listen(1)
threading.Thread(target=m._run, daemon=True).start()
while True: time.sleep(1)
PY

# terminal B: PTY at the documented path
socat "PTY,link=/tmp/obdlink-mx,raw,echo=0" TCP:127.0.0.1:35999

# terminal C
./tools/read_config.py --port /tmp/obdlink-mx
#   identity … '259156244R'   config 0x38 … Android Auto: NOT PRESENT

echo '{"enabled": true}' > /tmp/gate.json
./tools/write_config.py --port /tmp/obdlink-mx --gate /tmp/gate.json \
    --log /tmp/write.jsonl --arm --session-after-sales \
    --expect-current 38 --confirm-target 78 --min-voltage 12.5
#   session : no positive answer (suppress bit) - UNCONFIRMED
#   write   : 2E6C1C78
#   accepted: 6E 6C 1C
#   readback: 0x78

./tools/read_config.py --port /tmp/obdlink-mx | head -3
#   config  : 0x78 … Android Auto feature Present

./tools/write_config.py --port /tmp/obdlink-mx --gate /tmp/gate.json \
    --log /tmp/write2.jsonl --arm --session-after-sales \
    --expect-current 38 --confirm-target 78 --min-voltage 12.5
#   ABORT[3]: current 0x78 != expected 0x38      exit code 3
```

Clean up:

```bash
pkill -f "socat PTY,link=/tmp/obdlink-mx"
rm -f /tmp/obdlink-mx /tmp/gate.json /tmp/write.jsonl /tmp/write2.jsonl
```

The last line is the point of the rehearsal: a second run is refused because the
value is no longer the expected one. Nothing here replaces step 8 — the mock
answers with values this project put into it, which proves the code path, not the
car.
