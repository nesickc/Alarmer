# Contracts

The point where the pipeline track and the device track meet ([plan §2](../docs/plan.md#2-how-we-get-there)). The
Python pipeline and the Kotlin `:shared` module both test against the files here
([ADR-0011](../docs/adr/0011-shared-contract-golden-vectors.md)).

| File | Contents | Plan task |
|---|---|---|
| `record.schema.json` | JSON Schema of the wire format ([spec §5](../docs/spec.md#5-target-record-wire-format-v1)): the envelope, with the record in `$defs/record` | 0.3 |
| `examples/` | Envelopes that must validate: the spec example, a snapshot, a heartbeat | 0.3 |
| [golden/](golden/README.md) | Golden level vectors: a record and a user location in, the expected level out ([spec §6](../docs/spec.md#6-threat-model-and-alert-levels-phone-side)) | 0.3, 1.9 |

A change here changes what both sides must do, so it lands in the same PR as the code changes on both sides.

## Compatibility

* **The schema is strict for the producer.** It allows no unknown fields, requires each kind's fields and accepts only
  UTC timestamps. Everything the pipeline publishes must validate.
* **Types aren't tied to kinds.** Any type may appear in a `track`, `area`, `ballistic_threat` or `launch`, so a Kh-22
  launch or a ballistic missile with a known position needs no schema change. The kind picks the level rule.
* **The phone is tolerant.** It ignores fields it doesn't know and treats an unknown `type` as its class's `.unknown`
  (or `unknown`), so an older app keeps working with a newer pipeline.
* **When `v` changes.** Adding an optional field or a new type keeps `v`. Removing a field, making it required, or
  changing what it means bumps `v`, and the phone rejects envelopes of a version it doesn't know.

## Checks

`pipeline/tests/test_contracts.py` validates the schemas, the examples, the spec §5.2 example, every golden vector and
its references into the fixture world. It also checks that every §6 rule has a vector. The engines themselves arrive
in plan 1.9 (Python) and 3.2 (Kotlin).
