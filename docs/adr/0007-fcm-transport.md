# 0007. FCM high-priority data messages from PC to phone

* **Status:** Accepted
* **Date:** 2026-10-30
* **Source:** spec §4.8, §7.1 · qna Q4.4, Q9.2, Q10.2 · research R-8, R-9

## Context

* The phone must be woken within about a second, including in Doze and on Xiaomi HyperOS.
* The transport must be free.
* Telegram as a backbone would need a second Telegram client on the phone: bots can't see other bots' messages, and
  Telegram's push only wakes the Telegram app.
* FCM may downgrade high-priority messages that don't result in a user-visible notification, judged over 7 days per
  app instance.

## Decision

* The PC publishes **FCM high-priority data messages** (Firebase free tier, HTTP v1 API, service account kept locally)
  to a **single topic** for all of Ukraine.
* Urgent kinds go out immediately; others are coalesced for ≤1 s.
* Every message has a TTL. Heartbeats and periodic snapshots go over the same channel.
* The phone updates a **silent ongoing notification** on every message so the messages stay "user-visible".

## Consequences

* No server to run, no cost, and the most reliable wake-up path Android offers.
* The phone needs Google Play Services, which the target phones have.
* Every message wakes every phone, even for far-away threats. If battery use or deprioritisation becomes a problem,
  split into per-oblast topics; that only changes where records are published.
* Whether ongoing-notification updates count as visible must be confirmed in a spike.
* The transport is one-way, hence snapshots for recovery.

## Alternatives considered

* **Telegram private channel.** Needs a Telegram client on the phone.
* **Self-hosted push (ntfy/UnifiedPush/WebSocket over Tailscale).** Needs a persistent connection that Doze and
  HyperOS tend to kill. Kept as an option for a later "active threat" live stream.
* **SMS.** Parked. Needs a GSM path at home.
