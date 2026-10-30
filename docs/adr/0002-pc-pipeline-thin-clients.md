# 0002. A PC pipeline does all processing; phone and watch are thin clients

* **Status:** Accepted
* **Date:** 2026-10-30
* **Source:** spec §2, §4 · qna Q2.2, Q4.2, Q4.3, Q8.3, Q10.1

## Context

* Reading Telegram needs a long-lived MTProto connection, parsing needs an LLM, and fusion needs state across many
  channels.
* On a phone, all of this fights Doze, OEM battery killers (Xiaomi HyperOS) and Android 15 foreground-service limits.
  There is also no on-device model that can run in the background with good Ukrainian (Gemini Nano is foreground-only).
* A cloud server costs money; the target is $0/month.
* The developer has an always-on laptop with a 6 GB GPU, on home backup power with a UPS-backed router, and the
  provider isn't affected by outages.

## Decision

* The **laptop runs the whole pipeline**: ingest, filter, fast path, LLM, gazetteer, track fusion, publishing.
* It broadcasts **every** target record to every device.
* The **phone decides relevance** locally from its own location and settings.
* The **watch** only presents alerts and takes actions.

## Consequences

* User location never leaves the phone. The PC needs no user accounts or per-user state, so adding family members
  costs nothing.
* The phone app stays simple and battery-friendly: it is woken by push and evaluates a small record set.
* The laptop is a single point of failure. The phone must detect silence ("monitoring lost"), and the pipeline should
  stay portable enough to run a second instance (e.g. a free cloud VM) later.
* The phone needs a bundled gazetteer subset (areas, launch areas) to interpret area records.

## Alternatives considered

* **Phone-only.** Fragile in the background, weak on-device models, high battery cost.
* **Cloud VPS + cloud LLM.** Robust, but recurring cost, and it sends channel text to a third party.
* **Hybrid server + on-device fallback.** Doubles the parsing work. Deferred.
