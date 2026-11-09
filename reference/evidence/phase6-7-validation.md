# Phase 6.7 — real-vehicle validation addendum

This addendum integrates the validated Phase 6.7 findings without publishing the
private vehicle record. The raw 295-byte response payload — 293 configuration data
bytes after the two-byte positive-response header — its hash, the 462 individual raw
values, the V5.1 matrix, and the Phase 6.7 working reports remain private.

## 1. What was added

| Item | Result |
|---|---|
| Phase 6 evidence archive | 87 SHA-256 entries verified |
| Real all-configuration read | 295-byte response payload, of which 293 bytes are configuration data; 462 decoded fields |
| Independent iMac decoder | 0 differences against the MacBook evaluation |
| Reconstructed payloads | 5/5 byte- and hash-identical |
| Cornering flag | 0 in both the single-flag read and the all-configuration record |
| Front fog configuration | flag 1; PWM active; hardware owner-reported |
| Cornering parameters | A1 60°, A2 15°, speed 40 km/h; dimming raw 220 |
| V4→V5 regression | 54 rows; 33 shared columns; 0 known values lost |
| V5.1 | provenance column only; no new technical values |

The raw record is **not** a firmware image and is not published.

## 2. Evidence

| ID | Level | Status | Statement | Sources |
|---|---|---|---|---|
| `EV-P67-001` | L1 | CONFIRMED | A real read-only all-configuration read returned a 295-byte response payload including the two-byte positive-response header; 293 bytes are configuration data and decode to 462 fields. Raw record/hash/values private. | `SRC-PHASE67` |
| `EV-P67-002` | L1 | CONFIRMED | The cornering flag is 0 in both the single-flag read and the all-configuration record. | `SRC-PHASE67` |
| `EV-P67-003` | L1 | CONFIRMED | Front-fog configuration is 1; PWM configuration is active; electrical function is not proven. | `SRC-PHASE67` |
| `EV-P67-004` | L1 | CONFIRMED | A1 = 60°, A2 = 15°, speed = 40 km/h, dimming raw 220; 2.2 s only at 0.01 s/LSB. | `SRC-PHASE67`, `SRC-DDT-EMM-SW13_1` |
| `EV-P67-005` | L2 | CONFIRMED | 20 fields outside documented ranges: 0 proven definition errors, 14 probable scaling/offset errors, 6 unresolved. | `SRC-PHASE67`, `SRC-DDT-EMM-SW13_1` |
| `EV-P67-006` | L2 | CONFIRMED | V4→V5: 54 rows, 33 shared columns, 0 known values lost, 62 expected changes; menu-visible evidence retained; V5.1 documented. | `SRC-PHASE67-V51`, `SRC-MATRIX-V4` |
| `EV-P67-007` | L3 | NOT_TESTED | The single-flag write definition is fixed-value, no read-modify-write, no explicit save/commit/reset; not executed. | `SRC-DDT-EMM-SW13_1` |
| `EV-P67-008` | L5 | UNCONFIRMED | Persistence, LID-7F update, rollback and electrical function are unproven; no write was performed. | `SRC-PHASE67` |

Machine-readable: [`../data/phase6_7_evidence.json`](../data/phase6_7_evidence.json).

## 3. Claims

| ID | Claim | Status | Evidence |
|---|---|---|---|
| `CLM-P67-001` | The real EMM all-configuration response is 295 payload bytes, of which 293 are configuration data; it decodes to 462 fields. | CONFIRMED | `EV-P67-001` |
| `CLM-P67-002` | The cornering flag is 0 in both reads. | CONFIRMED | `EV-P67-002` |
| `CLM-P67-003` | The front fog lamps are configured. | CONFIRMED | `EV-P67-003` |
| `CLM-P67-004` | The front fog lamps are electrically functional. | NOT_TESTED | `EV-P67-003`, `EV-P67-008` |
| `CLM-P67-005` | V5 lost Android Auto/MirrorLink menu visibility. | CONTRADICTED | `EV-P67-006` |
| `CLM-P67-006` | A cornering write is safe, persistent and activates the function. | UNCONFIRMED | `EV-P67-007`, `EV-P67-008` |
| `CLM-P67-007` | The executable EMM firmware is SW13_1_V1_3. | UNCONFIRMED | `EV-P67-001` |

Machine-readable: [`../data/phase6_7_claims.csv`](../data/phase6_7_claims.csv).

## 4. Interpretation

- The real vehicle identity matches the `SW13_1_V1_3` **diagnostic definition**;
  it does not prove the executable firmware version.
- The configuration is read and reproducible; 295 bytes are the response payload
  including the two-byte positive-response header, and 293 bytes are configuration
  data. The function is not tested.
- The 295-byte response payload (293 configuration data bytes) improves the
  configuration baseline and rollback basis, not the firmware-readability picture.
- The V5.1 matrix is a documentation correction; it does not promote any function
  to “practically working”.
- The raw record and its values stay private because the combination is a
  vehicle-specific configuration fingerprint.
