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
