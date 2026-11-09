# Schemas

These JSON Schemas (Draft 2020-12) describe the data shapes used by the reference.
The public validator checks the public files against the subset of fields they use;
the full schemas are kept so that internal and public data remain comparable.

| Schema | Purpose |
|---|---|
| `claims.schema.json` | claim register |
| `evidence.schema.json` | evidence register |
| `source.schema.json` | source register |
| `ecus.schema.json` | ECU identity records |
| `diagnostics.schema.json` | diagnostics matrix |
| `configuration.schema.json` | configuration matrix |
| `firmware_catalog.schema.json` | firmware/artifact metadata |
| `feasibility.schema.json` | dump feasibility |
| `measurement.schema.json` | measurement record |

The public data files are in [`../data/`](../data/). A schema validates shape, not
truth; evidence status and source quality are checked separately.
