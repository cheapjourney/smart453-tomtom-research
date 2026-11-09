# TomTom 1ME09 — dump feasibility

## 1. OBD2 path

The MFD v5.4 definition has no upload/download, SecurityAccess, or routine-control
service. Its reads are limited to identifiers the definition describes; its write
and IO-control services change configuration or stimulate functions, not read flash.
There is therefore **no documented OBD2 full-flash read path** in this definition.

This is not proof that the device cannot support such a service. The claim “OBD2 can
dump the MFD” is `UNCONFIRMED`; the claim “a documented OBD2 dump path exists” is
`CONTRADICTED`.

A second limitation is physical: the multimedia CAN is commonly reported on OBD pins
12/13 of Renault vehicles, but for this Smart 453 no continuity or pin measurement
confirms it. Without that access, even a hypothetical service would not be reachable
through the standard OBD pins.

## 2. Offline update path

The official update package can be analysed offline. It provides a kernel and a
rootfs delta, but it is not a full image. The delta has journal/inode damage and
invalid DEX entries. It is enough to study parts of the software, not to reconstruct
the factory flash.

The `TOMTOM.000` ext3 container is a delivery container. It is not a NOR or eMMC
image.

## 3. Bench path

A bench dump would require one of:

- a confirmed NOR read (4 MiB CFI device at `0x08000000`),
- a confirmed eMMC read,
- a confirmed U-Boot/DIAGSYS recovery path,
- a confirmed UART console and a way to stop the bootloader.

None of these is established for the vehicle board. UART3/ttyO2 is a candidate; the
FCC board's test points are not proven to match. A bench attempt on a donor unit is
plausible, but it is not a documented procedure and it is not part of this reference.

## 4. What would change the answer

| Missing item | Why it matters |
|---|---|
| Vehicle-board photograph and test points | confirms whether the FCC layout applies |
| UART console confirmation | provides a recovery path and bootloader access |
| NOR/eMMC read attempt on a donor | establishes whether a dump is technically possible |
| Complete base rootfs | needed for a full software image, not just a delta |
| Confirmed multimedia-CAN pins | needed for any OBD-side service |

## 5. Risk and legal boundary

A flash read is not automatically harmless: it may violate copyright, contract, or
anti-circumvention rules, and a physical probe can damage the board. This reference
describes the barriers and does not provide a bypass or a probe recipe.

## 6. Open questions

- Is the vehicle board the same as the FCC `TN4D` board?
- Is the NOR device readable in circuit, or only on a removed/bench unit?
- Is the eMMC accessible, and is it encrypted?
- Is UART3/ttyO2 the console, and where is the test point?
- Does a signed full image exist anywhere, or only deltas?
- Are pins 12/13 connected to the multimedia CAN on this vehicle?
