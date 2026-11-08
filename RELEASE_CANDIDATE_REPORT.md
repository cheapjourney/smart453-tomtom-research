# Release candidate report — 2026-11-08

Independent check before the repository could be made public again. The repository
stayed **private** throughout; nothing was pushed to a public remote.

| Field | Result |
|---|---|
| FRESH_CLONE_TEST | **PASS** — clone from GitHub, own venv, only `pyserial`, 36/36 tests |
| SESSION_GUARD_TEST | **PASS** — see §2; exact bytes verified on the mock |
| MOCK_TESTS | **PASS** — 36 tests, 0 failures |
| DIFFERENCES_FROM_LIVE_TOOL | listed in §4; protocol identical, CLI and exit-code mapping differ |
| DOCUMENTATION_AUDIT | **PASS** after two fixes (§5) |
| PRIVACY_AUDIT | **PASS** (§6) |
| READY_FOR_PUBLICATION | **YES from the engineering side** — release awaits the owner's explicit approval |

---

## 1. Method

Everything below ran from a fresh clone in `/tmp/rc_clone`, created with
`gh repo clone` from the private remote — not from the working copy. The clone got
its own virtual environment and its own `pip install`. The private research project
and its Python environment were not used at any point.

Commit under test: `03de699` (plus the documentation fixes in §5, committed after
this report was written; the final commit is the one on `main`).

## 2. Session guard

The transport now takes an explicit set of permitted services per call. The default
is read-only (`21`, `22`). The writer has to ask for `10` and `2E` explicitly.

**Refusal test** (`test_read_answer_refuses_non_read_services`): with the default
allowlist, each of these raises before anything is written to the port —
`10C0`, `1081`, `1101`, `2E6C1C78`, `2701`, `31 01`, `14 FF FF`. The fake port's
`write()` raises if it is touched, and it never is.

**Positive path** (`test_read_answer_allows_only_asked_service`): with
`allow_services={"10"}` the call writes exactly `b"10C0\r"`; with `{"2E"}` exactly
`b"2E6C1C78\r"`.

**What actually reaches the ECU** (`test_exact_bytes_on_the_wire`): the mock records
every command it receives. Filtering that list to diagnostic services yields
exactly:

```
["10C0", "2E6C1C78"]
```

— one session frame, one write frame, in that order, nothing else. Across all
scenarios the suite additionally asserts that no command starting with `10` other
than `10C0` ever appears, and that no `11`, `12`, `14` or `27` appears at all.

**Session answers handled**

| Answer to `10 C0` | Behaviour |
|---|---|
| `50 C0` (or `50 40`) | confirmed, proceed |
| silence | logged as `UNCONFIRMED`, proceed — never counted as success |
| `7F 10 xx` | abort, no write |
| `50 81` (wrong session type) | abort, no write |

## 3. Offline suite

```
Ran 36 tests in 12.3s
OK
```

Covered: decoder and bit masks (8), allowlist and transport guard (7), writer
end-to-end against a mock head unit (21) — positive path, second run refused, wrong
identity, wrong current value, low voltage, silent identity, `7F 2E 22`,
`7F 2E 12`, `7F 2E 7F`, silent read-back, disconnect, read-back mismatch, session
confirmed / silent / rejected / wrong type, closed gate, inconsistent target.

## 4. Differences from the tool that performed the activation

The tool that wrote the vehicle on 2026-11-08 lives in the private project. The
published one was compared against it.

### 4.1 Identical

| Area | Result |
|---|---|
| Adapter command sequence | identical, all 13 commands in the same order |
| Session frame | `10C0`, exactly once, only with `--session-after-sales` |
| Write frame | `2E 6C 1C 78`, exactly once, computed as `current \| 0x40` |
| Read-back | one `22 6C 1C` after the write, compared with the target |
| ISO-TP reassembly | byte-identical output on 6 vectors, including the recorded multi-frame identity answer and a `7F` answer |
| Pre-write checks | part number, current value, voltage, target — same order, same conclusions |
| No retry / no reset / no rollback | identical |

### 4.2 Different

| Area | Live tool (2026-11-08) | Published tool | Effect |
|---|---|---|---|
| Service guard | none beyond fixed payloads | explicit `allow_services` per call, read-only default | new hardening; no behaviour change on the happy path |
| `--expect-current` / `--confirm-target` | defaulted to `38` / `78` | mandatory | a wrong-by-assumption run cannot happen silently |
| Gate file | fixed `config/aa_write.json` in the project | `--gate`, `AA_WRITE_GATE`, else `config/aa_write.json` | no behaviour change |
| Logging | `--label`, file name derived | `--log`, path given | no behaviour change |
| Log hash | over the whole run record | over the step list | cosmetic |
| Exit code: identity negative response | 6 | **2** | code now means "identity stage" |
| Exit code: config read negative response | 6 | **3** | "value stage" |
| Exit code: unexpected write answer | 9 | **7** | "no usable answer" |
| Exit code: read-back negative / unexpected | 6 / 9 | **8** / **8** | "read-back stage" |

The exit-code remapping is the only functional difference a caller can notice. It
groups failures by the stage they occurred in instead of by transport class.
Whether that is an improvement is arguable; it is documented here so nobody
compares two logs and concludes the tools behave differently.

### 4.3 Validation status

**The published tool has never been run against a vehicle.** It is validated
against a mock head unit only. The tool that wrote the car was validated on the car.
Same protocol, same frames, same checks — but that is an argument, not evidence.
The documentation says so in `docs/06-android-auto-activation.md`.

## 5. Documentation audit

Checked from the point of view of a reader who has never seen the project.

| Requirement | Where | State |
|---|---|---|
| Which units are supported | `docs/01-compatibility.md` | part number, software version, variants that differ, "stop if not `259156244R`" |
| Adapter and software needed | `docs/02`, `docs/03` | OBDLink MX+, STN vs. clone caveat, Python 3.9+, one dependency |
| Dependency on the separate RFCOMM bridge | `docs/03`, `docs/04` | named, linked, explained; nothing copied |
| iPhone can block the Bluetooth link | `docs/04` ("one-device rule"), `docs/troubleshooting.md` #1 | symptom, cause, fix |
| Only the tested route may be called verified | `docs/06` | route A `TESTED`, route B `DOCUMENTED — not executed by this project`; no other claim of verification anywhere |
| Android Auto over USB and CarPlay | `docs/07`, `docs/08`, `README.md` | both `NOT TESTED`, with the checks that would settle them |
| Warnings and recovery limits | `README.md`, `docs/recovery-and-risks.md` | no verified recovery path; the tool cannot clear the bit again; supply requirements |

Two issues found and fixed during this audit:

1. **Broken relative link** in `research/RESEARCH.md` (§9) — it still pointed at
   `RESULTS/…` after the move to `research/results/`. Fixed, and every relative
   link in the repository now resolves.
2. **Ambiguous wording** — `docs/troubleshooting.md` used "confirmed" for causes,
   which reads like a feature verification. Changed to "cause confirmed" / "cause
   suspected"; `docs/01` heading "Confirmed on this project" became "Measured on
   this project".

## 6. Privacy audit

Run over every tracked file after the fixes:

| Check | Result |
|---|---|
| Account name, home paths, `/Users/…` in text or code | 0 |
| RFC 1918 addresses | 0 |
| MAC addresses, adapter serial numbers | 0 |
| VIN patterns | 0 |
| Credentials, tokens, keys | 0 (4 raw hits: one audit table row, three occurrences of the code's `ADAPTER_TOKENS` variable) |
| Absolute paths in `tools/` and `tests/` | 0 |
| Binaries, images, archives | 0 |
| Vendor artefacts (`TOMTOM.000`, `.apk`, `.odex`, `ecu.zip`) | only named inside the audit's exclusion table |

## 7. Remaining gaps, stated plainly

1. The published writer is **not hardware-validated**. Only the private tool was.
2. Android Auto projection over USB is **not tested**; only the configuration and
   the menu entries are.
3. CarPlay is **not tested** in any form.
4. Restore is possible only by writing the original byte back with a different
   tool; `write_config.py` cannot clear the bit.
5. Behaviour on other part numbers or software versions is unknown.

## 8. Verdict

The repository is coherent, its claims are tagged, its tests pass from a clean
clone, and no personal or vendor data is present.

**READY_FOR_PUBLICATION = YES**, pending the owner's explicit decision. The
repository remains private until that decision is made.

---

## 9. Addendum before publication — labelling of the published code

Raised by the owner during the release review: the published scripts must be named
**MOCK-TESTED**, not "tested on the vehicle". The report above already said the
published writer was never run on a car, but one table in `docs/06` still labelled
`tools/write_config.py` as *TESTED on the research vehicle*. That was wrong and has
been corrected:

| Where | Change |
|---|---|
| `docs/06-android-auto-activation.md` | status table split into three rows: DDT4All route *DOCUMENTED*, the activation *TESTED*, the published tool *MOCK-TESTED*; plus a paragraph explaining that the tool of the day and the published tool are the same protocol in a stricter implementation |
| `docs/01-compatibility.md`, `README.md` | new evidence tag **MOCK-TESTED** defined |
| `docs/07-verification.md` | read-back marked TESTED for 2026-11-08 with the tool of that day; the published reader *MOCK-TESTED* |
| `tools/read_config.py`, `tools/write_config.py` | docstring states mock-tested only, never run on a vehicle |

Nothing else changed. The test suite still reports 36/36 after the edit.
