# Research gaps and next read-only steps

## 1. EMM

| Gap | Why it matters | Minimum next step |
|---|---|---|
| Executable firmware/calibration unknown | DDT definition is not firmware | read-only identification/history records; no write |
| MCU/package unknown | determines flash size and debug path | board inspection or manufacturer documentation |
| Censorship state unknown | determines whether a bench read is possible | documented service information; no bypass |
| No donor unit | bench read unproven | same-part donor, bench-only |
| Cornering hardware unknown | flag `0` does not prove function | physical inspection and a function test |
| Reprogramming history unread | could identify software lineage | read-only history record |

## 2. Head unit

| Gap | Why it matters | Minimum next step |
|---|---|---|
| Exact build/update history | version screen and identity record are not a build ID | read-only build query or signed package inspection |
| Vehicle board vs FCC board | test points and memory layout may differ | board photograph and part comparison |
| UART console unconfirmed | recovery and bootloader access | locate and confirm a test point; no destructive probe |
| NOR/eMMC dump unproven | full image absent | donor-bench read attempt |
| Projection untested | menu visibility is not function | phone/USB projection test, read-only |
| CarPlay absence unproven | incomplete image | complete image or device-level test |
| Multimedia-CAN pins unconfirmed | OBD-side access uncertain | continuity/pin measurement |

## 3. Shared

| Gap | Why it matters | Minimum next step |
|---|---|---|
| No public raw log | L1 raw records are private; only derived statements are public | keep the private archive hashed and re-verified before permanent reliance |
| Gateway topology unconfirmed | CAN paths may differ | read-only network documentation or measurement |
| No independent reproduction | single-vehicle research | second owner/unit with the same part numbers |

## 4. What not to do next

- Do not write a configuration value to test a hypothesis.
- Do not attempt a flash read by bypassing censorship.
- Do not apply a value or procedure from another part number.
- Do not treat a missing service in a DDT definition as proof of impossibility.
- Do not publish raw logs, VIN records, adapter identifiers, or vendor binaries.

## 5. Next read-only validation (post-8.4)

Phase 8.4 completed without a new vehicle measurement. The nine existing L1 events
are archived and hashed. A future repeat would only test reproducibility and would
need:

1. confirmed vehicle readiness and a parked vehicle;
2. an explicitly approved, unchanged read-only allowlist;
3. one request at a time, no retry and no session change;
4. private raw archiving with timestamp and hash;
5. public reporting of derived facts only.

No write, no session change, no SecurityAccess, no flash attempt.
