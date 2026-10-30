# 0006. A source-agnostic target record is the wire format

* **Status:** Accepted
* **Date:** 2026-10-30
* **Source:** spec §5 · qna Q10.3, Q10.11 · research R-2

## Context

* The phone has to decide relevance without seeing raw text ([0002](0002-pc-pipeline-thin-clients.md)).
* Today the records come from parsed text. Later they may come from structured feeds (war-monitor, military systems)
  that need no parsing.
* war-monitor's public data model (id, type, position, heading, destination, trail, status) has worked at scale.

## Decision

* The PC sends **target records**, versioned by `v`, in an envelope with a monotonic `seq`.
* `kind` is one of `track`, `area`, `ballistic_threat`, `launch`, `explosion`, `official_alert`, `all_clear`.
* Records carry type (war-monitor taxonomy + additions), position with uncertainty or area IDs, heading ± spread,
  speed, destination, launch area, "no threat to", confidence, source count and TTL.
* **No raw post text** in v1.
* Periodic full snapshots let a client recover from missed messages without a back-channel.
* Full field list: spec §5.

## Consequences

* The phone and watch never change when a source is added, replaced or turned from text into structured data.
* Uncertainty is explicit, so coarse sources (NEPTUN, area-only posts) fit the same model.
* Records must fit FCM's 4 KB payload. Batches split accordingly.
* Future sensor-derived data must be coarsened before it becomes a record, so the format must never need sensor
  identities or detection geometry.

## Alternatives considered

* **Send raw text plus parse hints.** Couples clients to sources and leaks parsing into the phone.
* **Precomputed per-user alerts.** Would need user locations on the PC.
