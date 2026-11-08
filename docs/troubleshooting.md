# Troubleshooting

Every entry below is a failure that actually occurred in this project, except
where marked **suspected**. Each one names the evidence, because a plausible cause
that was never confirmed is how people waste afternoons.

## Quick table

| Symptom | Cause | Confidence |
|---|---|---|
| Adapter visible, connection attempt dies after ~15 s | another Bluetooth client holds it | **cause confirmed** |
| Same, with no phone connected | adapter asleep or not powered | **cause suspected** |
| `/dev/cu.*` opens instantly, returns nothing | macOS serial-port object stopped initiating | **cause confirmed** |
| `NO DATA` on every request | adapter timeout shorter than the unit's answer | **cause confirmed** |
| Unit never answers at 500 kbit/s | adapter set to 250 kbit/s | **cause confirmed** |
| Write "does nothing", log looks fine | DDT4All in demo/editor mode | **cause confirmed** |
| Write rejected with `7F 2E 7F` | no after-sales session | **cause confirmed** |
| Write rejected with `7F 2E 12` | the unit does not accept the request in that form | **confirmed** (third party) |
| Configuration changed but menu unchanged | head unit caches the values until restart | **cause confirmed** |

---

## 1. A phone is holding the Bluetooth connection

**Cause confirmed.** The adapter accepts one client. A phone paired to it — usually
through an OBD app that reconnects in the background — keeps the link, and the
laptop's attempt fails.

How it looks:

```
device: OBDLink MX+ ... paired=true
Waiting for baseband connection ...          15.4 s
connectionStatusHandler callback ... error: 10
baseband connect rc=-536870186 (0xE00002D6)
```

The adapter stays visible and even reports a signal strength, which is what makes
this confusing: discovery works, connection does not.

Fix: turn Bluetooth off on the phone, or remove the adapter from the phone's paired
list. Then retry.

## 2. The adapter is asleep or unpowered

**Cause suspected** when no other client is connected and the symptom is the same page
timeout. The MX+ sleeps when the vehicle bus is idle; it wakes on bus traffic.

Try, in this order:

1. Ignition on — bus traffic wakes the adapter.
2. Unplug the adapter from the OBD socket and plug it back in. This is a power
   cycle, not a pairing action.
3. **Do not press the pairing button** to "wake" an adapter that already worked.
   That starts a new pairing and can invalidate the existing link key. The symptom
   afterwards is a connection that establishes and drops immediately, not a
   timeout.

## 3. macOS serial port opens but returns nothing

**Cause confirmed.** The persisted `/dev/cu.*` node for the adapter can stop initiating
connections after the first session while the adapter itself is healthy:

- `open()` succeeds in milliseconds,
- every read returns zero bytes at any baud rate,
- the system log shows no ACL connection attempt at all,
- the adapter still answers when the RFCOMM channel is opened directly.

The fix is the bridge in `04-obdlink-connection.md`, not a driver and not a
re-pair.

## 4. Adapter timeout is too short

**Cause confirmed.** With the factory default the unit's answer never arrives:

```
ATAT1 / STPTO not set  →  default 102 ms  →  NO DATA
ATAT0 + STPTO 2000     →  2 s window      →  62 6C 1C 38  (after ~2.05 s)
```

`NO DATA` therefore means "no answer within the adapter's window", not "the unit
does not answer". If you see it, check the timeout before doubting the car.

## 5. Wrong CAN speed

**Cause confirmed.** DDT4All decides the speed from the vehicle description and picks
250 kbit/s for the MFD v4.6 file (its metadata says `baudrate: 10400`, which the
program reads as a 250k hint). With 250 kbit/s on a 500 kbit/s bus nothing answers.

Evidence from DDT4All's own command sequence: in *Auto* mode it sends `AT SP 8`
(250 kbit/s); with the CAN line set explicitly to 500 it sends `AT SP 6`.

The tools in this repository always send `STP 33` — ISO 15765, 11-bit, 500 kbit/s.

## 6. DDT4All in demo/editor mode

**Confirmed**, both in the code and by reproduction. In demo mode the write path
prints log lines that look like a successful exchange but puts nothing on the bus.

Reproduced with a mock ECU and DDT4All's own request code:

```
demo/editor mode  : 0 frames reached the ECU
connected mode    : 1 frame  (2E 6C 1C 78)
```

If a guide's write "does nothing", check which mode the connection dialog is in
before assuming the car refused.

## 7. Missing after-sales session

**Confirmed** on this unit. Without a session, the write is refused:

```
2E 6C 1C 78  →  7F 2E 7F   serviceNotSupportedInActiveSession
```

With `10 C0` it is accepted. The session requirement is confirmed for this unit at
its software version; other units may differ.

## 8. Negative response codes

| NRC | Name | What it means here |
|---|---|---|
| `7F` | serviceNotSupportedInActiveSession | wrong session — see above |
| `12` | subFunctionNotSupported / invalid format | the unit rejects the request in that form; reported by a third party for a different payload (`2E 6C 1C C4`) |
| `22` | conditionsNotCorrect | a precondition is not met; nothing to guess at |
| `31` | requestOutOfRange | the identifier is not writable on this build |
| `33` | securityAccessDenied | would require a seed/key exchange — not implemented here, by design |

A negative response means the request was **not executed**. Do not retry blindly;
change exactly one thing and record which.

## 9. Configuration changed, menu unchanged

**Cause confirmed.** The head unit caches the vehicle configuration in a local database
and refreshes it at startup or when the vehicle side signals a finished
end-of-line write. A diagnostic write does neither.

Restart the head unit and check again. Re-read `0x6C1C` first: if it is still the
new value, the software simply has not reloaded it; if it reverted, the write was
not stored.

## 10. Everything reads fine but the identity is wrong

Different part number — stop. See `05-headunit-identification.md`. This project has
data for one part number only.
