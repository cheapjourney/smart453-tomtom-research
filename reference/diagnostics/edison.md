# EMM-T4 / EDISON — diagnostic service families

## 1. Definition basis

`EMM_EDISON_DDT2000_SW13_1_V1_3` has 237 requests and 2,111 data objects. The
identity tuple `8/414/C132/4022` matches one autoidents entry. The service counts
below describe the definition, not a vehicle capability test.

| Service family | Requests |
|---|---:|
| Diagnostic session control | 2 |
| ECU reset | 1 |
| Clear diagnostic information | 1 |
| Read DTC information | 6 |
| Read data by local identifier | 81 |
| Read data by identifier | 74 |
| Communication control | 1 |
| Input/output control | 25 |
| Write data by local identifier | 45 |
| Tester present | 1 |

There is no SecurityAccess, upload/download, or routine-control service in this
definition. The read services are limited to identifiers the definition describes.
The write service changes configuration data; it does not read memory. This is a
definition fact, not proof that the ECU lacks a service outside the definition.

## 2. Confirmed read

The base reference recorded one cornering-flag read. Phase 8.4 adds four more
archived EMM reads (identity, part number, cornering parameters, all-configuration),
for five EMM read observations in total. The Phase 6.7 raw payload is archived
privately; the public statements are derived facts. The data does not establish that
the cornering light works.

## 3. Definition-only items

The lighting configuration, reprogramming-history record, identification records,
and cornering parameter are present in the definition. The history and
identification reads were not performed on the vehicle. Their contents, and the
installed executable firmware, remain unknown.

The modern and legacy definition lines use different lighting blocks and different
write paths. They are not interchangeable. No write path is published here.

## 4. What the diagnostics do not establish

- A read of a configuration identifier is not a full memory read.
- A parameter being present is not proof that the vehicle has the hardware.
- A missing upload/download service is not proof that no bench read exists.
- A diagnostic definition is not a firmware image.
