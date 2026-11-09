# Configuration — introduction

Configuration data describes what a unit is allowed or expected to do. It is not
firmware, and reading a configuration value does not prove that the corresponding
function works.

This public reference describes **what the fields mean** and **what was observed**.
It does not publish a new write procedure. The only protocol frames in the public
repository belong to the already-published `0x6C1C` Android Auto case; that case is
linked, not duplicated here.

The two ECUs have separate configuration spaces. A field on the EMM is not a field
on the head unit. A field name in a DDT definition is not proof that the vehicle
accepts a write.
