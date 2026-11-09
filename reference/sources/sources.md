# Source register

Classes: **A** manufacturer/regulator, **B** original artifact or source code, **C** own observation/report, **D** community report, **E** unverified or unavailable.

A source marked `internal` is listed for provenance only; its content and locator are not published. A `gated` or `dead` source is not treated as confirmed.

| ID | Class | Source | Availability | Decision | Access / caveat |
|---|---|---|---|---|---|
| `SRC-DDT-DB` | B | DDT2000/DDT4All ECU database (5.673 definitions) | internal | INTERNAL_ONLY | internal; SHA-256 b78813c23f72cae283d50aa771d86e18375921125bafa8bae7da85953dcb90a1; 484.864.596 Byte; no licence proven. Licence unclear; no redistribution. |
| `SRC-DDT-EMM-SW13_1` | B | EMM_EDISON_DDT2000_SW13_1_V1_3 diagnostic definition | internal | INTERNAL_ONLY | internal; 689.857 Byte; SHA-256 f616f9bc73dab1626ef92ac2da9bbb19bc4ddd32f7d0341b255dfc5987d005af; 237 requests; 2.111 data objects. Definition only; no executable code. |
| `SRC-DDT-HU-MFD-v5.4` | B | MFD v5.4 diagnostic definition | internal | INTERNAL_ONLY | internal; 211.540 Byte; SHA-256 0415cb2ad9ff64689e7f5beabf221013fed6355068893856ee823cac1c3b2ee9; 192 requests; 688 data objects; 21 autoidents. Definition only; no executable code. |
| `SRC-DDT-HU-MFD-v4.6` | B | MFD v4.6 diagnostic definition | internal | INTERNAL_ONLY | internal; 210.010 Byte; SHA-256 7a82d95f80d0c1e8858362cc0379dedfc32c0b1f16846fb037023c7523b36762; 192 requests; 3 autoidents. Comparison definition only. |
| `SRC-DDT-HU453` | B | HU453 00.00.77 diagnostic definition | internal | INTERNAL_ONLY | internal; 79 requests; newer HU generation, not proven to be this vehicle's MFD. Included as comparison material only. Alternative definition; identity not proven. |
| `SRC-PHASE81-REPORT` | B | Phase 8.1 Firmware Discovery report | internal | INTERNAL_ONLY | internal; Internal report; contains local paths and detailed source work. Project report; not an independent source. |
| `SRC-MATRIX-V4` | C | Smart 453 V4 master matrix (54 functions, 33 columns) | internal | INTERNAL_ONLY | internal; SHA-256 ad84cb21d44a10d3f00104d206d8124167b2420cbc0984b4ce09b100bf93f205. Contains vehicle-specific values; no raw logs. |
| `SRC-CONFIG-INVENTORY` | C | Smart 453 / TomTom MFD read-only configuration inventory | internal | INTERNAL_ONLY | internal; MFD DIDs, masks and community references; only 0x6C1C was measured on this vehicle. Read-only inventory; not independently reproduced. |
| `SRC-REPO` | B | cheapjourney/smart453-tomtom-research | public | CITE | HTTP 206; Public, default branch main, last push 2026-11-08. Existing publication audit excludes raw request catalogues and firmware. Primary publication surface. |
| `SRC-REPO-DOC05` | C | 05 — Identifying the head unit | public | CITE | HTTP 206; Part number 259156244R, 1ME0.001.45, 4539002904; 0x6C1C 0x38 -> 0x78; a diagnostic identifier / a diagnostic identifier. Read-only identification report; raw log not published. |
| `SRC-REPO-RESEARCH` | C | research/RESEARCH.md and activation result | public | CITE | HTTP 206; Vehicle identity, diagnostic transport, a diagnostic identifier record length, projection architecture, activation. Includes the published 0x6C1C activation case. |
| `SRC-REPO-PUBLICATION-AUDIT` | B | Publication audit | public | CITE | HTTP 206; Explicitly excludes firmware, raw diagnostic hex, third-party DDT catalogue and vehicle-identifying records from the public repo. Section 10.5 is historical; section 11 correction added in the Phase 8.3 branch. |
| `SRC-PHASE4-R2` | C | Phase 4 — RenaultR2 identification record | internal | INTERNAL_ONLY | internal; Raw headunit a diagnostic identifier: 26 bytes, first ASCII 5104R, second field device-specific; only the line is decoded. Raw identification record remains internal. |
| `SRC-DEBUG-ACCESS` | B | SMART 1ME09 debug/service access | internal | INTERNAL_ONLY | internal; build.prop 8.8/3206684/3198575, TOMTOM.000 hash, ttpkg structure, rootfs delta, ADB gating. No physical debug access was confirmed. |
| `SRC-ADB-ROOTFS` | B | ADB activation and full-rootfs inventory | internal | INTERNAL_ONLY | internal; load_fdt/device-class/ADB chain; GPL source hash; no complete Android userspace/rootfs. Rootfs analysis is partial. |
| `SRC-HW-SW-TESTPOINTS` | B | Hardware/software testpoints, UART, JTAG, eMMC | internal | INTERNAL_ONLY | internal; FCC S4L1ME09; label 259154108R/4539001301/1ME0.001.27; board TN4D; no confirmed debug pad. No test point confirmed. |
| `SRC-FLASH-DUMP-PLAN` | B | Flash identification and read-only dump plan | internal | INTERNAL_ONLY | internal; 4 MiB CFI-NOR, 0x08000000, DIAGSYS 0x08300000; MoviNAND; no confirmed testpoints. Read-only plan only. |
| `SRC-DIAGSYS-FACTORY` | B | DIAGSYS/factory boot path | internal | INTERNAL_ONLY | internal; 1 MiB DIAGSYS applet at NOR 0x08300000; 44-byte DSA signature; no applet binary; UART3 context. Factory mode is not a general dump path. |
| `SRC-MFD-DIAG-SERVER` | B | MFD firmware diagnostic server | internal | INTERNAL_ONLY | internal; libttdaemon.features.diagnostics.so; handler names; no 0x23/0x35 evidence; internal file paths. Diagnostic server is factory/recovery context. |
| `SRC-MFD-UNDOCUMENTED` | B | MFD implemented vs documented diagnostic services | internal | INTERNAL_ONLY | internal; SID table; 53 IO-control requests; no 0x23/0x27/0x34-0x37 handler; no file export over CAN. Implemented-vs-documented service comparison. |
| `SRC-MFD-REPROG` | B | MFD Reprog/recovery references | internal | INTERNAL_ONLY | internal; No diagnostic reprog/transfer; HU453 start routine only; PyRen is configuration, not flashing. No verified recovery path on the vehicle. |
| `SRC-FIRMWARE-INVENTORY` | B | Firmware inventory and base image | internal | INTERNAL_ONLY | internal; TOMTOM.000 479.879.168 B; ttpkg 453.884.542 B; rootfs delta 451.162.156 B; no full rootfs. Artifacts not redistributed. |
| `SRC-PROJECTION-ARCH` | B | Strasbourg projection architecture | internal | INTERNAL_ONLY | internal; AA and MirrorLink fully implemented; iAP2 media only; no CarPlay/AirPlay stack. Completeness/function not proven. |
| `SRC-DIAG-AUDIT` | B | DiagnosticsApp/ServicesSettings/FudReader audit | internal | INTERNAL_ONLY | internal; Most extracted DEX are damaged; no reliable DiagnosticsApp export; signature check present but path unproven. App/service audit is partial. |
| `SRC-JOBLIST` | B | Official TomTom joblist wire format | internal | INTERNAL_ONLY | internal; jobs.xml, jobs.xml.sig, files.sig, pkgdownload/pkginstall/rebootrequired; signed jobs/files. Signature verification presence, not enforcement proof. |
| `SRC-FCC` | A | FCC ID S4L1ME09 — TomTom 1ME09 exhibits | public | CITE | HTTP 206; External photos, label, internal photos; no schematic/block diagram. Label: 259154108R / 4539001301 / 1ME0.001.27. Reference unit, not the vehicle unit. |
| `SRC-TOMTOM-CERT` | A | TomTom 1ME09/1ME09C (MFD2.x) certification construction file | public | CITE | HTTP 206; Part-number table: 1ME0.001.45 = 259156244R = 4539002904; 1ME0.001.27 = 259154108R = 4539001301; differences are SW aspects. Strong identity match. |
| `SRC-SMART-FORUM-4149` | D | Smart-453-Forum — MOPF LED front lights retrofit, page 46 | public | CITE_CAVEAT | HTTP 200; 2020 replacement 231A07278R / EMM-T4 / SW13_1_V1_3; Nsx_Singlebulb_DRL_Tail_CF only 0/1. No firmware file; anecdotal. |
| `SRC-SMART-FORUM-2510` | D | Smart-453-Forum — Android Auto/CarPlay in 453 | public | CITE_CAVEAT | HTTP 200; Community procedure for 0x6C1C; confirms AA configuration is known in the 453 community. Feature discussion; not a measurement. |
| `SRC-SMART-MEDIA-FORUM` | D | Smart-453-Forum — Smart Media System firmware versions | public | CITE_CAVEAT | HTTP 200; 11.346.3206684-8060 as last 453 combustion firmware; 11.347.x exists in 2023 but applicability is not proven for this unit. Version discussion; no files. |
| `SRC-DDT4ALL-512` | D | DDT4All issue #512 — Navigation / multimedia CAN | public | CITE_CAVEAT | HTTP 206; Navigation UCC-ITM name; separate multimedia CAN to radio; manual ECU selection; timeout observations. Multimedia-CAN method only. |
| `SRC-PINOUT-RENAULT` | D | Renault OBD-II connector pinout — pins 12/13 LS/multimedia CAN | public | CITE_CAVEAT | HTTP 200; General Renault convention, not a Smart 453 measurement; physical confirmation on this vehicle is outstanding. Not confirmed for this vehicle. |
| `SRC-ST-RM0037` | A | ST RM0037 — SPC560B54x/60x/64x reference manual | public | CITE_CAVEAT | HTTP 000; Censorship, BAM, serial boot, Nexus, boot-sector read limitation, permanent lockout. Original ST URL blocked; mirror used; conditional on MCU. |
| `SRC-ST-DATASHEET` | A | ST SPC560B54x/60x/64x datasheet | public | CITE_CAVEAT | HTTP 000; 768 KB/1 MB/1.5 MB code flash; 64 KB data flash; BAM; Nexus 1 all packages. Original ST URL blocked; family data only. |
| `SRC-RENAULT-REPROG` | A | Renault ReProg procedure (TN 3585A) | public | CITE | HTTP 206; CLIP/Renault.NET/CD 77 11 298 859; VIN/part number; battery charger; reprogramming code; emergency procedure. Procedure context; no firmware content. |
| `SRC-REPROG-V191` | E | Renault Reprog V191 factory flash files / ECU programming base | gated | CITE_CAVEAT | HTTP 403; V191, ca. 4 GB, CLIP; access via thanks/PM; no public index; not downloaded. HTTP 403; no content inspected. |
| `SRC-EVILUTION` | D | Evilution — Smart 453 Android Auto / R-Link notes | public | CITE_CAVEAT | HTTP 200; Community describes Smart Media System as R-Link-related; not an exact software identity proof. Background/method only. |
| `SRC-MHH` | D | MHH AUTO — EMM-T4 L3/L4 threads | gated | CITE_CAVEAT | HTTP 403; L3 MCU SPC560B54L; L4 pinout TCK/TMS/TDI/TDO/Reset; page often 403; unverified. HTTP 403; no content inspected. |
| `SRC-GITHUB-SEARCH` | E | GitHub code search — 231A07278R / EMM_EDISON / SPC560B54L | public | CITE_CAVEAT | HTTP 206; No hits at search time; absence of evidence is not proof of non-existence. No results does not prove absence. |
| `SRC-USER-PHASE82` | B | Phase 6.7 private EMM measurement | internal | INTERNAL_ONLY | project; Archived privately in the Phase 6.7 evidence set; raw record, hash and individual values are not published. The public statement is derived. |
| `SRC-PARTS-EMM` | E | 231A07278R EMM-T4 L4 parts listings | dead | DO_NOT_CITE | HTTP 500; EMM-T4 L4, Bosch, 231A07278R; A4539000403; 3058565646; dealer claims, not official. Dead link; dealer association only. |

## Access findings

- The original ST RM0037 and SPC560B54L datasheet URLs returned a transport error from this host. A public mirror of RM0037 was used for the analysis; the datasheet was treated as family material only.
- The Renault ReProg V191 page and the MHH thread return HTTP 403 without a session. They were not bypassed.
- The `ecusell.com` parts listing returns HTTP 500. It is not used as a confirmed source.
- `fccid.io` and the TomTom certification PDF are reachable; the certification is the stronger identity source.
- GitHub and the public project pages are reachable.
