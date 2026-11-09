# Firmware artifacts — metadata only

This directory describes firmware and update artifacts without redistributing them.
The files themselves remain private; only sizes, hashes, formats, and independently
formulated findings are published.

## 1. EMM

| Artifact | Status | What it is |
|---|---|---|
| EMM executable firmware | not available | executable image and calibration unknown |
| DDT definition `SW13_1_V1_3` | analysed | diagnostic definition, not firmware |
| Public firmware image for `231A07278R` | not found | negative search, not proof of nonexistence |
| Renault Reprog V191 archive | gated | no public index or confirmed EMM entry |

The DDT definition has 237 requests and 2,111 data objects. Its SHA-256 is
`f616f9bc73dab1626ef92ac2da9bbb19bc4ddd32f7d0341b255dfc5987d005af`.

## 2. Head unit

| Artifact | Size | SHA-256 | Type |
|---|---:|---|---|
| `TOMTOM.000` | 479,879,168 B | `157e95d96d97ed3319d3663a3a231acef912bbd242a8240c1f7290d1667034fb` | ext3 delivery container |
| `system-update_3206684_all.ttpkg` | 453,884,542 B | `5b4e311ae6973cbd5678b2044d64f7e3860b909beadde70875ef344f1b02de19` | kernel + rootfs delta |
| rootfs delta | 451,162,156 B | `53cc2a62ac01edb74a7ed45f0b8dfa06fce1b3774c1e52a9958ecea86a58e1e4` | partial filesystem, not mountable |
| update descriptor | 711 B | — | descriptor, not an image |
| GPL platform source | 127,807,017 B | `ac2151c84ba9b26e81cd8959a73f34a4c85e4e7ccf055fee129a09ea69726392` | source archive |

The update package is not a full flash dump. It contains a kernel and a rootfs
delta, but no U-Boot, no DIAGSYS, no eMMC image, and no NOR image. The `TOMTOM.000`
container is a delivery container, not a dump.

## 3. What is not published

No vendor firmware, update package, extracted application, root filesystem, DEX/ODEX
file, NOR dump, eMMC dump, or proprietary database content is published. Hashes and
sizes are metadata; they do not grant rights to the underlying material.

See [`../ecu/edison/firmware.md`](../ecu/edison/firmware.md) and
[`../ecu/tomtom-headunit/firmware.md`](../ecu/tomtom-headunit/firmware.md).
