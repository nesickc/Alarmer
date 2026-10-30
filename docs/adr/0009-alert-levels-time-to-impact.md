# 0009. Alert levels come from time to impact; blunt rules for ballistic-class

* **Status:** Accepted
* **Date:** 2026-10-30
* **Source:** spec §6 · qna Q6.2, Q6.3, Q7.1, Q10.4 · research R-5, R-9

## Context

* Threat speeds span more than 30× (Geran-2 ~180 km/h to Zircon), so distance alone says little about danger.
* Ballistic-class weapons leave about a minute or less.
* Launch posts almost always name a target, but targets get re-predicted in flight: a Zircon first called for Kyiv
  struck Vinnytsia two minutes later.
* Too many buzzes train users to ignore them, yet missing a critical event is the worst outcome.

## Decision

**Levels:** L4 red, L3 orange, L2 yellow, L1, L0, plus all-clear and monitoring-lost patterns.

**Ordinary threats:** the level comes from **time to impact** at the user's location. That is earliest arrival
(distance minus uncertainty, divided by the type's speed) for threats approaching the user (heading cone, or stated
destination nearby). Initial bands: L4 ≤ 2 min, L3 ≤ 5 min, L2 ≤ 15 min, to be calibrated from explosion-vs-threat data.

**Ballistic-class** (`ballistic.*`, Zircon, unknown "швидкісна ціль") skips ETA:

| Situation | Level |
|---|---|
| Threat | L2 within 550 km of the stated launch area (else the Russian border + occupied territory, not Belarus) |
| Launch without a target | L4 in that range |
| Launch with a named target | L4 within 50 km of the target and in a ±20° vector corridor; L2 elsewhere in range |
| Local "для нас без загрози" | L2 for that city |

**Other rules:**
* The official alert is the lowest buzzing tier (L1), shown with its reason. Alarmer never suppresses or downgrades it.
* A repeat buzz happens only when a level rises.

## Consequences

* One level engine on the phone, driven by records and a small parameter table, so calibration doesn't change the
  architecture.
* Ballistic-class rules will over-alert by design. That's accepted because the window is too short for judgement.
* Thresholds, speeds, corridor shape and track lifetimes are open parameters (spec §12) and must be measured: replay
  harness, explosion data mining, live use.

## Alternatives considered

* **Distance rings** (as in Флюгер). Simple, but wrong across speed classes.
* **Fixed per-type levels.** Ignore direction and the user's location.
