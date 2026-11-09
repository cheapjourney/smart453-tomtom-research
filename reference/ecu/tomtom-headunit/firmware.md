# TomTom 1ME09 — firmware and update artifacts

## 1. Software identity

| Item | Value | Basis |
|---|---|---|
| Application version | `11.346.3206684-8060` | version screen |
| Build | `3206684` | version screen / package name |
| Platform source | `3198575` | GPL platform source |
| Android | 2.2 / API 8 | build properties |
| Kernel | 2.6.32.9 | build properties |
| Product | `TomTom Strasbourg` | build properties |
| SoC | TI OMAP3 / OMAP35xx, ARMv7 | hardware/source analysis |

The version screen is a direct observation. The identity record is not a build
identifier; the exact build and the update history are `UNCONFIRMED`.

## 2. Artifacts examined

| Artifact | Size | SHA-256 | What it is |
|---|---:|---|---|
| `TOMTOM.000` | 479,879,168 B | `157e95d96d97ed3319d3663a3a231acef912bbd242a8240c1f7290d1667034fb` | ext3 delivery container |
| `system-update_3206684_all.ttpkg` | 453,884,542 B | `5b4e311ae6973cbd5678b2044d64f7e3860b909beadde70875ef344f1b02de19` | kernel image + rootfs block delta |
| rootfs delta | 451,162,156 B | `53cc2a62ac01edb74a7ed45f0b8dfa06fce1b3774c1e52a9958ecea86a58e1e4` | partial filesystem, damaged journal/inodes |
| update descriptor | 711 B | — | package descriptor, not a full image |
| GPL platform source | 127,807,017 B | `ac2151c84ba9b26e81cd8959a73f34a4c85e4e7ccf055fee129a09ea69726392` | source archive, not a flash image |

The `TOMTOM.000` container is not a flash dump. The `.ttpkg` is an update, not a
complete image: it contains a kernel and a rootfs delta, but no U-Boot, no DIAGSYS,
no eMMC image, and no NOR image.

The rootfs delta is not a complete, mountable root filesystem. It has journal and
inode damage, and some DEX files are invalid. A missing file or class in this delta
is not proof that the whole device lacks it.

## 3. Update and signature model

The update uses a job list and signed manifests (`jobs.xml`, its signature, and a
file signature). The project found a signature-verification path; the presence of a
verifier does not prove that every update path enforces it. No signature was broken
and no encryption was removed.

The package is a **delta**: it can update a matching base system, but it cannot
reconstruct the complete factory image. The 711-byte file sometimes described as an
“update” is only a descriptor.

## 4. Boot and recovery context

The board has a 4 MiB parallel CFI NOR device on GPMC chip-select 0 at
`0x08000000`; the DIAGSYS region is `0x08300000`–`0x083FFFFF`. U-Boot and a
factory/recovery diagnostic server are part of the platform. The UART3/ttyO2 console
is a candidate, not a confirmed test point.

ADB is gated by the device-class property loaded through the FDT; without
`device-class=1`, adbd remains off. No ADB session or root filesystem extraction is
part of this public reference.

## 5. What is not available

- No complete root filesystem.
- No NOR dump.
- No eMMC dump.
- No U-Boot image from the vehicle unit.
- No confirmed vehicle-board photograph or test point.

The FCC reference unit's board and software are not the vehicle unit. Transferring
its memory layout or test points without a board-level comparison would be an
unsupported leap.

## 6. Open questions

- Exact installed build and update chain.
- Whether the delta can be applied to the current base without a full image.
- Whether the NOR/eMMC can be read on a bench.
- Whether the UART console is exposed and where.
- Whether the FCC board is the same board as the vehicle unit.
