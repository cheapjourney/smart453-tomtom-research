# smart453-tomtom-research

Notes from a read-only investigation of the TomTom-based head unit in a Smart 453
(W453): what the unit is, how its diagnostic interface behaves, and how its
phone-projection stacks are put together.

> **Status: research notes, not a tool.** Nothing here writes to a vehicle, and
> nothing here has been validated as a working modification. Every claim is
> labelled with how it was obtained — see *Evidence levels* below.

## What this is

- A record of observations made on one vehicle with an off-the-shelf OBD-II
  adapter, using only reading diagnostic services.
- An architectural description of the unit's software, derived from a publicly
  downloadable firmware image that the vendor distributes.
- A list of questions that could not be answered without further hardware access.

## What this is not

- Not a coding, flashing or retrofit guide. There are no write procedures here.
- Not a redistribution of vendor firmware, extracted applications or vendor
  configuration databases.
- Not affiliated with, endorsed by or supported by TomTom, smart, Renault or
  Mercedes-Benz. Product names are used descriptively only.
- Not a claim that Android Auto, CarPlay or any other feature can be enabled.

## Evidence levels

Every factual statement in `RESEARCH.md` carries one of these tags:

| Tag | Meaning |
|---|---|
| **[LIVE]** | Read from the vehicle with the adapter, at least once, reproducible |
| **[OFFLINE]** | Derived from the vendor's public firmware image on a workstation, no vehicle involved |
| **[PUBLIC]** | Taken from a public document or a public repository, cited in `REFERENCES.md` |
| **[REPORTED]** | Stated by the project owner and not independently verified here |
| **[OPEN]** | Unknown; listed as an open question |

A statement never appears without a tag. Where a conclusion rests on more than one
kind of evidence, all applicable tags are given.

## Files

| File | Content |
|---|---|
| `RESEARCH.md` | The findings: environment, identity, diagnostics, architecture, encoding |
| `REFERENCES.md` | Public sources, each with a URL and what it supports |
| `PUBLICATION_AUDIT.md` | What was deliberately left out and why, plus the remaining risks |

## Headline findings

1. The unit identifies itself over diagnostics with Renault part number
   `259156244R`, which maps in the vendor's certification document to TomTom
   model `1ME09` / project `Strasbourg`. **[LIVE] [PUBLIC]**
2. It answers on the 11-bit diagnostic pair `0x747` (request) / `0x767`
   (response) with normal ISO-TP addressing. **[LIVE]**
3. It runs Android 2.2 (API 8) on an ARMv7 OMAP3 SoC. **[OFFLINE]**
4. It ships **two** independent phone-projection stacks as add-ons — a MirrorLink
   stack and an Android Auto stack — both fully implemented, both invisible in the
   normal app list. **[OFFLINE]**
5. There is no CarPlay stack in the firmware. **[OFFLINE]**

## Scope and safety

These notes describe a vehicle's internal systems. If you use them, you are
responsible for what you do with them:

- Diagnostics on a modern vehicle can affect safety-relevant systems if used
  carelessly. Reading is not automatically safe just because it is reading.
- The unit is part of the car. Bricking it is expensive and may not be
  recoverable.
- Modifying a head unit can create driver distraction, which is regulated in most
  jurisdictions.

Nothing in this repository is a substitute for the manufacturer's service
information.

## License

The documentation text in this repository is licensed **CC BY 4.0**. The unmodified
legal code is in [`LICENSE`](LICENSE); what the licence covers — and what it
explicitly does not — is in [`NOTICE.md`](NOTICE.md).

In short: it covers only the original prose written for this repository. It grants
no rights in any vendor firmware, software, database or documentation, and no rights
in any trademark. Cited third-party material is listed in
[`REFERENCES.md`](REFERENCES.md) and is not redistributed here.
