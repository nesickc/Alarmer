# Alarmer — round 2

Same format: write under **Answer:**; "ok" accepts the suggestion. Part A is what I took from your answers, so correct
anything I got wrong. Part B is what's still open. Background for both is in [research.md](research.md) R-9.

---

## A. What I took from round 1

| # | Decision |
|---|---|
| D1 | Users: you + family now. Nothing in the design should assume a single user. |
| D2 | Coverage: all of Ukraine, so regional Telegram channels for every oblast. |
| D3 | **Architecture:** the PC is the "brain" (Telegram ingest → keyword filter → fast path → local LLM → gazetteer → track fusion). It broadcasts **target records** (position, type, heading, speed, destination). The phone decides what's relevant from GPS/saved places, and the watch is the output. Records don't depend on their source, so structured military data could later replace text parsing without touching the phone. |
| D4 | Self-hosted LLM on the PC, $0/month apart from electricity. |
| D5 | Galaxy Watch 7 + Xiaomi 17T Pro. Alerts go to the watch only. The phone vibrates only when the watch isn't connected, and sound is optional. |
| D6 | Sources for v1: Telegram (`@kpszsu`, Kharkiv Life, `@war_monitor`, regional channels), with NEPTUN as corroboration only. No official-alert API. Ask war-monitor for access once the app works. |
| D7 | Relevance is based on **time to impact**, not distance. ETA bands get calibrated from explosion-vs-threat data (a data-mining side task). |
| D8 | Ballistics: a *threat* is a yellow alert. A *launch* is red for every city in range unless a target is named (refined in Q10.4). |
| D9 | The only non-threat content kept is explosion reports; promotions, aftermath and news are dropped by a keyword filter. |
| D10 | First deliverable: parser + replay harness on the exports. The PC keeps message logs (cheap, and they become our dataset); the phone keeps a few days. |
| D11 | Sideload for the MVP, Google Play later. Disclaimer + NEPTUN attribution in the app. |
| D12 | Watch actions: acknowledge, configurable shelter mode, open map on phone. Night hours are configurable. Throttling, track lifetime and the confidence hint get decided after testing the MVP. |
| D13 | Phone ↔ watch: the Wear OS Data Layer (free, over Bluetooth, no internet). The watch app plays a vibration pattern per level and shows a full-screen alert for critical ones. (Q4.4 in round 1 was really about PC → phone, which is Q10.2 below.) |
| D14 | SMS fallback is parked. One note for later: the PC can only send SMS through a GSM path at home, such as a USB modem or a spare Android phone with a SIM as a gateway. |

**Corrections:**

---

## B. Open questions

**Q10.1 🔴 Will this laptop be the 24/7 machine?**
It has an i5-12450H, 32 GB RAM and an RTX 3060 Laptop GPU with 6 GB VRAM, and it has a battery. Blackouts cut power
**and** home internet together, often during the same attacks we want to catch. The laptop battery covers power for a
while, but the router/ONT also needs backup.
Options:
(a) accept the downtime, and the phone shows "monitoring lost";
(b) put the router on a UPS or power bank and keep the laptop plugged in with a battery charge limit (if it's a Lenovo,
as the battery ID suggests, Vantage's conservation mode does this);
(c) later, run a second copy of the pipeline on a free cloud VM (CPU only, smaller model), with the phone taking
whichever source is alive.
Also: is the GPU free for the LLM permanently (~3–5 GB VRAM), or do you game or train on it?
*Suggestion:* (b) now. Design the pipeline so (c) is possible later.

**Answer:**
The internet works pretty well, I have UPS for the router and the modem. The outage doesn't affect the provider. I also have a large backup battery for the entire home. So running the inference on this laptop is fine. I'll also have an RTX 5080 machine for training, if we need that.

**Q10.2 🔴 PC → phone transport.** I recommend **Firebase Cloud Messaging (FCM)** over Telegram.
* Why not Telegram: for the phone app to read structured messages from a chat, it would need its own Telegram client
  logged in on the phone (TDLib + a user account). Bots don't see other bots' messages, and Telegram's push only wakes
  the Telegram app, not ours.
* FCM is free, and high-priority messages wake the app from Doze in about a second.
* The catch: FCM downgrades high-priority messages that don't lead to a visible notification [R-9], and with
  phone-side filtering most messages won't. Two fixes:
  1. One FCM topic per oblast. The phone subscribes to its own oblast and its neighbours, so far-away records never
     reach it. Google can see which oblast topics a phone subscribes to; the PC learns nothing else.
  2. Each message updates a silent ongoing notification ("Активних загроз поруч: 3"), which should count as visible.
     I'll verify that in a spike.
* Optional extra: during an active local threat, the phone holds a direct connection to the PC over Tailscale (free)
  for second-by-second updates.
* Optional fallback: the PC's bot also posts a one-line human-readable version to a **private Telegram channel**. It
  costs nothing, doubles as a debug log, and gives you something to read if our app breaks.

Agree with FCM + oblast topics + the Telegram mirror channel?

**Answer:**
I think it's fine to keep FCM only then, if it's free and has good uptime. We can have an ongoing notification, it's good enough. Keeping one FCM topic per oblast might make sense, but I'm not sure it's necessary.

**Q10.3 🟡 The target record.** A first draft of what the PC sends (one JSON per FCM message; several are batched
during floods, limit 4 KB):
```json
{"v":1, "seq":18342, "ts":"2026-10-30T21:14:05Z",
 "kind":"track", "id":"t-7f3a", "status":"active",
 "type":"uav.jet", "pos":{"lat":50.05, "lon":36.42, "r_km":5},
 "heading":{"deg":250, "pm":30}, "speed_kmh":400, "dest":"ua:kharkiv",
 "launch_area":null, "conf":0.7, "src_n":2, "ttl_s":600}
```
`kind` is one of `track` (a moving object), `area` (e.g. "КАБи на північ Харківщини"), `ballistic_threat`, `launch`,
`explosion`, `official_alert`, `all_clear`. The phone computes the ETA from distance and speed and picks the level.
`seq` lets the phone notice gaps and ask the PC for a full snapshot. Does this cover what you had in mind, or should the
phone receive raw text too (e.g. to show the original post)?

**Answer:**
This is great, I think it's enough data.

**Q10.4 🔴 Ballistic rule, checked against the data.** In 2026, threat posts and launch posts are clearly different
(table in R-9). Launch posts **almost always name a target** ("Балістика на Київ!", "Ракета на Харків", "Швидкісна
ціль на Дніпро"). Kharkiv Life also names the **launch area** ("з Брянська / Таганрогу / Криму"), sometimes adding
"для нас без загрози". Questions:
* (a) 550 km from the Russian border covers almost all of Ukraine except the far west. Should we measure from the
  **stated launch area** instead (Брянськ, Курськ, Бєлгород, Воронеж, Таганрог, Крим, occupied territory), and fall back
  to "border + occupied territory" when it's unknown? Include Belarus?
* (b) Target named: red for that city plus what radius? Does everyone else in range drop back to yellow?
* (c) Should "Швидкісна ціль" (could be ballistic, Кинджал, Х-22 or Бандероль) be treated exactly like a ballistic
  launch?
* (d) Level names: is yellow = **L3 High** and red = **L4 Critical**? (Round 1 used "high" and "yellow" for the same
  case.)
* (e) If a local channel says "для нас без загрози", may it downgrade the threat for that city?

*Suggestion:* (a) yes, without Belarus unless launches from there resume; (b) 30 km; (c) yes; (d) yes; (e) only to
yellow, never to nothing.

**Answer:**
Banderol is a cruise missile. Kh-22 is pretty fast, but not as fast. Kinzhal and Iskander are basically the same, so those should be treated as a ballistic launch. Zircon is even faster, so also high alert. L3 is orange, L2 is yellow, L4 is red. If a local channel says without threat to us then set it to L2 for that city. There's one point about these, high speed targets are a threat along their vector, imo. There was an instance where Zircon first was predicted for Kyiv, but it struck Vinnytsia in 2 minutes instead. We should keep it in mind somehow. As for when target is named, I'd extend the radius to 50 km. We should not include belarus in the calculations, they almost never launch from there. Though the russians do launch Kinzhals from Crimea, which is a separate threat (it's usually labeled as such). 

**Q10.5 🔴 Official alert as the lowest tier.** You want it with its reason, but without the official-alert API. My
proposal: read the official «Повітряна тривога» Telegram channel (`@air_alert_ua`, to be verified) with the same
account. It has a fixed format, so no LLM is needed. The reason comes from what the Air Force posts in the same minutes,
e.g. "Тривога · Харківська обл. · ☄️ загроза балістики з півночі". OK?

**Answer:**
Yeah, sounds reasonable.

**Q10.6 🔴 Local LLM plan.**
* Engine: **llama.cpp** `llama-server` (C++, runs on Windows with CUDA). It can force output to follow a JSON schema,
  so every reply is valid JSON.
* Candidates, benchmarked on our eval set: Qwen3-4B, Qwen3-8B (4-bit), Gemma 3 4B, and a Ukrainian-tuned Gemma
  (MamayLM) with CPU offload as a quality reference. We pick the smallest one that passes.
* Expected speed: ~1 s per message for a 4B model on this GPU. Your keyword filter removes most non-alert posts
  before the LLM sees them.
* Bursts: in a mass attack, 50–100 channels can queue up. The rule-based fast path fires critical alerts without the
  LLM, and the queue processes ballistic and local posts first.

Any model you'd specifically like tried? And is a Qwen-family model acceptable to you (some people avoid Chinese
models for this kind of use)?

**Answer:**
No particular preferences, we should benchmark the models and use the fastest one that covers our needs. We don't need super detailed reasoning here, it's loose text parsing basically.

**Q10.7 🟡 Auto-labeling while staying at $0.** The live system stays free whatever we pick; this only concerns
building the eval/training labels once:
(a) a one-time ~$1–3 of cloud API calls for labeling only;
(b) I label batches here in Claude Code (uses your Claude subscription, not money; slower);
(c) the biggest model the laptop can run labels them, and you review more.
*Suggestion:* (b) for the ~500–1000-message eval set, (c) for bulk training data later.

**Answer:**
I think it's reasonable to utilize the Claude Code sub for this. There can be several Sonnet agents in parallel doing the labeling

**Q10.8 🟡 Channel discovery for all of Ukraine.**
* I'll compile a candidate list per oblast: monitoring channels, city channels, and official ОВА / city-hall channels.
* With your second account, Telethon can pull months of history from public channels, so no manual exports are needed.
  That lets us score each channel before adding it (Q10.9).
* Limits: a non-Premium account can join ~500 channels, which is plenty. Joins have to be spread out to avoid
  Telegram's flood limits.

OK to use the account for history fetching? Shall I start the list now?

**Answer:**
Sure. Though which account are you intending to use, and how do you access it? I have a second account for these purposes (not the main one logged into right now)

**Q10.9 🟡 Trust score.** Proposal: a score per **(channel × threat type × region)**, recomputed weekly from the logs.
It would combine:
* how often the channel's reports are confirmed (by the Air Force, another channel, or a later explosion);
* its median lead time vs the Air Force;
* its false-alarm rate.

Manual overrides always win. The score sets how much one message counts. A critical keyword from a channel above a
threshold fires on its own; below the threshold it needs a second source. Good basis?

**Answer:**
I feel like we should gather historic data and see. I don't think updating the score weekly makes sense, it's too granular. We can have it done once a few months at most.

**Q10.10 🟡 Explosion data mining.** With the current exports I can already measure, for Kharkiv, the time from a threat
post of each type ("реактив на …", "КАБ на …", "балістика") to the next "вибух" post. That gives first ETA bands and
shows how often each threat type ends in an explosion. Other cities follow once we fetch their channels' history. Do
it right after the parser works (it needs threat types parsed first)?

**Answer:**
Sure, we don't really require this data before the parser is functional anyway

**Q10.11 ⚪ єППО / Флюгер.** Флюгер is made by KB «Технарі» (Odesa) as part of the єППО system. It shows azimuth and
15/30/45 km rings, which is close to what we're building. I found **no public API**, and its data source isn't
published [R-9]. Add KB «Технарі» to the "ask for data access once our app works" list, next to war-monitor?

**Answer:**
Yeah, we may keep it for the future. Add "Віраж", "Графіт" and "Дельта" as potential future sources. If we succeed these ones would provide accurate data straight from the military online, which could save countless lives when scaled across the country. Though we'd need to assume the russians would have access to what we push as datapoints, so we'd need to ensure safety for the tracking equipment (the russians could calculate the radars' locations if we aren't careful). These are hypothetical and for the future, so treat them as such.