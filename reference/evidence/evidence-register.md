# Evidence register

This register contains the 44 hardened base statements from the Phase 8.3 audit. The
Phase 6.7 addendum adds 8 derived entries in
[`phase6-7-validation.md`](phase6-7-validation.md); the Phase 8.4/8.5 addendum adds 8
entries in [`phase8-4-consolidation.md`](phase8-4-consolidation.md). It is a public
derived view: raw logs, raw frames, internal paths, and artifact locators are not
included. The full audit with original and hardened statements is kept privately.

| ID | ECU | Level | Status | Statement | Sources |
|---|---|---|---|---|---|
| `EV-EMM-001` | ECU-EMM-EDISON | L1 | CONFIRMED | The EMM reported the cornering configuration flag as 0. The Phase 6.7 evidence set contains the archived read-only record; it is not published. This is a read-only vehicle observation, not a function test. | SRC-USER-PHASE82, SRC-MATRIX-V4 |
| `EV-EMM-002` | ECU-EMM-EDISON | L2 | CONFIRMED | The diagnostic definition EMM_EDISON_DDT2000_SW13_1_V1_3 is present in the project: 237 requests, 2,111 data objects, SHA-256 f616f9bc…. | SRC-DDT-EMM-SW13_1 |
| `EV-EMM-003` | ECU-EMM-EDISON | L2 | CONFIRMED | The identity tuple 8/414/C132/4022 is exactly one autoidents tuple of SW13_1; no other EMM definition in the examined set contains it. | SRC-DDT-EMM-SW13_1, SRC-DDT-DB |
| `EV-EMM-004` | ECU-EMM-EDISON | L2 | CONFIRMED | In the SW13_1 definition, the service set contains no SecurityAccess, upload/download, or routine-control service; the read and configuration services are limited to the identifiers the definition describes. Absence in this definition is not proof that the device lacks a service. | SRC-DDT-EMM-SW13_1 |
| `EV-EMM-005` | ECU-EMM-EDISON | L2 | CONFIRMED | The modern lighting-configuration read returns at least 11 bytes; the legacy form returns at least 13 bytes. Both are definition-derived length constraints. | SRC-DDT-EMM-SW13_1, SRC-DDT-DB |
| `EV-EMM-006` | ECU-EMM-EDISON | L3 | NOT_TESTED | In SW13_1, the lighting-configuration, history, identification, and cornering parameters are defined. The lighting-configuration, history, and identification reads were not performed at the vehicle; the cornering read is covered by EV-EMM-001. | SRC-DDT-EMM-SW13_1 |
| `EV-EMM-007` | ECU-EMM-EDISON | L3 | NOT_TESTED | The reprogramming-history record is defined as a read-only history record in SW13_1, but it was not read on this vehicle. | SRC-DDT-EMM-SW13_1 |
| `EV-EMM-008` | ECU-EMM-EDISON | L3 | NOT_TESTED | A modern cornering write path is defined in SW13_1. It was not executed in any phase covered by this reference; no write payload is published here. | SRC-DDT-EMM-SW13_1 |
| `EV-EMM-009` | ECU-EMM-EDISON | L4 | UNCONFIRMED | The vehicle's EMM part number is 231A07278R. A single community report describes a 2020 replacement 231A07278R unit as EMM-T4; this is not independent confirmation. The EMM-T4 L4/Bosch attribution and the alternative numbers from dead dealer/parts listings remain unconfirmed and are not used as evidence here. | SRC-USER-PHASE82, SRC-SMART-FORUM-4149 |
| `EV-EMM-010` | ECU-EMM-EDISON | L4 | UNCONFIRMED | The MCU is not confirmed for 231A07278R. Forum candidates are SPC560B54L and SPC560B60L5; neither is proven for this L4 board. | SRC-MHH |
| `EV-EMM-011` | ECU-EMM-EDISON | L2 | CONFIRMED | The SPC560B family reference manual describes censorship protection for JTAG/Nexus and serial boot. If the fitted MCU is in that family, a full flash read without the 64-bit password would require defeating that protection, which this project does not do. | SRC-ST-RM0037, SRC-ST-DATASHEET |
| `EV-EMM-012` | ECU-EMM-EDISON | L5 | UNCONFIRMED | The executable firmware version installed in 231A07278R is unknown. The DDT definition selected by the identity tuple is not the firmware. | SRC-DDT-EMM-SW13_1, SRC-PHASE81-REPORT |
| `EV-EMM-013` | ECU-EMM-EDISON | L4 | UNCONFIRMED | One community report describes a 2020 replacement 231A07278R unit that reported SW13_1_V1_3 and a two-value single-bulb DRL parameter. This is a single, unverified report. | SRC-SMART-FORUM-4149 |
| `EV-EMM-014` | ECU-EMM-EDISON | L2 | CONFIRMED | Eleven EMM_EDISON definitions differ in requests, data objects, and autoidents; SW15_2 and SW15_3 have identical request and data sets. | SRC-DDT-DB |
| `EV-EMM-015` | ECU-EMM-EDISON | L4 | CONFIRMED | No public firmware image for 231A07278R was found. The Renault Reprog V191 archive is gated and no public index or confirmed EMM entry was found. A negative search does not prove that no image exists. | SRC-GITHUB-SEARCH, SRC-REPROG-V191, SRC-PHASE81-REPORT |
| `EV-EMM-016` | ECU-EMM-EDISON | L2 | CONFIRMED | The all-configuration block grows from 295 bytes in SW13_1 to 443 bytes in SW15_3. This is a configuration block, not a flash image. | SRC-DDT-EMM-SW13_1, SRC-DDT-DB |
| `EV-EMM-017` | ECU-EMM-EDISON | L2 | CONFIRMED | The DDT project mapping names the project families x07, x82, x87, x98, xGA, and xHA. This is a project mapping, not a part-number release list. | SRC-DDT-DB |
| `EV-EMM-018` | ECU-EMM-EDISON | L5 | UNCONFIRMED | A donor-bench full-flash read is plausible only if the donor MCU is uncensored or the 64-bit password is known. This project does not bypass censorship. | SRC-ST-RM0037, SRC-MHH |
| `EV-HU-001` | ECU-HU-MFD | L1 | CONFIRMED | A read-only part-number query on the vehicle returned 259156244R for the head unit. | SRC-REPO-DOC05, SRC-REPO-RESEARCH |
| `EV-HU-002` | ECU-HU-MFD | L1 | CONFIRMED | The 0x6C1C configuration byte was 0x38, was changed to 0x78 in the after-sales session, and was read back as 0x78. The owner reports that Android Auto entries appeared after a restart; projection was not tested. | SRC-REPO-DOC05, SRC-REPO-RESEARCH |
| `EV-HU-003` | ECU-HU-MFD | L1 | CONFIRMED | An identity-record read returned 26 bytes; the first ASCII field is 5104R. The second field is device-specific and is redacted. The exact build is not derived from this record. | SRC-PHASE4-R2 |
| `EV-HU-004` | ECU-HU-MFD | L1 | CONFIRMED | The head unit's version screen shows application version 11.346.3206684-8060. | SRC-REPO-DOC05, SRC-SMART-MEDIA-FORUM |
| `EV-HU-005` | ECU-HU-MFD | L2 | CONFIRMED | MFD v5.4 and v4.6 each contain 192 requests and 688 data objects; v4.6 has 3 autoidents, v5.4 has 21. | SRC-DDT-HU-MFD-v5.4, SRC-DDT-HU-MFD-v4.6 |
| `EV-HU-006` | ECU-HU-MFD | L2 | CONFIRMED | The MFD v5.4 definition contains no SecurityAccess, upload/download, or routine-control service. Its read and configuration services are limited to defined identifiers. Absence in the definition is not proof that the device lacks a service. | SRC-DDT-HU-MFD-v5.4, SRC-MFD-UNDOCUMENTED |
| `EV-HU-007` | ECU-HU-MFD | L2 | CONFIRMED | MFD v5.4 contains 49 write requests, 53 IO-control requests, 71 data-by-identifier reads, and 5 local-identifier reads. | SRC-DDT-HU-MFD-v5.4 |
| `EV-HU-008` | ECU-HU-MFD | L2 | CONFIRMED | MFD v5.4 defines a diagnostic session and an after-sales session, but no programming session. | SRC-DDT-HU-MFD-v5.4, SRC-MFD-UNDOCUMENTED |
| `EV-HU-009` | ECU-HU-MFD | L2 | CONFIRMED | TOMTOM.000 is a 479,879,168-byte ext3 delivery container with SHA-256 157e95d9…. | SRC-DEBUG-ACCESS, SRC-FIRMWARE-INVENTORY |
| `EV-HU-010` | ECU-HU-MFD | L2 | CONFIRMED | The 3206684 update package is 453,884,542 bytes with SHA-256 5b4e311a… and contains a kernel image and a rootfs block delta. | SRC-DEBUG-ACCESS, SRC-FIRMWARE-INVENTORY |
| `EV-HU-011` | ECU-HU-MFD | L2 | CONFIRMED | The rootfs delta contains a journal and inode damage; it is not a complete, mountable root filesystem. | SRC-FIRMWARE-INVENTORY, SRC-DEBUG-ACCESS |
| `EV-HU-012` | ECU-HU-MFD | L2 | CONFIRMED | The board has a 4 MiB parallel CFI NOR device on GPMC chip-select 0 at 0x08000000; the DIAGSYS region is 0x08300000–0x083FFFFF. | SRC-FLASH-DUMP-PLAN, SRC-DIAGSYS-FACTORY |
| `EV-HU-013` | ECU-HU-MFD | L2 | UNCONFIRMED | UART3/ttyO2 is a candidate for the U-Boot console, but no physical test point is confirmed. | SRC-HW-SW-TESTPOINTS, SRC-DIAGSYS-FACTORY |
| `EV-HU-014` | ECU-HU-MFD | L2 | CONFIRMED | ADB is gated by the device-class property loaded through the FDT; without device-class=1, adbd remains off. | SRC-ADB-ROOTFS |
| `EV-HU-015` | ECU-HU-MFD | L2 | CONFIRMED | Android Auto and MirrorLink components are present in the analyzed firmware artifacts. Their completeness and their actual projection function are not proven. | SRC-PROJECTION-ARCH |
| `EV-HU-016` | ECU-HU-MFD | L2 | UNCONFIRMED | iAP2 media components are present. No CarPlay/AirPlay protocol stack was found in the analyzed, incomplete artifacts; absence on the whole device is not proven. | SRC-PROJECTION-ARCH |
| `EV-HU-017` | ECU-HU-MFD | L4 | CONFIRMED | TomTom certification identifies 1ME0.001.45 as Renault 259156244R and Daimler 4539002904, model 1ME09. | SRC-TOMTOM-CERT |
| `EV-HU-018` | ECU-HU-MFD | L4 | CONFIRMED | The FCC reference unit is 1ME0.001.27 / 259154108R / 4539001301, FCC ID S4L1ME09, board TN4D. | SRC-FCC, SRC-HW-SW-TESTPOINTS |
| `EV-HU-019` | ECU-HU-MFD | L4 | UNCONFIRMED | It is not proven that the FCC board TN4D is identical to the vehicle part 259156244R. | SRC-FCC, SRC-TOMTOM-CERT, SRC-HW-SW-TESTPOINTS |
| `EV-HU-020` | ECU-HU-MFD | L5 | UNCONFIRMED | The exact installed build (3206684 vs 3168863) cannot be derived from the identity record; the version screen names 3206684. | SRC-PHASE4-R2, SRC-REPO-DOC05 |
| `EV-HU-021` | ECU-HU-MFD | L1 | CONFIRMED | The write to the 0x6C1C configuration byte was refused in the default diagnostic session and accepted in the after-sales session. This establishes a session requirement for this one case; it is not a universal recipe. | SRC-REPO-RESEARCH |
| `EV-HU-022` | ECU-HU-MFD | L2 | CONFIRMED | The TomTom update uses signed job and file manifests; a signature-verification path is present. | SRC-JOBLIST, SRC-DIAG-AUDIT |
| `EV-HU-023` | ECU-HU-MFD | L2 | CONFIRMED | The project holds no complete root filesystem, NOR dump, or eMMC dump for the head unit. | SRC-FIRMWARE-INVENTORY, SRC-FLASH-DUMP-PLAN |
| `EV-HU-024` | ECU-HU-MFD | L4 | UNCONFIRMED | Community descriptions call the Smart Media System R-Link-1-like; the exact identity established here is TomTom 1ME09/Strasbourg, not R-Link. | SRC-EVILUTION, SRC-DDT4ALL-512 |
| `EV-SHARED-001` | SHARED | L4 | NOT_TESTED | OBD pins 12/13 are commonly described as an LS/multimedia CAN pair on Renault vehicles; for this Smart 453, no continuity or pin measurement confirms it. | SRC-PINOUT-RENAULT, SRC-DDT4ALL-512 |
| `EV-PUB-001` | SHARED | L2 | CONFIRMED | The public repository excludes firmware and the DDT request catalogue. Raw diagnostic hex is limited to the one deliberately published 0x6C1C activation case. | SRC-REPO-PUBLICATION-AUDIT |

## Scope notes

- `ECU-EMM-EDISON` means the EMM in this vehicle; its executable firmware is unknown.
- `ECU-HU-MFD` means the vehicle head unit `259156244R` / `1ME0.001.45`; the FCC reference unit is different.
- `SHARED` means a diagnostic/CAN infrastructure statement, not a statement about one ECU.
- A level is attached to the exact statement; it is not a property of the document or the ECU.
