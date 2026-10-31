# Contracts

The point where the pipeline track and the device track meet ([plan §2](../docs/plan.md#2-how-we-get-there)). The
Python pipeline and the Kotlin `:shared` module both test against the files here.

| File | Contents | Plan task |
|---|---|---|
| `record.schema.json` | JSON Schema of the wire format ([spec §5](../docs/spec.md#5-target-record-wire-format-v1)) | 0.3 |
| `golden/` | Golden level vectors: a record and a user location in, the expected level out ([spec §6](../docs/spec.md#6-threat-model-and-alert-levels-phone-side)) | 0.3, 1.9 |

A change here changes what both sides must do, so it lands in the same PR as the code changes on both sides.
