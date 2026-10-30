# 0010. Python on the PC, Kotlin on phone and watch

* **Status:** Accepted
* **Date:** 2026-10-30
* **Source:** qna Q4.3, Q9.1

## Context

* The developer is comfortable in C++, with a light preference for it, but asked for the language that fits the tools
  best.
* The PC side needs: an MTProto client, an HTTP client for llama-server, geo libraries (polygons, distances, bearings),
  the Firebase Admin SDK, SQLite, and lots of data analysis for the replay harness, evals and data mining.
* End-to-end latency is dominated by Telegram, FCM and LLM time, not by the pipeline's own code.

## Decision

* **PC pipeline:** Python 3.12+, asyncio. Libraries: Telethon, shapely/pyproj, firebase-admin, SQLite.
* **Inference:** llama.cpp (C++), run as a separate `llama-server` process.
* **Phone:** Kotlin + Jetpack Compose. **Watch:** Kotlin + Compose for Wear OS.
* The phone and watch share a Kotlin module for the record model and the level engine.

## Consequences

* The fastest route to a working replay harness and eval loop; one language for the pipeline and the analysis.
* C++ stays where performance matters (llama.cpp) without us maintaining it.
* A hot spot found later can be moved to native code behind the same interfaces.

## Alternatives considered

* **C++ pipeline with TDLib.** Workable, but geo, FCM and analysis tooling would take much longer.
* **Kotlin on the PC too.** One language across the project, but a weaker MTProto and data-analysis ecosystem.
