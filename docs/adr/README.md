# Architecture decision records

Each significant decision gets a short record: the context, what we decided, and what follows from it. The
[spec](../spec.md) describes *what* the system does. ADRs explain *why* it is built this way.

## Conventions

* **File name:** `NNNN-short-title.md`, numbered in order, never reused. Copy [template.md](template.md).
* **Status:** `Proposed` → `Accepted` → (`Superseded by NNNN` | `Deprecated`).
* **Accepted ADRs are not rewritten.** To change a decision, write a new ADR and mark the old one
  `Superseded by NNNN`. Typos and broken links can be fixed in place.
* Keep each ADR to about a page. Link the spec section or `qna/` question it came from.
* When a PR changes architecture, add or supersede the ADR in that same PR.

## Index

| # | Decision | Status |
|---|---|---|
| [0001](0001-record-architecture-decisions.md) | Record architecture decisions | Accepted |
| [0002](0002-pc-pipeline-thin-clients.md) | A PC pipeline does all processing; phone and watch are thin clients | Accepted |
| [0003](0003-v1-data-sources.md) | v1 data sources: Telegram channels, NEPTUN for corroboration only | Accepted |
| [0004](0004-telegram-mtproto-user-client.md) | Read Telegram with an MTProto user client on a dedicated account | Accepted |
| [0005](0005-fast-path-plus-local-llm.md) | Parse with a rule-based fast path plus a local LLM | Accepted |
| [0006](0006-target-record-wire-format.md) | A source-agnostic target record is the wire format | Accepted |
| [0007](0007-fcm-transport.md) | FCM high-priority data messages from PC to phone | Accepted |
| [0008](0008-wear-os-data-layer-watch-app.md) | Own Wear OS app over the Data Layer for watch alerts | Accepted |
| [0009](0009-alert-levels-time-to-impact.md) | Alert levels come from time to impact; blunt rules for ballistic-class | Accepted |
| [0010](0010-implementation-languages.md) | Python on the PC, Kotlin on phone and watch | Accepted |
| [0011](0011-shared-contract-golden-vectors.md) | Share one contract: a strict record schema and golden level vectors | Accepted |
