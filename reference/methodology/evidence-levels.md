# Evidence levels and statement scoping

The reference uses levels for the **kind of support** and statuses for the **degree
of establishment**. A statement gets one level and one status; the level never
spills over to a neighbouring statement.

## 1. Levels

| Level | Name | Typical support | Minimum requirement |
|---|---|---|---|
| **L1** | Vehicle verified | A read or observation on the vehicle | An archived measurement, or an explicit measurement reference and a stated archive gap |
| **L2** | Artifact verified | Firmware image, package, definition, hash, parse | A named artifact, a hash or stable reference, and a reproducible method |
| **L3** | Definition only | A DDT parameter or service is defined | The definition name and the exact parameter/request identifier |
| **L4** | External report | Manufacturer document, regulator filing, forum, community | Author, date if known, URL or document identifier, and the exact claim |
| **L5** | Hypothesis | Conditional inference, proposed mechanism | The condition, the missing observation, and what would falsify it |

## 2. Statuses

| Status | Meaning |
|---|---|
| `CONFIRMED` | The statement is supported at its stated scope and no known contradiction remains |
| `UNCONFIRMED` | The statement is plausible or reported, but the required independent support is missing |
| `CONTRADICTED` | A statement with the same scope is contradicted by stronger evidence |
| `NOT_TESTED` | The action or observation was not performed |
| `NOT_APPLICABLE` | The statement does not apply to the object in question |

`UNCONFIRMED` is not a synonym for “false”. A negative search, an incomplete image,
or a missing service in a definition produces `UNCONFIRMED`, not `CONTRADICTED`.

## 3. Scoping examples

- A confirmed **read** of the cornering flag is not a confirmed **write** and not a
  confirmed **function**.
- A DDT parameter named `Nbx_Cornering_CF` proves that the parameter exists in the
  definition; it does not prove that the vehicle has the hardware or that the light
  works.
- A DDT definition named `SW13_1_V1_3` is not the executable firmware.
- A `3206684` update package is a delta; it is not a full flash dump.
- A string in an incomplete root filesystem is not proof of a working
  implementation.
- A service missing from a DDT definition is not proof that the ECU cannot support
  it.
- A missing CarPlay code path in an incomplete image is not proof that the whole
  device lacks CarPlay.

## 4. Correction policy

Corrections are not silent. Every change from the Phase 8.2 registry is recorded in
the Phase 8.3 evidence audit and change log. The original statement, the hardened
statement, the old and new level/status, the reason, and the publication decision are
kept side by side.

The most important corrections in this reference are:

- the EMM cornering read is an **archived private Phase 6.7 measurement**; its raw
  record is not public and the public statement is derived;
- the dealer/parts attribution of the EMM variant is `UNCONFIRMED`;
- the community report about a 2020 replacement EMM is `UNCONFIRMED`;
- the UART3/ttyO2 console is a **candidate**, not a confirmed test point;
- Android Auto/MirrorLink components are **present**, but completeness and function
  are not proven;
- no CarPlay stack was found in the **incomplete** artifacts, but device-wide absence
  is not proven;
- a full OBD2 dump is **not documented**, not proven impossible;
- the public repository's “no raw hex” rule is limited by the already-published
  `0x6C1C` case.
