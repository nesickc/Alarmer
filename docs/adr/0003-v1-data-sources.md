# 0003. v1 data sources: Telegram channels, NEPTUN for corroboration only

* **Status:** Accepted
* **Date:** 2026-10-30
* **Source:** spec §3 · qna Q3.1–Q3.5, Q10.5, Q10.11 · research R-1–R-4, R-9

## Context

* **Telegram.** The fastest public information is in Telegram: the Air Force channel nationwide, plus regional channels
  that are often tens of seconds earlier locally (Kharkiv Life: −28 s on ballistics, −68 s on KAB, median).
* **war-monitor.org.** Its structured map API is deliberately bot-protected.
* **єППО.** It has no outbound feed. Флюгер (KB «Технарі», part of єППО) has no public API.
* **Official alert APIs.** They need keys and a proxy, and are not faster than Telegram.
* **NEPTUN.** It offers a free, legal API with tracks, but positions are coarse and its provenance is unknown.

## Decision

* **Telegram channels are the primary input:**
  * `@kpszsu`;
  * Kharkiv Life;
  * `@war_monitor`;
  * regional channels for each oblast, added after scoring;
  * the official alert channel `@air_alert_ua`, for official alert state and the lowest alert tier.
* **NEPTUN** is used only to corroborate tracks (raising confidence), with the attribution its terms require.
* No official-alert API in v1. No scraping of any site that protects itself against bots.

## Consequences

* All live inputs come through one Telegram client ([0004](0004-telegram-mtproto-user-client.md)), and one parser
  family handles them.
* Every new channel needs eval samples and a trust score before it can raise alerts on its own.
* Partner access (war-monitor, KB «Технарі», «Віраж», «Графіт», «Дельта») is the later path to accurate data. Any
  sensor-derived feed must be published in a way that can't reveal sensor locations (spec §3.3).

## Alternatives considered

* **alerts.in.ua / ukrainealarm APIs.** Official state, but not faster, and they need keys and a proxy. Can be added
  if Telegram proves insufficient.
* **NEPTUN as a primary feed.** Its accuracy has to be measured against Telegram first.
