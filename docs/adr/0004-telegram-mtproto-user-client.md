# 0004. Read Telegram with an MTProto user client on a dedicated account

* **Status:** Accepted
* **Date:** 2026-10-30
* **Source:** spec §4.1 · qna Q4.1, Q10.8 · research R-6

## Context

The Bot API can't read public channels unless the bot is an admin there. Reading them takes an MTProto client logged
into a real user account. Automated use carries a small risk of the account being limited. The developer has a
spare account for this.

## Decision

* Use **Telethon** on the PC, logged into the **dedicated second account**.
* The client is **read-only**: it never posts, reacts or messages anyone.
* Live updates come over the open connection, and the same client backfills channel history.
* Joins are spread out, and `FLOOD_WAIT` is always respected.
* **Credentials:** `api_id`/`api_hash` (from my.telegram.org) live in a local `.env`. The `.session` file stays on the
  PC. Both are git-ignored.
* **Login:** the developer logs in once, in their own terminal, entering the login code and 2FA password themselves.

## Consequences

* Sub-second delivery, and history access for the replay harness, channel scoring and data mining.
* The main account is never put at risk.
* The `.session` file is as sensitive as the account itself and must never be committed or copied off the PC.
* A non-Premium account caps out at ~500 joined channels, which is enough for all oblasts.

## Alternatives considered

* **TDLib (C++).** Equivalent capability, but more integration work from Python, and its main advantage (mobile push
  support) doesn't matter on a PC.
* **Telegram Bot API.** Can't read channels.
* **Manual HTML exports.** Fine for the initial dataset, useless live.
