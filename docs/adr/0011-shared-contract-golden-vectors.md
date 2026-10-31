# 0011. Share one contract: a strict record schema and golden level vectors

* **Status:** Accepted
* **Date:** 2026-10-31
* **Source:** plan §2, §9 · spec §5, §6 · [0006](0006-target-record-wire-format.md),
  [0009](0009-alert-levels-time-to-impact.md), [0010](0010-implementation-languages.md)

## Context

* There will be two level engines on separate tracks: a Python reference for the replay harness (plan 1.9) and Kotlin
  on the phone (plan 3.2). If they disagree, the replay harness predicts alerts the phone never fires.
* The wire format ([0006](0006-target-record-wire-format.md)) is written in Python and read in Kotlin. A field that
  drifts on one side breaks the other silently.
* Spec §6 is prose and tables with gaps, such as a Shahed "над Харковом" with no heading. Two implementers would fill
  them differently.
* The real gazetteer doesn't exist yet (plan 1.3), and its data will keep changing after it does.

## Decision

* `contracts/` holds the contract, versioned with the code:
  * `record.schema.json`: JSON Schema (2020-12) of the envelope and record. It is **strict for the producer**: no
    unknown fields, per-kind required fields, UTC timestamps. Everything the pipeline publishes must validate.
  * `golden/`: **stateless vectors**. Each takes a record and a user location and gives the expected level. Vectors
    run in a small fixture world (areas, launch areas, users) with a parameter file holding the spec §6 values.
* **Types aren't tied to kinds.** Any type may appear in a `track`, `area`, `ballistic_threat` or `launch`, and the
  kind, not the type, picks the level rule. Threats and launches get the blunt rules of
  [0009](0009-alert-levels-time-to-impact.md) whatever the weapon. Tracks get ETA, with a default speed for
  ballistic-class types too. A new fast weapon's launches, or a ballistic missile tracked from military data some day,
  then need no schema change. [0009](0009-alert-levels-time-to-impact.md) assumed ballistic-class weapons only arrive
  as threats and launches; its rules stand for those.
* Both engines run every vector in CI. Each vector is tagged with the spec §6 rules it exercises, and a test fails if
  any rule has no vector.
* Vectors use the fixture world, not the real gazetteer, so they test rules rather than data. The gazetteer gets its
  own tests in 1.3.
* Expected levels stay clear of every threshold (10% of an ETA band, 3° of an angle, 20 km of a range limit), so any
  sound great-circle maths gives the same answer.
* **Compatibility.** The phone ignores unknown fields and treats an unknown `type` as its class's `.unknown` (or
  `unknown`). Adding an optional field or a type keeps `v`. Removing a field or changing its meaning bumps `v`.
* Where spec §6 is silent, a vector records a proposed reading and says so. Once confirmed, the spec absorbs it.
* Stateful behaviour is out of scope for these vectors: repeats only on a rising level (§6.6), the all-clear when the
  last track ends, monitoring lost (§7.5), TTL and `seq` handling. Sequence vectors can follow once the Python engine
  exists (1.9).

## Consequences

* "What level should this be?" has one answer, and a disagreement shows up as a failing vector instead of in the field.
* A contract change touches both sides in one PR.
* Calibration (plan Stage 5) edits `params.json` and the affected vectors, not the engines' structure.
* The fixture geometry is crude, so vector descriptions quote fixture distances, not real ones.
* The Kotlin tests will need a JSON parser (e.g. kotlinx.serialization) when 3.2 starts.

## Alternatives considered

* **Hand-ported unit tests on each side.** They drift as soon as one side changes.
* **Vectors against the real gazetteer.** Every data fix would churn the expected levels, and the gazetteer arrives
  after the first engine.
* **Shared or generated engine code.** The languages differ by design ([0010](0010-implementation-languages.md)); a
  data-level contract is simpler than code generation.
* **A tolerant schema that allows extra fields.** Typos and stray fields from the pipeline would pass unnoticed.
  Tolerance belongs in the phone's parser instead.
* **Types tied to kinds** (a `launch` must be ballistic-class, a `track` must not). It would catch some pipeline
  mix-ups, but it rejects the launch of any other fast weapon and a ballistic missile with a known position.
