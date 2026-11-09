# Diagnostics — introduction

This section describes **service families and what they can establish**, not
copy-paste request sequences. The full request catalogue is not published because the
DDT database's licence is unclear and because a complete recipe is outside the
repository's publication policy.

The public reference distinguishes:

- **what a definition contains** (a service family, a parameter, a length);
- **what a vehicle returned** (a read-only observation, with its scope);
- **what a write changed** (only the already-published `0x6C1C` case);
- **what remains unknown** (a missing service is not proof of impossibility).

The two ECUs are separate. A diagnostic finding on the EMM is not a head-unit
finding, and a head-unit CAN service is not automatically available on the EMM.

See [`edison.md`](edison.md) and [`headunit.md`](headunit.md).
