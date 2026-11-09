# Public data

| File | Contents |
|---|---|
| `evidence.json` | 44 hardened base evidence statements, levels, statuses, source IDs, scopes, residual uncertainty |
| `claims.csv` | 19 base claims under test |
| `sources.csv` | 41 base sources with class, availability, access status, publication decision |
| `counts.json` | Aggregate counts for the public reference |
| `firmware_metadata.csv` | Public-safe artifact metadata and hashes |
| `obd_dump_feasibility.csv` | Method-level dump feasibility |
| `phase6_7_evidence.json` | 8 derived Phase 6.7 evidence entries |
| `phase6_7_claims.csv` | 7 Phase 6.7 claims |
| `phase6_7_sources.csv` | 2 private-source metadata entries |
| `phase6_7_counts.json` | Phase 6.7 counts and private-data list |
| `phase8_4_evidence.json` | 8 Phase 8.4/8.5 derived evidence entries |
| `phase8_4_claims.csv` | 9 Phase 8.4/8.5 claims |
| `phase8_4_sources.csv` | 1 private-source metadata entry |
| `phase8_4_counts.json` | 429-command, 9-L1 and 293/295 counts |

The data is a derived public view. Raw logs, raw frames other than the already
published `0x6C1C` case, internal locators, and artifact contents are not included.

Source availability values:

- `public` — a public URL or public document is available;
- `gated` — a login/paywall/403 blocks access;
- `dead` — the URL currently fails;
- `internal` — listed for provenance only; content not published.
