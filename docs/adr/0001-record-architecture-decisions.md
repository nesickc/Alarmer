# 0001. Record architecture decisions

* **Status:** Accepted
* **Date:** 2026-10-30
* **Source:** project setup

## Context

Alarmer's design came out of two rounds of questions ([qna/](../../qna/)). Many choices depend on facts that will
change: channel formats drift, new sources appear, models improve. Without a record of *why* a choice was made, it's
hard to tell later whether it still holds.

## Decision

Record each significant architectural decision as a short ADR in `docs/adr/`, following the conventions in
[README.md](README.md).

## Consequences

* A decision becomes reviewable in the PR that introduces it.
* Revisiting a decision means writing a new ADR, so history stays readable.
* Small cost: one extra page per significant change.

## Alternatives considered

* **Keep decisions in the spec only.** The spec says what is true now and loses the reasoning and the history.
* **Keep them in issues or chat.** Hard to find later, and not versioned with the code.
