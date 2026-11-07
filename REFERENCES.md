# References

Public sources used for these notes. Nothing listed here is redistributed in this
repository; each entry states what it supports and how it may be used.

---

## 1. Vendor certification document

**TomTom International B.V., _Certification Construction File MFD2.x_, document
TT00113919, version 2.1, released 2016-01-26.**

- Public copy (FCC filing mirror): `https://fccid.io/m/4d60f33c8360e1aea305216972e6d0ff15525ad55ced1c2cfa3f17d477ca8fe5.pdf`
- FCC ID of the device family: `S4L1ME09`
- Supports in these notes: product name "MFD", brand TomTom, model `1ME09`,
  internal project name "Strasbourg", the part-number table that maps Renault
  `259156244R` to TomTom `1ME0.001.45` and Daimler `4539002904`, and the component
  list mentioning an Apple authentication IC.
- Usage: quoted only as isolated facts (model names, part numbers, the existence of
  a component). No pages, diagrams or tables are reproduced here. The document is
  the vendor's; check its terms before redistributing it.

## 2. Adapter documentation

**ScanTool.net, _OBDLink Family Reference and Programming Manual_ (FRPM).**

- `https://www.scantool.net/scantool/downloads/678/obdlink_frpm_e.pdf`
- Supports: protocol presets (ISO 15765 / ISO 11898), CAN addressing and flow
  control behaviour, the adapter's default request timeout, RFCOMM and SPP
  behaviour, 11-bit and 29-bit reception.
- Usage: referenced for behaviours observed with the adapter (timeouts, flow
  control). No manual text is copied.

**OBDLink MX+ product page** — `https://www.obdlink.com/products/obdlink-mxp/`
Supports: Bluetooth class, supported protocols, platform list (iOS/Android/Windows).

**OBDLink FAQ** — `https://www.obdlink.com/faq/`
Supports: the vendor's statement that no Mac or Linux software is planned. Relevant
because the macOS transport in this project is built on OS-level APIs, not vendor
software.

## 3. Firmware image (analysed, not redistributed)

**Vendor-published update image** for this product family, obtained through the
manufacturer's official update and support channel.

- Integrity: SHA-256 verified against the vendor's own manifest inside the package.
- Usage: analysed offline on a workstation. **Not included, not mirrored, and no
  download link is given here.** The image belongs to the vendor; anyone obtaining
  it is bound by the vendor's terms, not by this repository's licence. Readers who
  need it should use the manufacturer's official support pages.

## 4. Update container decoding

**goingelective wiki, "R-Link Update entpacken"** —
`https://www.goingelectric.de/wiki/R-LinkUpdateEntpacken`

- Supports: the container layout used by these update packages (extra 20-byte
  blocks every 102,400 bytes plus leading bytes, removed before unpacking).
- Usage: method reference only. The page is community documentation; no text or
  code is reproduced.

## 5. Platform facts

**Wikipedia, "Smart Fortwo"** — `https://en.wikipedia.org/wiki/Smart_Fortwo`
Supports: the 453 generation was co-developed with the third-generation Renault
Twingo on a shared platform, which is why Renault part numbers and Renault-style
diagnostic conventions appear on this unit. CC BY-SA; used for a single factual
statement, attributed here.

## 6. Open-source CarPlay projects (studied, not included)

Used only to understand what a CarPlay receiver requires. Their code is **not**
vendored into this repository and no excerpts are reproduced.

| Project | URL | License | Note |
|---|---|---|---|
| LIVI | `https://github.com/f-io/LIVI` | GPL-3.0 | Rust/Slint CarPlay + Android Auto head unit |
| CatPlay | `https://github.com/catplay-labs/catplay` | **none declared** | Rust CarPlay stack for wireless dongles |
| PlayPort | `https://github.com/youcci/playport` | GPL-3.0 | Kotlin/JVM + browser wireless CarPlay |

All three require Apple MFi authentication material: either a physical MFi
coprocessor or a vendor-issued certificate and key. This is stated in their own
documentation and is the reason no CarPlay work is attempted here.

CatPlay has **no license file** in its repository, which means no reuse rights are
granted by default. It is cited as a reference only.

## 7. Standards

- **ISO 15765-2** — CAN transport protocol (ISO-TP), segmentation and flow control.
- **ISO 14229** (UDS) — diagnostic services, notably `0x22` ReadDataByIdentifier.
- **ISO 15031 / SAE J1979** — legislated OBD services and identifiers.

Referenced by name for terminology. The standards are not free to redistribute and
are not reproduced here.

## 8. Tooling

- **DDT4All / DDT2000** — community diagnostic tooling that consumes declarative
  ECU descriptor files. Described structurally in `RESEARCH.md`; the tool and its
  vendor-specific databases are **not** included here.
- **ddt4all `projects.json`** (address mapping for several brands) — public in the
  project's repository; supports the observation that ECU descriptors derive CAN
  identifiers from a logical address.

---

## Licensing summary

The text of this documentation is licensed **CC BY 4.0** — legal code in
`LICENSE`, scope in `NOTICE.md`. That
licence covers only the original prose written for this repository. It does not
extend to any third-party material, and it grants no rights in any vendor firmware,
software, database, documentation or trademark. Product names are used
descriptively; all trademarks remain with their owners.

| Material | Status in this repository |
|---|---|
| Prose in `README.md`, `RESEARCH.md`, `REFERENCES.md`, `PUBLICATION_AUDIT.md`, `NOTICE.md` | **CC BY 4.0** (`LICENSE`, scope in `NOTICE.md`) |
| Vendor certification document | not included, not licensed here |
| Vendor firmware image | not included, not licensed here |
| Community wiki content | not included, not licensed here |
| Open-source CarPlay projects | not included, not licensed here |
| Standards texts | not included, not licensed here |
| DDT4All and its databases | not included, not licensed here |
| Trademarks and product names | remain with their respective owners |
