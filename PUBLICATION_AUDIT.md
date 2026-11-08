# Publication audit

Date: 2026-11-07. Scope: the documentation files in this directory.

**Status: published.** Repository `cheapjourney/smart453-tomtom-research` is public.
Initial commit `902f1b806ee6591df6aea78597d380bd7f64f0da` on `main`. This audit was
performed before that commit and re-run after the licence restructuring described in
section 7; the results below reflect the published content.

This audit exists because the material is derived from a vendor's firmware and from
a real vehicle. The default is to leave something out — a claim that cannot be
sourced, a value that identifies a person, a snippet that is someone else's code.

---

## 1. What was deliberately excluded

| Excluded | From where | Why |
|---|---|---|
| Firmware image (`TOMTOM.000`) and the update package | project working copy | vendor copyright; redistributing it is not defensible regardless of how it was obtained |
| Extracted applications, DEX/ODEX files, file-system tree | project working copy | verbatim vendor code and resources |
| Diagnostic request catalogue derived from a third-party DB | project working copy | licence of the vendor-specific database is unclear |
| DDT4All database files | third-party download | unclear licence; not ours to relicense |
| All capture files, `.raw.log`, CSV/JSON statistics | project working copy | contain vehicle traffic; one of them is a fingerprint of the car |
| VIN, part-number scans, calibration/software record bytes | vehicle reads | identifies the specific car; also the most sensitive data we hold |
| Bluetooth MAC, adapter serial number, device node names | host | identifies the owner's hardware |
| Local paths, hostnames, IP addresses, SSH details | host | identifies the owner's machine and network |
| Screenshots | none taken | unwverified provenance and third-party content |
| Any write procedure (coding, adaptation, retrofit steps) | project work | publishing a ready-to-run modification is a safety and legal risk, not research |
| Class names, package internals, decompiled sources | firmware analysis | would be a code disclosure; the findings are stated functionally instead |
| Raw request hex strings (`22 F1 xx`, `21 8x`, adapter setup commands) | project scripts | an exact recipe to talk to the unit; the findings are described without a copy-paste recipe |

The underlying working files remain untouched in the private project; nothing was
deleted there.

## 2. Checks performed

Run against the documentation files in this directory:

| Check | Method | Result |
|---|---|---|
| Personal name / home paths | regex for the account name and absolute home prefixes | clean |
| Private IP ranges | regex for RFC 1918 ranges | clean |
| MAC addresses | regex for six hex octets | clean |
| VIN / chassis identifiers | regex for the three common WMI prefixes and `VIN:` | clean |
| Adapter serial in device names | regex for the adapter family name followed by digits | clean |
| Credentials | regex for common credential words | clean |
| Raw diagnostic hex / adapter setup | regex for the project's request payloads and adapter headers | clean |
| Vendor code fragments | regex for Dalvik/Java/C declaration syntax and vendor package prefixes | clean |
| Embedded blobs | regex for long base64 lines | clean |
| File types | `file` | six UTF-8 text files, no binaries |
| URLs | extraction | 9 unique URLs, all in `REFERENCES.md` only |

## 3. Legal risk assessment

### 3.1 Firmware and copyright

No firmware is redistributed and no code is reproduced. What is published is
**factual description**: the unit runs Android 2.2, contains two projection stacks,
has three software gates. Facts about a product are generally not protected by
copyright, though the line between "description" and "derived work" can be argued.
Risk: **low**, because nothing is copied and the descriptions are coarse.

If the vendor's EULA forbids reverse engineering outright, that is a contract
question between the owner of the device and the vendor, not a copyright claim
against a third-party reader — but it is a real risk for the person who performed
the analysis. This document therefore does not describe *how* the image was
obtained beyond "publicly downloadable from the vendor's update host".

### 3.2 Anti-circumvention

No protection measure was circumvented: the update signature was verified, not
broken; no encryption was removed; no authentication was bypassed. The text
explicitly states that the three gates were not defeated. Risk: **low**. Publishing
"we did not defeat these" is a different act from publishing how to defeat them.

### 3.3 Trade secrets

Architectural statements (two stacks, add-on permission model, factory device
class) are the kind of information a manufacturer could consider confidential. They
are published at a level that is already visible to anyone who owns the device or
reads its update package. Risk: **low to moderate**, and unavoidable if the research
is to be published at all.

### 3.4 Trademarks

"TomTom", "smart", "MirrorLink" and "Android Auto" appear descriptively.
`README.md` contains an explicit non-affiliation disclaimer. Risk: **low**.

### 3.5 Third-party licenses

- LIVI, PlayPort: GPL-3.0 — cited, no code used.
- **CatPlay: no license file at all.** Citation is fine; reuse would not be. No code,
  no excerpts, no derivative content from it.
- DDT4All and its databases: structure described in the abstract; no data files.
- goingelectric wiki: method reference only, no text copied.
Risk: **low**, because nothing is redistributed.

### 3.6 The bit-encoding example

`0x38 | 0x40 = 0x78` is arithmetic, not a procedure. It carries no ECU identity, no
byte offset and no write instruction, and the text says explicitly that the write
was never performed and the effect is unknown. Risk: **low to moderate** — somebody
could still read it as a hint. Accepted, with the disclaimers in place.

## 4. Safety risk assessment

The document intentionally contains no coding path. What remains is the risk that a
reader reconstructs one from the architecture description. That risk is inherent to
publishing any reverse-engineering research on a vehicle and is mitigated by:

- no request recipes,
- no register or byte locations,
- an explicit statement that no modification was attempted,
- a scope section in `README.md` naming safety and driver-distraction concerns.

**Residual risk: moderate.** This is research about a safety-relevant system.

## 5. Decisions taken

| # | Decision | Outcome |
|---|---|---|
| 1 | Text licence | **CC BY 4.0**; unmodified legal code in `LICENSE`, scope and third-party carve-out in `NOTICE.md` |
| 2 | Vendor firmware link | **removed** from `REFERENCES.md`; replaced with a reference to the manufacturer's official support pages, no URL given |
| 3 | Third-party rights | stated in `NOTICE.md` and `README.md`: no rights in vendor firmware, software, databases or trademarks are granted |
| 4 | Naming third-party vendors | projection stacks named by technology only (MirrorLink, Android Auto), vendor name omitted |
| 5 | EULA conflict | only the device owner can answer; if one applies, publish the abstract results only |

## 6. Re-audit after the changes

| Check | Result |
|---|---|
| Privacy patterns (name, paths, RFC 1918, MAC, VIN, adapter serial, credentials) | clean |
| Raw diagnostic hex / adapter setup strings | clean |
| Vendor code fragments, class names, package names, `.apk`/`.odex`/`.smali` references | clean |
| Embedded blobs / binaries | clean — six UTF-8 text files |
| Evidence tags present and distributed | LIVE 20, OFFLINE 26, PUBLIC 9, REPORTED 7, OPEN 11 |
| Firmware download link | absent |
| Android Auto activation claim | none found |
| `0x78` framed as calculated and untested | confirmed, every occurrence |
| Reference URLs | 9 of 9 reachable (HTTP 200) |

## 7. Verdict

The material is **publishable**: no vendor code, no vehicle-identifying data, no
credentials, no write procedure, no third-party asset, and an explicit licence scope
that carves out every third party.

Two residual risks remain and are inherent to the subject matter:

1. the architecture description itself (two projection stacks, permission model,
   factory device class) — unavoidable for a research write-up;
2. the bit-encoding example — arithmetic only, no location, no ECU, no offset,
   explicitly never applied.

Both are documented here rather than hidden.

**Publication state:** published on 2026-11-07 as `cheapjourney/smart453-tomtom-research`
(public), initial commit `902f1b806ee6591df6aea78597d380bd7f64f0da`. The licence
layout was restructured afterwards — the scope notice moved from `LICENSE` into
`NOTICE.md` so that GitHub can recognise the licence automatically — and the audit
was re-run on the result. Section 2 and section 6 reflect that re-run.

## 8. Post-publication check

| Item | Result |
|---|---|
| Repository visibility | public |
| Files published | six text files, matching the audited set |
| Branch / commit | `main` at the audited commit |
| Licence recognition | after moving the scope notice to `NOTICE.md`, GitHub reports `CC-BY-4.0` |
| Third-party rights notice | present in `NOTICE.md` and linked from `README.md` |

---

## 9. Update 2026-11-08 — activation disclosure

This section records a deliberate change of decision and the re-audit that
accompanied it. The earlier sections are left as they were; where they conflict
with this one, this one applies.

### 9.1 What changed

On 2026-11-08 the vehicle's owner performed and confirmed an Android Auto
activation on the research vehicle. The owner decided that the confirmed case
should be published, including the diagnostic frames that produced it. That
overrides two entries in the section 1 exclusion table:

| Previously excluded | Now |
|---|---|
| "Any write procedure (coding, adaptation, retrofit steps)" | **Published as a documented case**, not as a guide: `RESULTS/ANDROID_AUTO_ACTIVATION_2026-11-08.md` and `RESEARCH.md` §9 |
| "Raw request hex strings" | **Published for this one data identifier**: the session frame, the write frame and the three answers |

The reasoning is the owner's: a confirmed result with its exact protocol values is
the finding, and withholding the frames would leave a claim nobody can check.

Everything else in section 1 still stands. Still excluded: the vendor firmware and
update package, extracted applications and file-system content, the third-party
configuration database, all capture files and raw logs, VIN and identification
record bytes, adapter serial, Bluetooth address, hostnames, addresses and local
paths.

### 9.2 What was published, exactly

- session frame `10 C0` and its answer `50 C0`,
- write frame `2E 6C 1C 78` and its answer `6E 6C 1C`,
- read-back `62 6C 1C 78`, and the preceding value `0x38`,
- the rejected first attempt: `2E 6C 1C 78` → `7F 2E 7F`,
- the bit table that turns `0x38` into `0x78` (offset 1, mask `0x40`).

Not published: timestamps that would tie the vehicle to a place, log files, adapter
setup sequences, and any second data identifier.

### 9.3 Images

The owner took two photographs of the head unit's screen after the activation.
They are **not** included: they were not available in the working copy used for this
publication, and their privacy status has not been checked. The user-interface
result is documented as a text observation tagged **[REPORTED]** instead. No image
was recreated or substituted.

### 9.4 Re-run of the privacy checks

| Check | Result |
|---|---|
| Personal name / home paths | clean |
| RFC 1918 addresses | clean |
| MAC addresses | clean |
| VIN patterns | clean — the only hit is this file describing its own check |
| Adapter serial in device names | clean |
| Credentials / tokens | clean — the only hit is the heading "Trade secrets" |
| Vendor artefacts by filename | clean — two hits are this file's own exclusion table |
| Binaries / images | clean — text files only |

### 9.5 Legal and safety re-assessment

**Copyright.** Unchanged: no vendor code, firmware, application or database is
reproduced. Protocol values read from a device the owner possesses are facts about
that device.

**Anti-circumvention.** Unchanged and now more explicit: no signature was broken,
no protection was removed. `10 C0` is a diagnostic session that the unit offers; it
is not a security mechanism, and there is no security-access service in the data set
used here.

**Safety.** Raised from *low* to *moderate*. The repository now contains a working
sequence that changes a configuration byte in a production head unit. Mitigations
in the published text:

- it is framed as one case on one unit, with an explicit statement that the session
  requirement is confirmed only for that unit at that software version,
- it states that the target value depends on the flags a unit already reports, so
  copying `0x78` blindly can clear flags elsewhere,
- it states that no recovery path is verified and that a failed write may be
  unrecoverable,
- it separates the confirmed configuration change from the untested projection and
  from the untested CarPlay path.

**Residual risk:** moderate, and accepted by the owner of the vehicle and of this
repository. A reader who copies the sequence onto a different unit does so at their
own risk; the text says so in three places.

### 9.6 Verdict of the re-audit

Publishable. No personal data, no vendor material, no third-party asset, no
credentials, no binaries. The one substantive change is that a protocol sequence is
now disclosed deliberately, with its scope and its limits stated next to it.

---

## 10. Restructure 2026-11-08 — from research notes to a project

The repository was rebuilt as a guide plus tools. This section records what that
changed and re-runs the checks.

### 10.1 What moved and what was added

| Change | Detail |
|---|---|
| `RESEARCH.md` | moved to `research/RESEARCH.md` (git rename, history kept) |
| `RESULTS/…2026-11-08.md` | moved to `research/results/` |
| `docs/` | ten new chapters: compatibility, hardware, installation, connection, identification, activation, verification, CarPlay plan, troubleshooting, recovery |
| `tools/` | new: `ecu_config.py`, `obd_transport.py`, `read_config.py`, `write_config.py`, `requirements.txt` |
| `tests/` | new: `mock_ecu.py`, `test_ecu_config.py`, `test_write_config.py` — 33 offline tests |
| `LICENSE-CODE` | new: MIT for `tools/` and `tests/` |
| `NOTICE.md` | rewritten: CC BY 4.0 for text, MIT for code, third-party carve-out |
| `config/aa_write.example.json` | example gate, disabled; the real file is git-ignored |
| `.gitignore` | excludes `config/aa_write.json`, `logs/`, caches |

The original research text and the result report are unchanged apart from their
paths.

### 10.2 Code provenance

Every line under `tools/` and `tests/` was written for this project during the
work described in `research/`. Nothing is copied from DDT4All, from a vendor, or
from any other repository. The tools use the Python standard library plus
`pyserial`.

DDT4All is referenced in two ways only: as a source of the *encoding convention*
(a fact about how its descriptors number bits, verified by reading its source) and
as an alternative route the reader may choose. No code, no database, no data file
from it is included. DDT4All is GPL-3.0; the MIT/CC-BY split here does not conflict
with it because there is no derived code.

The Bluetooth bridge lives in a **separate** repository
(`obdlink-macos-rfcomm-bridge`) and is referenced by URL, not copied.

### 10.3 Re-run of the checks

Checks run over all tracked text and code files:

| Check | Result |
|---|---|
| Account name, home paths, `/Users/…` | clean |
| RFC 1918 addresses, hostnames | clean |
| MAC addresses, adapter serial numbers | clean |
| VIN patterns | clean |
| Credentials, tokens, keys | clean |
| Vendor artefacts by filename (`TOMTOM.000`, `.apk`, `.odex`, `ecu.zip`) | clean — only the audit's own exclusion table mentions them |
| Proprietary database content | none present |
| Binaries, images, archives | none |
| Absolute private paths in code | none — tools resolve paths relative to themselves |
| Third-party code without licence | none |
| Offline test suite | 33 tests, all pass |
| Write tool locked by default | verified: refuses without both switches |

### 10.4 Risk changes from publishing code

The repository now ships a working writer. That raises the practical risk compared
with a documentation-only release, and the mitigations are in the code rather than
in prose:

- the tool refuses to start without two independent switches,
- it verifies part number, current value, voltage and target before sending,
- it sends exactly one frame and never retries,
- it cannot clear the bit again, so it cannot be used to "try things",
- session commands are limited to one `10 C0` behind an explicit flag; every other
  session or reset command is refused by the transport layer and covered by a test.

**Residual risk: moderate.** Accepted by the repository owner. The documentation
states the limits next to every claim.

### 10.5 Verdict of the restructure

The repository is coherent as a project: guide, tools, tests, research, licences.
No personal data, no vendor material, no unsourced claims. The visibility remains
**private** until the owner gives explicit release approval.
