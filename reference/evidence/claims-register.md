# Claim register

This is the hardened base claim set (19). The Phase 6.7 addendum adds 7 claims in
[`phase6-7-validation.md`](phase6-7-validation.md); the Phase 8.4/8.5 addendum adds
9 claims in [`phase8-4-consolidation.md`](phase8-4-consolidation.md). A claim is a
statement under test, not a proven fact; the status is the result of the Phase 8.3
review.

| ID | Claim | Status | Evidence | Explanation |
|---|---|---|---|---|
| `CLM-001` | MFD v5.4 ist die installierte Firmwareversion. | CONTRADICTED | EV-HU-004;EV-HU-005 | MFD v5.4 ist eine DDT-Diagnosedefinition (2019-02-28), keine Firmware. Die Anwendungsversion ist 11.346.3206684-8060. |
| `CLM-002` | Das 3206684-Updatepaket ist ein vollständiger Flash-Dump. | CONTRADICTED | EV-HU-009;EV-HU-010;EV-HU-011 | Es enthält zImage und ein RootFS-Blockdelta, kein U-Boot, kein DIAGSYS, kein eMMC-/NOR-Abbild. |
| `CLM-003` | Über OBD2 lässt sich das MFD vollständig dumpen. | UNCONFIRMED | EV-HU-006;EV-HU-007 | No documented OBD2 path for a full MFD dump was found. The DDT definition lacks upload/download and routine-control services, but absence in a definition does not prove that the device cannot support such a service. Multimedia-CAN access is also unconfirmed. |
| `CLM-004` | Android Auto ist nur ein verstecktes Konfigurationsbit. | UNCONFIRMED | EV-HU-002;EV-HU-015 | The 0x40 bit and Android Auto components are documented. Completeness of the stack and USB projection with a phone were not tested. |
| `CLM-005` | CarPlay lässt sich per Codierung aktivieren. | UNCONFIRMED | EV-HU-015;EV-HU-016 | No CarPlay/AirPlay stack was found in the analyzed, incomplete artifacts; iAP2 media components are present. Absence in an incomplete image does not prove absence on the device. An Apple MFi/installation right is not documented. |
| `CLM-006` | 259154108R und 259156244R sind identische Hardware. | UNCONFIRMED | EV-HU-017;EV-HU-018;EV-HU-019 | Gleiche 1ME09/MFD2.x-Familie, unterschiedliche Teilenummern; laut TomTom unterscheiden sie sich in SW-Aspekten. Board-Gleichheit ist nicht belegt. |
| `CLM-007` | Das Smart Media System ist ein umgelabeltes R-Link-1-Gerät. | UNCONFIRMED | EV-HU-017;EV-HU-024 | Community-Aussage; die exakte Identität ist TomTom 1ME09/Strasbourg. Eine Hardware-/Software-Gleichsetzung ist nicht belegt. |
| `CLM-008` | 231A07278R ist die Firmwareversion SW13_1. | CONTRADICTED | EV-EMM-003;EV-EMM-012 | 231A07278R ist eine Teilenummer; SW13_1_V1_3 ist eine Diagnosedefinition. Die ausführbare Firmware ist unbekannt. |
| `CLM-009` | SW15 ist neuer und besser als SW13_1. | UNCONFIRMED | EV-EMM-013;EV-EMM-014 | DDT-Namen sind nicht chronologisch; SW13_1 ist jünger als SW14_V1_3; 2015er Fahrzeug mit SW15, 2020er Ersatzteil mit SW13_1. |
| `CLM-010` | Renault Reprog V191 enthält ein vollständiges 231A07278R-Image. | UNCONFIRMED | EV-EMM-015 | Kein öffentlicher Index, kein Eintrag belegt; V191 ist gated und nicht heruntergeladen. |
| `CLM-011` | The cornering-flag read at the EMM returned 0. | CONFIRMED | EV-EMM-001 | Phase 6.7 archived read-only observation; raw record is private. The derived flag value is 0. |
| `CLM-012` | Der ausgelesene Cornering-Konfigurationswert ist 0; die Funktionsimplementierung ist unbekannt; die tatsächliche Abbiegelichtfunktion wurde nicht getestet. | NOT_TESTED | EV-EMM-001;EV-EMM-006 | EV-EMM-001 bestätigt den ausgelesenen Wert 0; EV-EMM-006 ist eine L3-Definition und ausdrücklich NOT_TESTED. Die Definition belegt keine physische Funktion. |
| `CLM-013` | 259156244R ist die Teilenummer des Fahrzeug-Headunits. | CONFIRMED | EV-HU-001;EV-HU-017 | Read-only part-number query at the vehicle plus the TomTom certification. |
| `CLM-014` | Das FCC-Board TN4D ist das Board des Fahrzeugs. | UNCONFIRMED | EV-HU-018;EV-HU-019 | FCC-Gerät ist 259154108R/1ME0.001.27, Fahrzeug 259156244R/1ME0.001.45; Board-Gleichheit nicht belegt. |
| `CLM-015` | Der Multimedia-CAN liegt am Smart 453 sicher auf OBD Pin 12/13. | UNCONFIRMED | EV-SHARED-001 | Renault-Allgemeinwissen; für dieses Fahrzeug keine Kontinuitäts-/Pin-Messung. Kein automatischer Buswechsel. |
| `CLM-016` | The installed build is exactly 3206684. | UNCONFIRMED | EV-HU-003;EV-HU-004;EV-HU-020 | The version screen names 3206684; the identity record does not encode the exact build, and 3168863 remains a possibility. |
| `CLM-017` | CarPlay is absent from the device. | UNCONFIRMED | EV-HU-015;EV-HU-016 | No CarPlay stack was found in the analyzed artifacts, but the image is incomplete. Absence on the whole device is not proven. |
| `CLM-018` | A full EMM flash dump is impossible over OBD2. | UNCONFIRMED | EV-EMM-004;EV-EMM-018 | No documented OBD2 full-flash path exists in the examined definition; this is not proof that no service or bench path exists. |
| `CLM-019` | The public repository excludes all raw diagnostic hex. | CONTRADICTED | EV-PUB-001 | The repository deliberately published the 0x6C1C activation frames in the 2026-11-08 case. The exclusion is limited to other identifiers and to raw logs. |

## Status changes from Phase 8.2

- `CLM-003` changed from `CONTRADICTED` to `UNCONFIRMED`: no documented OBD2 dump path is not proof of impossibility.
- `CLM-005` changed from `CONTRADICTED` to `UNCONFIRMED`: no CarPlay code in an incomplete image is not proof of device-wide absence.
- `CLM-016` to `CLM-019` were added during the hardening review.
