# EMM-T4 / EDISON — firmware and software versions

## 1. The core distinction

There are two different questions:

1. **Which diagnostic definition matches the unit?**
   The identity tuple `8/414/C132/4022` matches
   `EMM_EDISON_DDT2000_SW13_1_V1_3`. This is an exact match in the DDT
   `autoidents` list.

2. **Which executable firmware is installed?**
   This is **unknown**. The definition is a JSON description of requests, data
   objects, and parameters. It contains no executable code and no calibration.

Phase 6.7 confirmed the definition match with a real read-only identity and a
295-byte response payload (293 configuration bytes) and 462 fields; raw data private.
That still does not
identify the executable firmware. See
[`../../evidence/phase6-7-validation.md`](../../evidence/phase6-7-validation.md).

A DDT name is therefore not a firmware version. A higher DDT number is not an update
recommendation.

## 2. Definition families examined

| Definition | Date | Requests | Data objects | Identity notes |
|---|---|---:|---:|---|
| `SW10_V2` | 2012 | 214 | 2,081 | older generation |
| `SW11_1_V1_4_7` | — | 216 | 2,100 | legacy lighting block |
| `SW11_1_V1_6_3` | — | 229 | 2,099 | modern lighting block |
| `SW12_V1_6` | 2014 | — | — | intermediate |
| `SW13_V1_3` | 2014 | 237 | — | predecessor |
| `SW13_1_V1_3` | 2016 | 237 | 2,111 | matches `8/414/C132/4022` |
| `SW14_V1_3` | 2015 | — | — | different identity set |
| `SW15_1_V1.0` | 2016 | — | — | different identity set |
| `SW15_2_V1_0` | 2017 | — | — | same data set as SW15_3 |
| `SW15_3_V1.0` | 2018 | 246 | — | nine requests added versus SW13_1 |
| `SW15_V1_1` | — | — | — | latest name in the examined set |

`SW13_1_V1_3` is newer than `SW14_V1_3` by file date. The DDT numbers are not a
chronological oder semantic update chain. The examined files are diagnostic
definitions, not firmware releases.

The `SW13_1_V1_3` definition has SHA-256
`f616f9bc73dab1626ef92ac2da9bbb19bc4ddd32f7d0341b255dfc5987d005af` and is
689,857 bytes. The comparison definition `SW15_3` has SHA-256
`d64edb4339a4275e18a2909989e10b7b3979a679699496b4477acea82eddc8b2`.

## 3. What changed between definitions

- `SW13` to `SW13_1`: 237 requests in both; two requests changed; no request added
  or removed. The all-configuration block grows by one byte; the lighting block
  grows by one byte.
- `SW13_1` to `SW15_3`: 237 to 246 requests; nine requests added; the
  all-configuration block grows from 295 to 443 bytes. These are definition
  differences, not proof of a firmware update.
- `SW15_2` and `SW15_3` have identical request and data sets in the examined files.

## 4. Public firmware-image search

No public firmware image for `231A07278R` was found. The Renault Reprog V191
archive is gated; no public index or confirmed EMM-T4 entry was found. This is a
negative search result, not proof that no image exists.

The definition's reprogramming-history objects (approval number, programming site,
tool reference, number/date/time of reprogramming, save marking, CRC) exist in the
JSON. They were **not read** from the vehicle; the installed history is unknown.

## 5. What would be needed for a real firmware answer

A read-only identification/history query on the vehicle would provide the installed
software identity if the relevant record is available. A bench read of a donor unit
would require a confirmed MCU, a confirmed read path, and no bypass of censorship.
Neither has been done.

See [`dump-feasibility.md`](dump-feasibility.md) for the dump paths and their limits.
