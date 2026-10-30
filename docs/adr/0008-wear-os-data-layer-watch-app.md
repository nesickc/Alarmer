# 0008. Own Wear OS app over the Data Layer for watch alerts

* **Status:** Accepted
* **Date:** 2026-10-30
* **Source:** spec §7.2, §8 · qna Q2.1, Q2.3, Q7.5, D13 · research R-8

## Context

* The watch is the main output (Galaxy Watch 7 paired with a Xiaomi phone).
* Bridged phone notifications all vibrate the same way, so threat levels can't be told apart by feel.
* We need acknowledge, shelter mode and open-on-phone actions.
* The phone should vibrate only when the watch isn't connected.

## Decision

* Build a **Wear OS app** (Wear OS 5+).
* It receives alerts from the phone over the Wear OS **Data Layer `MessageClient`**: Bluetooth, no internet, free.
* The watch app owns the **per-level vibration waveforms**, the L4 full-screen alert that repeats until acknowledged,
  and the actions.
* The phone checks that the watch app is reachable before sending. If it isn't, the phone vibrates itself. Phone
  notifications for alerts the watch handles are local-only, so the watch doesn't buzz twice.

## Consequences

* Distinct patterns per level, and full control of repetition and actions.
* Two apps to build and sideload. Watch and phone settings (shelter mode) must stay in sync.
* Without the watch app installed, bridged notifications still work as a degraded mode.
* Only Wear OS watches are supported. Garmin and others would need their own SDKs.

## Alternatives considered

* **Bridged notifications only.** One vibration for everything; this is just the fallback.
* **Samsung Accessory SDK.** Samsung-specific, and not needed when the Data Layer works across Wear OS.
