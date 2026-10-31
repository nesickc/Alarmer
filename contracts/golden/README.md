# Golden level vectors

A vector is one worked case of [spec §6](../../docs/spec.md#6-threat-model-and-alert-levels-phone-side): a **record**
and a **user location** go in, and the **expected level** comes out. The Python reference engine (plan 1.9) and the
Kotlin engine in `:shared` (plan 3.2) must both pass every vector
([ADR-0011](../../docs/adr/0011-shared-contract-golden-vectors.md)).

| File | Contents |
|---|---|
| `vectors/*.json` | The vectors, one file per spec section: `eta` (§6.2), `ballistic` (§6.3), `area` (§6.4), `alerts` (§6.5) |
| `world.json` | Fixture world: areas (parent, neighbours, polygon), launch areas, users |
| `params.json` | The engine parameters the vectors assume: the initial values from spec §6 |
| `golden.schema.json` | The shape of each file above |

Each vector has an `id`, the `rules` it exercises (table below), a `description` that quotes the deciding numbers, a
`user` from `world.json`, a `record` that validates against [record.schema.json](../record.schema.json), and
`expect.level`: `L0`–`L4` or `all_clear`.

The world is deliberately crude: rectangles for city districts, a dozen vertices for an oblast. Its IDs are readable
stand-ins for КАТОТТГ codes. Distances in the descriptions are fixture distances, not real ones.

## How a vector is evaluated

The engine gets the record, the user's coordinates, the world and the params, and returns one level. There is no clock
and no state: each record is judged on its own, as of its `last_seen`.

**Geometry**
* Distances are great-circle on a sphere of radius 6371 km. Bearings are initial great-circle bearings.
* The distance to a circle (`pos`, `dest`) is to its edge: `max(0, d − r_km)`.
* The distance to a launch area is to its geometry: the point, or the nearest polygon edge (0 inside).
* The user's areas are the world areas whose polygons contain them. `world.json` lists them, and a test checks the list.

**Area ladder** for one area ID, compared with the user's areas:

| The area is… | Ladder |
|---|---|
| the user's neighbourhood or district | L4 |
| the user's hromada, or inside it (another district or neighbourhood of the same city) | L3 |
| the user's raion | L2 |
| a hromada bordering the user's, or inside one | L2 |
| anything else in the user's oblast, including the oblast itself | L1 |
| anything else | L0 |

A record with several areas takes the highest.

**Rules by kind.** The kind picks the rule; the type only picks a speed or a nationwide threat. Whatever the kind, a
record whose `status` isn't `active` gives L0.

* **`track`.** The level is the highest of:
  * the ETA band, if approaching. Speed is `speed_kmh`, else `params.speed_kmh` (exact type, then `class.*`, then
    `*`). ETA = distance to the `pos` circle ÷ speed. It is *approaching* if the user lies within
    `heading.deg ± max(pm, 25°)` as seen from `pos`, or the `dest` circle is within 10 km of the user. Bands:
    ≤ 2 min L4, ≤ 5 min L3, ≤ 15 min L2;
  * the area ladder over the track's `area` (`над <place>`);
  * L1 if the track is in the user's oblast: the `pos` centre lies in the oblast's polygon, or an `area` is inside it.
* **`area`.** The area ladder over `area`.
* **`ballistic_threat`**, whatever its type. A type in `params.ballistic.nationwide_threat_types`
  (`aviation.mig31k`) gives L2 anywhere. Otherwise L2 within 550 km of the `launch_area`, or of
  the fallback launch area (`params.ballistic.fallback_launch_area`) when there is none. Beyond that, L0.
* **`launch`**, whatever its type.
  * Without a `dest`: L4 within 550 km of the launch area (same fallback).
  * With a `dest`, L4 in either of two places. One is within 50 km of the `dest` circle. The other is the vector
    corridor: from the launch area's `origin`, the user's bearing is within ±20° of the bearing to the target, and
    the user is no farther than the target's distance + 150 km. Both reach beyond 550 km. Elsewhere it is L2 within
    550 km, else L0. A launch area without an `origin` (the fallback) has no corridor.
  * If `no_threat_to` contains one of the user's areas, the level is capped at L2.
* **`explosion`.** In the user's neighbourhood or district: L2. In the user's hromada: L1. Anything else: L0.
* **`official_alert`.** If `area` contains one of the user's areas: L1, else L0.
* **`all_clear`.** If `area` contains one of the user's areas: `all_clear`, else L0.

## Rules

Every rule below has at least one vector; a test enforces it.

| Rule | Spec | Case |
|---|---|---|
| `eta.l4` | §6.2 | Approaching, ETA ≤ 2 min → L4 |
| `eta.l3` | §6.2 | Approaching, ETA ≤ 5 min → L3 |
| `eta.l2` | §6.2 | Approaching, ETA ≤ 15 min → L2 |
| `eta.over` | §6.2 | Over the user's neighbourhood or district → L4 |
| `eta.over_ladder` | §6.2 | Over another area: the area ladder |
| `eta.oblast` | §6.2 | In the user's oblast, no band reached → L1 |
| `eta.none` | §6.2 | Anything else → L0 |
| `approach.cone` | §6.2 | Heading cone at its minimum ±25° |
| `approach.spread` | §6.2 | A spread over 25° widens the cone |
| `approach.dest` | §6.2 | Stated destination within its radius + 10 km of the user |
| `speed.slow_uav` | §6.2 | `uav.*` at 180 km/h |
| `speed.jet_uav` | §6.2 | `uav.geran_3` at 350 km/h |
| `speed.cruise` | §6.2 | `cruise.*` at 800 km/h |
| `speed.banderol` | §6.2 | `cruise.banderol` at 600 km/h |
| `speed.kh22` | §6.2 | `cruise.kh22` at 3600 km/h (≈ Mach 3) |
| `speed.ballistic` | §6.2 | Ballistic-class types as tracks at 6000 km/h (≈ Mach 5) |
| `speed.record` | §5.2 | A record's `speed_kmh` beats the type default |
| `ballistic.threat` | §6.3 | Threat → L2 within 550 km of the launch area |
| `ballistic.fallback` | §6.3 | No launch area: measured from the Russian border + occupied territory |
| `ballistic.mig31k` | §6.3 | MiG-31K take-off → L2 nationwide |
| `ballistic.launch` | §6.3 | Launch, no target → L4 within 550 km |
| `ballistic.target` | §6.3 | Launch with a target → L4 within 50 km of it |
| `ballistic.corridor` | §6.3 | Launch with a target → L4 in the ±20° corridor up to target + 150 km |
| `ballistic.in_range` | §6.3 | Launch with a target → L2 elsewhere within 550 km |
| `ballistic.out_of_range` | §6.3 | Beyond 550 km → L0 |
| `ballistic.no_threat` | §6.3 | «Для нас без загрози» → at most L2 for that city |
| `ballistic.any_type` | §6.3 | Threats and launches get these rules whatever the type, e.g. a Kh-22 |
| `area.local` | §6.4 | KAB on the user's district or neighbourhood → L4 |
| `area.hromada` | §6.4 | KAB on the user's hromada → L3 |
| `area.raion` | §6.4 | KAB on the user's raion → L2 |
| `area.neighbour` | §6.4 | KAB on a neighbouring hromada → L2 |
| `area.oblast` | §6.4 | KAB elsewhere in the oblast → L1 |
| `area.none` | §6.4 | KAB in another oblast → L0 |
| `area.other_type` | §6.4 | Other area-only threats follow the same ladder |
| `official.alert` | §6.5 | Official alert for the user's area → L1 |
| `explosion.local` | §6.5 | Explosion in the user's neighbourhood or district → L2 |
| `explosion.city` | §6.5 | Explosion in the user's city → L1 |
| `explosion.none` | §6.5 | Explosion anywhere else → L0 |
| `all_clear` | §6.5 | All-clear for the user's area → the all-clear pattern |
| `status.inactive` | §4.6 | A destroyed, departed or expired record → L0 |

## Not covered yet

Stateful behaviour has no vectors: buzzing again only when a level rises (§6.6), the all-clear when the last relevant
track ends (§6.5), monitoring lost (§7.5), and TTL and `seq` handling (plan 3.1). A sequence-vector format can be added
alongside the Python engine in plan 1.9.

## Adding a vector

1. Tag it with the rules it exercises. A new rule goes into the `rule` enum in `golden.schema.json` and the table
   above.
2. Keep clear of thresholds: at least 10% from an ETA band edge, 3° from a cone or corridor edge, and 20 km from a range
   limit or the corridor's end.
3. Quote the deciding numbers in the description.
4. Run `pytest` in `pipeline/`. It validates the file, the record and every reference into `world.json`.
