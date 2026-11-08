# Smart 453 — Android Auto on the factory TomTom head unit

Documentation and small, auditable tools for reading and changing the configuration
of the TomTom-built head unit in a Smart 453, with a long-term interest in getting
CarPlay onto the same screen through an adapter.

This repository is the work of one vehicle owner on one car. It records what was
measured, what was changed, and what is still unknown. It is not a vendor
procedure, and it is not affiliated with TomTom, smart, Renault, Mercedes-Benz or
Google.

---

## Status of the project

| Area | State |
|---|---|
| Head unit identified, diagnostic interface documented | done, on the vehicle |
| Configuration byte understood and decoded | done |
| Android Auto activated (`0x38` → `0x78`) | **done on 2026-11-08**, written and read back |
| Android Auto entries visible in the head unit menu | observed after a restart |
| Android Auto projection with a phone over USB | **not tested** |
| CarPlay through a CarLinkit T-Box Lite S | **not tested** |
| Behaviour on other part numbers or software versions | unknown |

The difference between "configured", "visible" and "working" is the point of
[`docs/07-verification.md`](docs/07-verification.md). A menu entry is not a working
projection.

## What was actually changed

One byte, one bit, on data identifier `0x6C1C`:

```
before  0x38   0011 1000   MirrorLink, MW and LW enabled, Android Auto absent
mask    0x40   0100 0000   Android Auto only
after   0x78   0111 1000   nothing else moved
```

The write needed the head unit's after-sales diagnostic session (`10 C0`); in the
default session it was refused with `7F 2E 7F`. Read-back confirmed `0x78`. After a
restart the head unit shows the Android Auto entries.

**`0x78` is not a universal value.** The correct target is `current | 0x40`, where
`current` is what your own unit reports. The tool enforces exactly that.

## Start here

| If you want to… | Read |
|---|---|
| know whether your car is covered | [`docs/01-compatibility.md`](docs/01-compatibility.md) |
| buy the right adapter | [`docs/02-required-hardware.md`](docs/02-required-hardware.md) |
| install the tools | [`docs/03-software-installation.md`](docs/03-software-installation.md) |
| get a reliable connection | [`docs/04-obdlink-connection.md`](docs/04-obdlink-connection.md) |
| identify your head unit, read-only | [`docs/05-headunit-identification.md`](docs/05-headunit-identification.md) |
| understand the activation | [`docs/06-android-auto-activation.md`](docs/06-android-auto-activation.md) |
| verify a result | [`docs/07-verification.md`](docs/07-verification.md) |
| plan CarPlay | [`docs/08-carplay-adapter.md`](docs/08-carplay-adapter.md) |
| fix a problem | [`docs/troubleshooting.md`](docs/troubleshooting.md) |
| understand the risk | [`docs/recovery-and-risks.md`](docs/recovery-and-risks.md) |

## The tools

Two command line programs and a pure decoder. One runtime dependency: `pyserial`.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r tools/requirements.txt

# read-only: identity + configuration byte
./tools/read_config.py --port /tmp/obdlink-mx

# write: single frame, locked twice, refuses anything unexpected
cp config/aa_write.example.json config/aa_write.json   # then edit: enabled=true
./tools/write_config.py --port /tmp/obdlink-mx --arm --session-after-sales \
    --expect-current 38 --confirm-target 78 --min-voltage 12.5
```

`tools/write_config.py` verifies the part number, the current value, the supply
voltage and the target before it sends anything, sends exactly one frame, reads the
value back once, and never retries. It cannot clear the Android Auto bit again —
see `docs/recovery-and-risks.md` for why, and for how a restore is done instead.

Offline tests, no car required:

```bash
python -m unittest discover -s tests -v      # 33 tests
```

## Layout

```
docs/        the guide, chapter by chapter
tools/       read_config.py, write_config.py, ecu_config.py, obd_transport.py
tests/       mock head unit and the offline test suite
research/    the underlying investigation and the original result report
config/      example configuration (the real one is git-ignored)
```

`research/RESEARCH.md` holds the original investigation: the firmware analysis, the
projection architecture, the software gates and the bit-encoding derivation.
`research/results/ANDROID_AUTO_ACTIVATION_2026-11-08.md` is the full account of the
activation. Public sources are listed in [`REFERENCES.md`](REFERENCES.md).

## Evidence standard

Every factual statement is tagged:

| Tag | Meaning |
|---|---|
| **[LIVE]** / **TESTED** | performed on the vehicle, with logged answers |
| **[DOCUMENTED]** | described by a third party, not executed here |
| **[OFFLINE]** | derived from the vendor's published firmware image, no vehicle |
| **[PUBLIC]** | taken from a public document or repository |
| **[REPORTED]** | stated by the vehicle owner, not independently verified |
| **[OPEN]** / **NOT TESTED** | unknown or never attempted |

A claim without a tag is an open question.

## Safety

- Changing a configuration byte in a head unit is a modification of a
  safety-relevant system. It can end with a unit that no longer answers.
- There is **no verified recovery path** beyond writing the original value back
  over the same diagnostic channel, and that only works while the unit still
  answers.
- A stable external supply is advisable. A voltage dip during a write leaves the
  outcome undetermined.
- Nothing here is a substitute for the manufacturer's service information, and
  nothing here is a promise that any of it works on your car.

## License

Documentation: **CC BY 4.0** — see [`LICENSE`](LICENSE) and [`NOTICE.md`](NOTICE.md).
Code in `tools/` and `tests/`: **MIT** — see [`LICENSE-CODE`](LICENSE-CODE).

No vendor firmware, application, database or documentation is redistributed here.
Third-party material is cited in [`REFERENCES.md`](REFERENCES.md).
