# Alarmer — spec questions

Write your answer under each **Answer:** line. "ok" means you accept my suggestion. Skip anything you don't care
about and I'll use the suggested default. **[R-x]** points to the background in [research.md](research.md).

Legend: 🔴 blocks the architecture · 🟡 shapes the MVP · ⚪ can wait

---

## 1. Scope and users

**Q1.1 🔴 Who is this for?**
(a) just you, (b) you + family/friends (≤10 people), (c) a public app (Play Store, unknown users).
This decides Telegram-account usage, API terms (alerts.in.ua forbids tokens in apps, NEPTUN requires attribution),
server cost, legal exposure and Play-policy constraints [R-3, R-4, R-8].
*Suggestion:* (a) now, designed so that (b) is possible.

**Answer:**
For now only me and family, but the infrastructure should be scalable

**Q1.2 🔴 Geographic scope at launch?** Kharkiv city only, Kharkiv oblast, or all of Ukraine?
The Kharkiv neighbourhood gazetteer and Kharkiv Life slang are the hard parts; the rest of Ukraine mostly comes from
the Air Force channel and NEPTUN.
*Suggestion:* Kharkiv city + oblast for v1; keep the data model country-wide.

**Answer:**
The geographic scope should be the entirety of Ukraine. So I'll need to find a bunch of chats to add the telegram account to.

**Q1.3 🟡 Where is "the user"?**
(a) one fixed home location, (b) several saved places (home/work/parents) with the active one picked manually,
(c) live GPS, (d) live GPS with saved places as a fallback.
*Suggestion:* (d). Location never leaves the phone (see Q8.3).

**Answer:**
D, your suggestion is good

**Q1.4 🟡 How precise does "near me" have to be?**
City → district (Салтівський, Київський…) → neighbourhood (Північна Салтівка, ХТЗ, Нова Баварія…) → street-level.
Kharkiv Life works at neighbourhood level ("3 на Куліни/ХТЗ"), so neighbourhood is realistic; street-level isn't.

**Answer:**
Neighbourhood is as best as we can have it, for now.

**Q1.5 🟡 Language of the notifications:** Ukrainian, English, or configurable?

**Answer:**
Ukrainian for now, but take a note that it should be configurable later on

**Q1.6 🔴 Relationship to the official alert.**
This app is a *supplement*, not an official warning system. NEPTUN's terms also require us to say so [R-4].
Should the app (a) only add detail on top of the official air-raid alert, or (b) also alert when there is **no**
official alert in your hromada (e.g. "КАБ на Дергачі" while Kharkiv is clear)?
*Suggestion:* (b), but never *downgrade* or suppress anything the official alert says.

**Answer:**
The official alert is fine to keep as the lowest tier notification. Ideally specifying the official reason.

**Q1.7 🟡 What counts as success?**
Rank: (a) earliest possible warning, (b) fewest false/irrelevant alerts (especially at night), (c) battery life,
(d) zero missed critical events. How many non-critical vibrations per night are tolerable before you'd mute the app?

**Answer:**
All four are important. I'd say a handful of vibrations are fine, they'd probably even go unnoticed (lower tier especially). The critical ones (high tier) are important to not miss. But then again, they should be reasonable.

---

## 2. Devices

**Q2.1 🔴 Which watch exactly** (brand, model, OS: Wear OS / Galaxy Watch, Pixel Watch, Garmin, Amazfit/Zepp,
Mi Band, Huawei…)?
Custom vibration patterns per threat level are easy on Wear OS (small watch app), possible on Garmin (Connect IQ, with
limits), and often impossible on bands whose companion app controls notifications [R-8].

**Answer:**
Galaxy watch 7, the phone is Xiaomi 17t pro. We should primarily target android and Wear OS.

**Q2.2 🔴 Which phone (model + Android version)?** Do you use any OEM "battery saver"/"app freezing" features?
This matters for background survival and NPU/on-device-LLM viability.

**Answer:**
I am thinking about having the phone and the watch serve as "frontend". They would ingest the coordinates, target type, and heading from the PC. Maybe using some special internal private telegram chat, or some other communication method. Perhaps it makes sense to use SMS in case internet is not available, but let's not go there for now.
The LLM would run on the PC. It maybe makes sense to use something like qwen, so it can reasonably work with spotty data from the telegram channels. This would also allow us to pivot to more accurate methods (i.e. if access to the military data is provided), to avoid having to parse the text at all. Since the "frontend" would ingest the coordinates just as well.

**Q2.3 🟡 Does the phone also make sound or vibrate?**
Options: watch-only; phone sound for critical only; phone sound for high+critical; mirror everything.
At night, should critical alerts **bypass Do Not Disturb** on the phone (needs your one-time permission grant)?

**Answer:**
Only the watch, unless it's not connected. If the watch isn't connected then the phone should vibrate instead (sound is probably excessive)

**Q2.4 ⚪ Does the watch need to work without the phone** (LTE watch, phone at home)? (Big extra scope; suggest no.)

**Answer:**
No.

**Q2.5 🔴 Distribution:** sideloaded APK only, or eventually Google Play?
Play adds policy reviews for `specialUse` foreground services, DND/full-screen behaviour, and "safety app" claims
[R-8].
*Suggestion:* sideload for v1.

**Answer:**
Sideload for the MVP, later we'll do google play if this thing works as good as I'd like.
---

## 3. Data sources

**Q3.1 🔴 What do you mean by "єППО"?**
As far as I can find, єППО is a *reporting* app: citizens send sightings to the Air Force. It has **no public outbound
feed** [R-3]. Did you mean:
(a) єППО itself (if so, do you have any access or contact?),
(b) the Air Force data in general,
(c) the official «Повітряна тривога» map, which since 17–18 Oct 2026 shows approximate Shahed/cruise/Бандероль
movement but **no ballistics** and has no published API,
(d) something else?

**Answer:**
I thought єППО has an API to get that data. That's what I gathered about a similar project called "Флюгер" that provides approximate direction and distance from the targets nearby.

**Q3.2 🔴 war-monitor.org:** their API is deliberately bot-protected (Cloudflare Turnstile + device keys), and I will not
build around that [R-2]. Options:
(a) write to the project and ask for partner/API access (I can draft the request),
(b) consume only their public Telegram channel `@war_monitor` as one more text source,
(c) both.
*Suggestion:* (c). We copy their **schema and type taxonomy** for our own model either way.

**Answer:**
I think we'll be able to write a request if our application works well. Before that let's use their channel as a text input. If NEPTUN gives access, we should try using them instead.

**Q3.3 🟡 NEPTUN (neptun.in.ua) open API** gives tracks with id, type, heading, speed, uncertainty and trail, plus a
WebSocket stream. It's free and legal with visible attribution [R-4]. Its provenance and accuracy are unknown, and
positions are coarse (4–28 km uncertainty in today's sample).
Use it as (a) a primary structured feed, (b) a corroborating feed only, or (c) not at all?
*Suggestion:* (b) in v1. Measure it against Telegram on live data, then decide.

**Answer:**
Agreed with your suggestion

**Q3.4 🟡 Official alert state:** alerts.in.ua (hromada-level, red/yellow, token, ≤12 req/min, server proxy required),
ukrainealarm API (key via form), or both? I'll apply for keys if you want; tell me under whose name.

**Answer:**
Official alert state is usually only slightly faster than the telegram channels (sometimes slower), so let's not use it for now (if we can make do with the telegram channels).

**Q3.5 🔴 Telegram channel list.** Confirmed: `@kpszsu`, Kharkiv Life. Candidates: `@war_monitor`, `@air_alert_ua`,
`@deraketaua`, `@eRadarrua`, `@radar_raketaa`, the "radar.kharkiv" map Kharkiv Life promotes, Kharkiv city-hall /
ХОВА channels.
Which do you actually read today, and **which do you trust most**? Name any Kharkiv channels I've missed.
(Each new channel needs its own parsing prompt section and eval samples.)

**Answer:**
We'll need to gather a comprehensive list of channels we process. It would probably require a channel for each oblast at least, if not for each city.

**Q3.6 🟡 Per-source trust:** should a single unconfirmed message from a less reliable source be able to raise a
**critical** alert on its own, or only after corroboration?
The data says Kharkiv Life is often 30–70 s earlier than the Air Force on ballistic and KAB threats [R-1], so waiting
for corroboration costs real warning time.
*Suggestion:* critical keywords from trusted sources fire immediately; everything else gets confidence-weighted.

**Answer:**
yeah, we'll need to have a scoring system for channels, to quantify their trustworthiness.

**Q3.7 ⚪ Other inputs you'd like considered later?** (siren audio detection via microphone, public radio scanners,
Diia's upcoming alert app, X/Bluesky.)

**Answer:**
Not now, we'll see later if there are additional sources we want.
---

## 4. Ingestion and architecture

**Q4.1 🔴 Are you OK with a real Telegram user account reading the channels?**
The Bot API can't read public channels; an MTProto client (TDLib/Telethon) on a logged-in account is required [R-6].
*Suggestion:* a dedicated second account (separate SIM/number), read-only, to protect your main account.

**Answer:**
Yeah, a separate account is fine, I have one.

**Q4.2 🔴 Where does the processing run?**
* **(A) Phone-only:** TDLib + parser + (on-device) model inside a foreground service. Private, no server costs, but
  fragile under Doze/OEM killers/Android 15 limits; on-device LLM quality and battery are a concern; no Haiku-class
  model.
* **(B) Server:** a small VPS running Telegram client + parser + LLM + track fusion, pushing events to the phone via
  high-priority FCM. Robust and easy to iterate. ~$5–10/month VPS + ~$5–10/month LLM.
* **(C) Hybrid:** server primary; the phone keeps a minimal on-device fallback (e.g. polls official alerts) and warns
  you if the server goes silent.

*Suggestion:* (C). If you choose (A), on-device parsing becomes a research project of its own [R-7].

**Answer:**
I believe we should parse the channels on a PC, and send the processed data to the phone for the app to decide what to show. The PC would basically send a list of targets: their coordinates, heading, and type. We can discuss the protocol in detail.

**Q4.3 🟡 If there's a server: any hosting preferences?** (existing VPS, cloud provider, region; outside Ukraine is more
robust to blackouts.) Preferred server language (Python/Telethon is quickest; Kotlin, Go or C++ are possible)?

**Answer:**
I'd like to have it local on my PC + phone + watch for now. We should choose the language by the available tools (convenience) considering what we need, and performance. I am leaning towards C++ as it's a language I'm comfortable with, but it's a very light preference. If python is better here -- go for that.

**Q4.4 🟡 Push channel:** Google FCM (most reliable under Doze, needs Google Play Services), or self-hosted
(ntfy/UnifiedPush/WebSocket; no Google, less reliable in deep sleep)?

**Answer:**
For phone <-> watch communication we should go for the most reliable free option


**Q4.5 🔴 End-to-end latency target** (channel post → watch buzz). Proposal: **critical ≤ 3 s**, high ≤ 5 s, rest
≤ 15 s. For ballistics from the north, the total warning window may be under a minute [R-5]. Agree?

**Answer:**
We should reduce the latency to the least possible amount. Especially for ballistics. High alert for ballistic threat, red alert if the missile is launched in the direction of the user.

**Q4.6 🟡 Degraded mode:** during blackouts mobile data can drop. If the app hasn't heard from its sources for X
minutes **while an official alert is active**, should the watch get a distinct "⚠️ monitoring lost" buzz? What X?
*Suggestion:* yes, X = 2 min during an alert, 10 min otherwise.

**Answer:**
I feel like if the comms drop we should investigate SMS as an option for high alerts, and perhaps a small message that monitoring is lost otherwise.
---

## 5. Parsing and the LLM

**Q5.1 🔴 Is it OK to send public channel text to a cloud LLM** (Anthropic API)? No personal data or location would be
sent, only public posts plus our context.
*Suggestion:* yes, **Claude Haiku 5.5** (`claude-haiku-5-5`): strong Ukrainian, strict JSON-schema output, cheap
(~$10/month at expected volume), and a deterministic fast path in front so critical alerts don't wait for it [R-7].

**Answer:**
I want a self-hosted llm. I want the system to be as close to free as possible

**Q5.2 🔴 Is "works with zero cloud dependency" a hard requirement?**
If yes, we need on-device parsing. Gemini Nano is ruled out because it only runs while the app is in the foreground.
That leaves a fine-tuned small model (Gemma 3 1B via LiteRT-LM, ~2–3 s per message, plus a 0.5–1.5 GB download) or a
small NER classifier, trained on labels distilled from the exports [R-7].

**Answer:**
The LLM may run on a PC

**Q5.3 🟡 Monthly budget ceiling** for LLM + server (e.g. $10 / $25 / $50)?

**Answer:**
We should target $0 excluding electricity. I don't know about SMS, don't count that either.

**Q5.4 🟡 Will you help build the ground truth?**
I'd auto-label a few thousand messages with a strong model, and you'd review ~300–500 (especially Kharkiv Life slang
and neighbourhood names). That eval set lets us measure parser accuracy and catch format drift like the
20.08.2026 emoji change [R-1]. How much time can you give it?

**Answer:**
I'm fine with looking through the data. Though your suggestion for auto-labeling is very good.

**Q5.5 🟡 Kharkiv slang dictionary:** can you confirm or extend these meanings?
`МД`, `ХГ` (Холодна Гора?), `БНР`, `КР`, `Молнія`, `реактив`, `upd: без фіксації`, `Вилетів в область`, `Чисто`,
`Баварія`, `РЖМ`, `ХТЗ`, `Дафі`, `Барабашова`, `Сортувальна`. Anything else you see often?

**Answer:**
There's a lot of slang for these, some would refer to places. I can give this info for Kharkiv, but not for other cities. I'd prefer if you could look up the ones you're unsure of (as a part of the auto-labeling). Or I can translate the ones you provide in a list.


**Q5.6 ⚪ What should be extracted from non-threat posts?** (aftermath/"влучання" reports, power schedules, morning
summaries.) Ignore them, keep them as context only, or show some (e.g. "explosion reported in your district")?

**Answer:**
I think explosions are important, everything else is noise. We should probably set a filter of a handful of words for alert posts, others are promotions, aftermath, and general news -- irrelevant to our usecase.
---

## 6. Geography and threat model

**Q6.1 🟡 Gazetteer:** I'll build it from OSM (settlements + Kharkiv neighbourhood polygons) plus a hand-made alias
table (inflected forms, slang). Do you know of a good existing Kharkiv neighbourhood map/polygon set, and can you
sanity-check the alias list later?

**Answer:**
I will definitely check the alias list later, that one is important. We might have to make some polygons manually tho.

**Q6.2 🟡 "Coming toward me" definition.** Proposal: a target counts as *approaching* if its estimated heading puts you
within ±25° and the distance is shrinking, or its stated destination (`курсом на X`) is within N km of you. ETA uses
per-type speeds [R-5]. Good starting rule? What N for city-level (e.g. 5 km) vs oblast-level?

**Answer:**
I don't think we should use distance, instead we should use approximate time to impact. Distance is somewhat meaningless alone, considering we have a plethora of different target types with vastly different speeds (from hypersonic missiles like Zircon to Geran-2 single prop drones). we'll need to discuss it once we gather some data. I believe we should track explosion reports compared to threat reported to gather enough data to make conclusions. That'll be a separate data mining sidequest.

**Q6.3 🟡 Area-only threats** ("☄️ Загроза балістики з півночі", "КАБи на Харківщину") have no point or vector. Treat
"ballistic threat from the north/north-east" as **high** for Kharkiv by default, since it is the city closest to the
launch areas?

**Answer:**
Threat of ballistics is a yellow alert, ballistics launched is a red alert for every city within 550 km of russian border unless the target is explicitly specified. These missiles are too fast to afford extra time for judgement.

**Q6.4 ⚪ Track lifetime:** how long after the last mention does a track auto-expire if no "збито"/"вилетів в
область"/all-clear arrives? (Suggest: Shahed 20 min, jet 10 min, missile 5 min, ballistic 3 min.)

**Answer:**
Not sure, this is a UX thing, it will need to be tested manually
---

## 7. Alert levels and watch UX

**Q7.1 🔴 Proposed levels.** Please edit:

| Level | Example triggers | Watch | Phone |
|---|---|---|---|
| **L4 Critical** | ballistic threat toward Kharkiv; "ціль/ракета на Харків"; KAB on your district; jet/Бандероль < ~2 min ETA to you; "над <your district>" | long continuous pattern, repeats until acknowledged | loud, bypass DND |
| **L3 High** | threat heading to your district/neighbourhood; Shahed < ~5 min ETA; "над Харковом" | strong triple buzz | sound (optional) |
| **L2 Medium** | threat heading to your city but other side of it; within ~15–20 km; KAB on nearby hromadas | double buzz | silent |
| **L1 Low** | threat in oblast, not heading to you; official alert starts | single short buzz (or none at night) | silent |
| **L0 Info** | far away, summaries, aftermath | no buzz, visible in app | — |
| **All-clear** | official відбій; track destroyed/left | gentle distinct pattern | — |

**Answer:**
Sounds should be optional. Threat heading in the user's district can be critical depending on the ETA. We need to gather explosions data to tell for sure. Otherwise I agree with your proposals.

**Q7.2 🟡 Night mode:** between which hours should L1/L2 be muted or batched?

**Answer:**
This should be configurable from the app.

**Q7.3 🟡 Anti-spam:** during mass attacks the Air Force posts ~300/day and Kharkiv Life up to ~1/min. Proposal:
updates to the **same track** don't re-buzz unless the level rises; at most one L1/L2 buzz per N minutes; L3/L4 are
never throttled. What N?

**Answer:**
During a mass attack on a city each alert is useful. I need to see it myself to judge. So let's wait for the MVP for this one

**Q7.4 🟡 Notification text:** the watch fits ~2 short lines. Example: `🏍 Реактивний → Салтівка · ~3 хв` /
`джерело: Харків Life`. Do you want the source and a confidence hint shown?

**Answer:**
I don't think we need the source. Confidence hint is interesting, but I'm not sure how we'd calculate it to be meaningful.

**Q7.5 ⚪ Watch actions:** acknowledge (stop repeat), "in shelter" mode (suppress ≤L2 for 30 min), snooze source,
"open map on phone". Which of these do you want?

**Answer:**
I think I want a shelter mode, acknowledge, and open map on the phone. The shelter mode should probably be configurable 

**Q7.6 ⚪ Phone UI scope for v1:** just settings + event log, or also a map of active tracks?
*Suggestion:* settings + event log + simple map later.

**Answer:**
I agree with your suggestion. What we need to test in the MVP is the general feel of this system, and calibrate the timings + alerts.
---

## 8. Reliability, privacy, legal

**Q8.1 🟡 Testing with history:** I'd build a **replay harness** first. It feeds the 2 years of Kharkiv Life + Air
Force exports through the pipeline at real or accelerated speed and reports which alerts would have fired.
OK to make this the first deliverable?

**Answer:**
Okay. We need some way to test it, so why not.

**Q8.2 ⚪ Logging:** keep a local history of received messages, parsed events and fired alerts (for tuning)? How long?

**Answer:**
I think a few days is the most we need. Unless it's quite cheap, then we can have it up to a few weeks. Not sure if any longer is useful.

**Q8.3 🟡 Privacy:** with a server, should it **broadcast all parsed threats** (or per-oblast topics) and let the
phone decide relevance locally, so your location never leaves the phone?
*Suggestion:* yes.

**Answer:**
Yes. The PC should just send the targets datapoints, and the phone would decide what is relevant to display.

**Q8.4 ⚪ Disclaimers / terms:** fine with an in-app disclaimer ("not an official warning system, always follow
official alerts"), NEPTUN attribution, and no redistribution of others' data beyond your own devices?

**Answer:**
Agreed
---

## 9. Project setup

**Q9.1 🟡 Stack preferences.** Suggested: Kotlin + Jetpack Compose (phone), Kotlin Wear OS module (watch), Python
server (Telethon, asyncio, Anthropic SDK). The repo lives under `cpp/`. Do you want C++ anywhere (e.g. a shared parser
core), or is that just your folder layout?

**Answer:**
Given that I've decided to use the PC, update the stack accordingly. As for the c++, I don't mind if we use anything else. The cpp folder is named as such for historic reasons, I have plenty of other languages here.

**Q9.2 🟡 MVP definition.** Proposal:
1. Replay harness + eval set from the exports.
2. Server: Telegram ingest (kpszsu + Kharkiv Life) → fast path + Haiku parser → gazetteer → simple track fusion.
3. Phone: receives FCM events, filters by your location, 5 notification channels.
4. Watch: bridged notifications first; a custom Wear OS vibration app second.

Later: NEPTUN/war-monitor fusion, ETA map, more channels, on-device fallback. Agree or reorder?

**Answer:**
The server should run on the PC, the phone should ingest the datapoints from it and choose what to show. What protocol we'd use between the PC and the phone is up to you, I was thinking about using Telegram as the convenient backbone, but I'm open to suggestions. Otherwise I agree.

**Q9.3 ⚪ The `data/` exports (≈270 MB) are untracked.** Add `data/` to `.gitignore` and commit only a small curated
sample (a few thousand messages as JSONL) for tests?

**Answer:**
Yes.

**Q9.4 ⚪ Anything else** about how you use alerts today (what annoys you in existing apps, what you wish they did)?

**Answer:**
The gov alerts are too noisy, I end up checking the telegram channels anyway. I don't even remember having heard the official alert half the times (the brain just filters them out). The existing apps aren't showing the notifications on the watch, afaik. Though I haven't investigated the existing apps yet (do you have suggestions?)
