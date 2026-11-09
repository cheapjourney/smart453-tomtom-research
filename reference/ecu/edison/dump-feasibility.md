# EMM-T4 / EDISON — firmware dump feasibility

This page answers one question: **can the EMM's firmware be read completely?** It
separates the OBD2 path, the bench path, and the evidence that is missing.

## 1. OBD2 path

The examined diagnostic definition has no upload/download service, no
SecurityAccess service, and no routine-control service. The read services are
limited to identifiers the definition describes, and the configuration write service
does not read memory. There is therefore **no documented OBD2 full-flash read path**
in this definition.

This is not proof that the ECU cannot support such a service. A missing service in a
DDT definition is `UNCONFIRMED` for device-wide impossibility, not `CONTRADICTED`.
The head-unit and EMM definitions are separate; a finding on one does not transfer to
the other.

## 2. Bench path

The board's MCU is not confirmed. The forum candidates are `SPC560B54L` and
`SPC560B60L5`; neither is proven for this L4 board. No public board photo with a
readable MCU marking was found for `231A07278R`, and no external flash is documented
for this EMM. If the fitted device is an SPC560B family MCU, the family reference
manual describes code flash of 768 KB (B54), 1 MB (B60), or 1.5 MB (B64) plus 64 KB
data flash; censorship protection covers JTAG/Nexus and serial boot. Without the
64-bit password, a full flash read would require defeating that protection.

This project does not bypass censorship. A donor-bench dump is therefore plausible
only if:

- the donor MCU is uncensored, or
- the 64-bit password is known, or
- a documented, authorised read path exists.

None of those conditions is established. The bench route remains an `L5`
hypothesis, not a procedure.

## 3. What would make a dump possible

| Condition | Status | Consequence |
|---|---|---|
| Exact MCU and package identified | unknown | needed before any probe |
| Board schematic or confirmed test points | unknown | needed for a safe connection |
| Censorship state known | unknown | determines whether a read is possible |
| 64-bit password available lawfully | no | without it, no bypass is allowed |
| Documented bootloader read command | not found | serial boot is protected |
| Donor unit with the same part number | not acquired | bench-only, no vehicle risk |

## 4. What is not a dump

- The 295/443-byte all-configuration block is configuration, not firmware.
- The DDT JSON is a diagnostic definition, not executable code.
- The reprogramming-history record is a log, not a flash image.
- A read of an identification or configuration identifier is not a memory read.

Phase 6.7 confirmed the real 295-byte response payload (293 configuration bytes) and
462 decoded fields. It is a configuration baseline, not a flash image; it does not add
a memory-read service. See [`../../evidence/phase6-7-validation.md`](../../evidence/phase6-7-validation.md).

## 5. Risk and legal boundary

Reading a flash image from a unit the owner possesses may still be affected by
copyright, contract, and anti-circumvention rules. This reference documents the
technical barrier and does not provide a bypass. A donor unit does not remove the
legal question.

## 6. Open questions

- Is the fitted MCU an SPC560B54L, an SPC560B60L5, or another device?
- Is the censorship password set?
- Is there an authorised Renault/Bosch read or replacement procedure?
- Does a same-part donor exist, and is it readable without protection?
- Can the vehicle's own history record identify the installed software without a
  flash read?
