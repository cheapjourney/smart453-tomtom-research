# 02 — Required hardware

## Minimum

| Part | Requirement | Why |
|---|---|---|
| Laptop | macOS, Linux or Windows with Python 3.9+ | runs the tools |
| OBD-II adapter | **OBDLink MX+** (STN2255 chip) or another STN-based adapter | this project was built and tested with it |
| Vehicle | Smart 453 with the TomTom MFD unit | see `01-compatibility.md` |

That is all that is strictly needed to **read** the configuration.

## About the adapter

The project used an **OBDLink MX+**, firmware `STN2255 v5.10.3`, which presents
itself as `ELM327 v1.4b` with STN extensions. Two properties matter:

1. **A configurable request timeout.** The head unit answers a diagnostic request
   after roughly 2 seconds. The adapter's factory default is 102 ms, and with it
   the answer is discarded before it arrives. The tools set a 2 s timeout
   explicitly (`STPTO 2000`) and disable adaptive timing (`ATAT0`).
2. **Classic Bluetooth SPP.** The MX+ is a Bluetooth Classic device, not BLE.
   macOS exposes SPP at the operating-system level; see `04-obdlink-connection.md`
   for the caveat that comes with it.

### Cheap ELM327 clones

Forum guides for this activation insist on a clone with a genuine **PIC18F25K80**
chip. That is a workaround for clones whose firmware mishandles multi-frame
responses or the `STPTO`/`STCFCPA` commands this project relies on. An STN-based
adapter (OBDLink, VLinker FS, Vgate) avoids the problem entirely and is what this
project recommends.

An adapter that cannot set a 2 s timeout will report `NO DATA` for every request.
That is a limitation of the adapter, not of the car.

## For the write step only

| Part | Requirement | Why |
|---|---|---|
| Stable supply | regulated 13.8 V, ≥ 20 A, or a workshop charger with a supply mode | a voltage dip during a write leaves the outcome undetermined |

The successful activation in this project was performed **without** an external
supply, on a fully charged battery at 12.2 V — with the risk accepted explicitly.
That is a data point, not a recommendation. See `recovery-and-risks.md`.

## Not required

- No special cable, no pin swap, no bench harness. The unit is reached through the
  normal OBD connector, pins 6 and 14.
- No second adapter, no CAN interface (SocketCAN, PEAK, Kvaser). A serial ELM/STN
  adapter is sufficient.
- No Windows machine. DDT4All, the tool most guides use, runs on Windows; the
  tools in this repository do not need it.

## What to avoid

- **BLE-only adapters.** They do not speak SPP and will not appear as a serial
  port.
- **Adapters that auto-detect the protocol and refuse to be pinned.** The tools
  set the protocol explicitly (`STP 33`, ISO 15765, 11-bit, 500 kbit/s).
- **A phone holding the Bluetooth connection.** See `troubleshooting.md`; this
  cost the project an afternoon.
