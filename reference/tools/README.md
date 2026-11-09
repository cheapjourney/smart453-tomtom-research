# Tools

## Public validator

```bash
python3 tools/validate_public.py
```

Run from the `reference/` directory. It uses only the Python standard library and
needs no vehicle, adapter, DDT database, or firmware image.

It checks:

- required files and data;
- evidence, source, and claim references, including the Phase 6.7 (8 evidence /
  7 claims) and Phase 8.4/8.5 (8 evidence / 9 claims) addenda;
- L1 measurement references and L2 artifact references;
- hardware/software scope;
- JSON/CSV structure and counts;
- blocked file types and oversized files;
- home paths, RFC 1918 addresses, MAC addresses, VIN patterns, credentials, and raw
  diagnostic pairs;
- relative Markdown links.

It writes `validation_report.json` and `VALIDATION_REPORT.md` in the current
directory and exits non-zero on an error.

## Limits

The validator checks the **public** data. It cannot rebuild the full 237/192 request
matrices without the private DDT database, and it cannot verify the Phase 6.7 raw
record because that record is private. Those limits are stated in
[`../methodology/reproducibility.md`](../methodology/reproducibility.md).
