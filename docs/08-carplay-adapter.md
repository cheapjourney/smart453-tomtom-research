# 08 — CarPlay over an adapter

**Status: NOT TESTED.** Nothing in this chapter has been verified. It describes a
plan, not a result.

## The starting point

The head unit has **no CarPlay stack**. Its firmware contains two projection
implementations — MirrorLink and Android Auto — and no AirPlay or CarPlay code.
That is an offline finding from the vendor's own update image, not an opinion.

Android Auto, however, is now enabled on the research vehicle: the configuration
byte carries the Android Auto bit and the menu shows the entries (see
`07-verification.md`, levels 1–3).

## The idea

Several products present themselves to a head unit as an **Android Auto phone**
while actually running CarPlay towards the iPhone. The proposal for this project
is a **Carlinkit T-Box Lite S, 4+32 GB**:

```
iPhone  ── wireless CarPlay ──▶  T-Box  ── USB, Android Auto (AOA) ──▶  head unit
```

The head unit sees an Android Auto device, which is exactly what its stack
expects. The T-Box does the protocol translation.

## What has to be true for this to work

Each item below is unverified. If any one fails, the chain fails.

| # | Requirement | Status |
|---|---|---|
| 1 | Wired Android Auto projection works with a plain phone | **NOT TESTED** — the precondition for everything else |
| 2 | The unit recognises the T-Box as an Android Auto accessory | **NOT TESTED** |
| 3 | The T-Box accepts the unit's USB power and enumeration | **NOT TESTED** |
| 4 | Wireless CarPlay between iPhone and T-Box establishes | **NOT TESTED** |
| 5 | Touch input reaches CarPlay | **NOT TESTED** |
| 6 | Audio playback works | **NOT TESTED** |
| 7 | Microphone input works (call audio) | **NOT TESTED** |
| 8 | Navigation audio mixes correctly with the unit's own sources | **NOT TESTED** |
| 9 | The connection survives reconnects and ignition cycles | **NOT TESTED** |

## Why step 1 comes first

If a plain Android phone cannot project over USB, the T-Box cannot either. Testing
the adapter before the base function works is the fastest way to misattribute a
failure to the adapter.

## What to check when it is tried

- Does the head unit show an Android Auto device while the T-Box is connected?
- Does the T-Box LED indicate CarPlay or Android Auto mode? The device has a mode
  switch; the wrong mode looks like "not recognised".
- Is the T-Box powered from the unit's USB port or does it need external power?
- Does the iPhone see the T-Box's Wi-Fi network?
- After a reconnect, does the unit still show the projection?

## Honest expectations

- A menu entry is not a working projection; a recognised device is not a working
  CarPlay session.
- Even a working session may be limited: the head unit's screen is small, its
  input is a touch panel of its own design, and the audio path goes through the
  unit's mixer.
- Vendors of such boxes change firmware without notice; a model that worked in
  someone else's car may behave differently in this one.

## Publication rule

This project will publish a CarPlay result only after it has been observed on the
vehicle, with the same evidence standard as the Android Auto activation: what was
connected, what the unit showed, what worked, what did not. Until then this chapter
stays **NOT TESTED**.
