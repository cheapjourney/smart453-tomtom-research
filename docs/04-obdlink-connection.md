# 04 — Connecting to the adapter

This is the step where most attempts fail, usually for reasons that have nothing
to do with the car.

## Pair the adapter once, by hand

Pair the OBDLink MX+ in the operating system's Bluetooth settings, as you would
pair headphones. Some adapters only become visible after their pairing button is
pressed and held; that is a security feature, not a defect.

**Do not press that button later to "wake" an adapter that already worked.**
Pressing it starts a new pairing and can replace the link key the host already
holds. The host then still believes it is paired while the adapter refuses the old
key — a failure that looks like a hardware fault.

## The macOS serial-port trap

On this project's machine, the adapter appeared as a normal serial device
(`/dev/cu.OBDLink…`). It worked for the first session and then stopped:

- the port opened instantly, without error,
- every read returned zero bytes,
- the adapter itself kept answering over Bluetooth,
- the system log showed no attempt to establish a link on that port.

macOS keeps a serial-port object per device that can stop initiating connections
after the first session while the adapter stays healthy. The workaround is not a
driver and not a re-pair: open the RFCOMM channel directly and expose it as a
local serial device.

That is what the companion project does:

<https://github.com/cheapjourney/obdlink-macos-rfcomm-bridge>

It opens RFCOMM channel 1 to the adapter, publishes a loopback TCP port, and
bridges that to a pseudo-terminal. On the legacy v0.1.0 path it moves Bluetooth
bytes without filtering diagnostic commands; the v0.2.0 secured Unix-socket mode
adds an adapter-only/vehicle-readonly gate, but that gate does not permit write
frames. The commands below are the **legacy TCP/PTY path** used by this project's
activation workflow.

```bash
ADDR="<adapter-address>"      # ← replace with YOUR adapter's address
./scripts/start.sh --address "$ADDR" --pty /tmp/obdlink-mx
#   tcp : 127.0.0.1:35100 (loopback only)
#   pty : /tmp/obdlink-mx -> /dev/ttys004

OBDLINK_PTY=/tmp/obdlink-mx ./scripts/stop.sh     # when you are done
```

**Naming:** the bridge's default PTY is `/tmp/obdlink`; this project uses
`/tmp/obdlink-mx` in every command. Always pass `--pty /tmp/obdlink-mx` to
`start.sh` and `OBDLINK_PTY=/tmp/obdlink-mx` to `stop.sh` and `verify.sh`, or the
two sides will disagree about the path.

From the point of view of the tools in this repository it is simply a serial
device:

```
adapter  →  RFCOMM  →  bridge  →  /tmp/obdlink-mx
```

The bridge binds `127.0.0.1` only. Never expose it on a network interface.

## Before you trust the link

Two adapter-only queries prove the path without touching the car's ECUs:

```
ATI     → ELM327 v1.4b            (adapter family)
STDI    → OBDLink MX+ r3.1.3      (actual hardware, more useful than ATI)
ATRV    → 12.6V                   (supply voltage)
```

If `ATI` answers but `ATRV` does not, the link is marginal. If nothing answers at
all, see `troubleshooting.md` — in this project that always meant the adapter was
held by another device, asleep, or the pairing had gone stale.

## The one-device rule

An OBDLink accepts **one** Bluetooth client at a time. If a phone is connected to
it — typically through an OBD app that reconnects in the background — the laptop's
connection attempt fails with a *page timeout* after about 15 seconds, even though
the adapter is visible and reports a signal strength.

This is the single most common cause of "the adapter stopped working" in this
project. Turn Bluetooth off on the phone, or forget the adapter there, before
connecting from the laptop.

## Timeouts and protocol

The tools configure the link themselves:

| Setting | Value | Why |
|---|---|---|
| Protocol | `STP 33` (ISO 15765-4, 11-bit, 500 kbit/s) | the head unit speaks 11-bit CAN at 500 kbit/s |
| Header / filter | `ATSH 747` / `ATCRA 767` | request and response identifiers |
| Flow control | `STCFCPA 747, 767` | the response ID is not request+8, so the adapter's automatic filter would miss the answer |
| Adapter timeout | `STPTO 2000` with `ATAT0` | the unit answers after ~2 s; the 102 ms default drops the reply |
| Auto formatting | `ATCAF1` | the adapter builds the ISO-TP length byte, so requests are sent as bare hex |

With `ATCAF1` the payload you send is the UDS message only, e.g. `22F187`. Adding
a length byte yourself double-frames the request and the unit rejects it as
malformed.
