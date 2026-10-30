# 0005. Parse with a rule-based fast path plus a local LLM

* **Status:** Accepted
* **Date:** 2026-10-30
* **Source:** spec §4.2–§4.5, §9.2 · qna Q5.1–Q5.4, Q10.6, Q10.7 · research R-7

## Context

* Channel posts are short, unformatted Ukrainian with slang, inflection, and implicit context: two-thirds of Kharkiv
  Life follow-ups have no reply link.
* Formats drift. The Air Force changed its emoji codes on 20.08.2026, so rules alone break.
* Ballistic warnings leave seconds, not minutes.
* The budget is $0, so there's no cloud LLM. The laptop has a 6 GB GPU.

## Decision

* **Keyword pre-filter.** Only threat posts and explosion reports go further.
* **Deterministic fast path.** Rules for ballistic-class threats and launches, `над <place>`, official alerts and
  all-clears fire records immediately, without waiting for the LLM.
* **Local LLM for everything else.**
  * Engine: llama.cpp `llama-server` with **JSON-schema-constrained output**.
  * Input: the message plus recent channel context.
  * Output: event JSON with place *text*. The LLM never produces coordinates.
* **Gazetteer** (OSM + КАТОТТГ + a reviewed alias table) resolves places.
* **Model choice by benchmark.** We use the fastest model that meets the eval thresholds. Candidates: Qwen3-4B/8B,
  Gemma 3 4B, and MamayLM as a quality reference.
* **Labels.** Built by parallel Sonnet agents in Claude Code, reviewed by the developer.

## Consequences

* Critical alerts don't depend on LLM speed or availability.
* Constrained decoding removes malformed-JSON handling.
* A model swap is a config change, re-checked against the eval set.
* We have to maintain an eval set and a drift monitor. Rules and LLM can disagree, and fusion must reconcile them.
* GPU memory (~3–5 GB) is permanently taken on the laptop.

## Alternatives considered

* **Rules only.** Breaks on format drift and slang.
* **Cloud LLM (e.g. Claude Haiku).** Best quality per effort, but recurring cost; rejected by the $0 target.
* **On-device phone LLM.** Ruled out by [0002](0002-pc-pipeline-thin-clients.md).
* **Fine-tuned small encoder (NER).** A possible later optimisation once labels exist. The RTX 5080 machine can train
  it.
