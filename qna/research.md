# Alarmer — research notes (2026-10-30)

Background for the spec. The questions themselves live in [questions.md](questions.md); each one refers to a
section here as **[R-x]**.

> These notes are a snapshot from before the decisions were made. Where they disagree with
> [docs/spec.md](../docs/spec.md) or the [ADRs](../docs/adr/README.md) (for example, R-7 recommends a cloud LLM), the
> spec and the ADRs win.

---

## R-1. The sample Telegram data (`data/`)

Both folders are Telegram Desktop HTML exports. I parsed them into `{id, ts, text, media, reply_to}` records.

| | `kpszsu_chats` (Повітряні Сили ЗСУ) | `kharkivlife_chats` (Харків Life) |
|---|---|---|
| Messages | 91,105 | 61,428 |
| Period | 18.02.2019 → 30.10.2026 | 01.10.2024 → 30.10.2026 |
| Volume, Oct 2026 | 9,437 (~300/day, growing fast: 2.5k/month a year ago) | 3,785 (~120/day) |
| Median text length (2025+) | 56 chars | 36 chars |
| Messages that are replies (2025+) | ~11% (reply chains up to 14 deep) | ~12% |
| Non-threat content (2026, rough) | <1% (daily summaries, PR posts) | ~25% (news, aftermath, blackout schedules, ads) |

### Air Force channel (kpszsu): semi-structured
* A leading emoji encodes the threat class:
  `🛵` Shahed/UAV · `🏍` jet Shahed (Geran-3) · `☄️` ballistic **threat** (area-level, often "з півночі") ·
  `🚀` concrete missile / "Бандероль" / older KAB posts · `💣` KAB · `🛸` recon UAV · `🛫/🛬` tactical aviation ·
  `📢` all-clear · `⚡️` morning summary · `⚠️ Увага!` older generic format.
* **Reply chains work like track IDs.** For example, `91380 🏍 …вздовж Київського водосховища курсом на Вишгород/Київ`
  → reply `Мінський масив` → `Куренівка` → `Сирець` → `Відрадний` → `Чабани` → `Глеваха`. One target's path through the
  city, one hop per reply.
* Typical grammar: `<emoji> [Область:] <type> [кількість] (курсом на|в напрямку|на|повз|через|над) <place> [з <side>]`.
  Examples: `🏍 Реактивний БпЛА на Харків з північного заходу`, `🚀Балістична ракета курсом на Полтаву з Харківщини`,
  `🏍 Реактивний БпЛА над Харковом. Перебувайте в укриттях!`.
* **The format drifts.** `🏍` and `💣` only appeared on **20.08.2026** (10.7k `🏍` messages since then; jet Shaheds now
  dominate). In 2023 the channel posted oblast-level "ракетна небезпека" bulletins. In early 2025 it posted
  "⚠ Увага! м.Харків! У вашому напрямку ворожий БпЛА з північного сходу". A hard-coded parser would have broken twice
  in this period.

### Kharkiv Life: noisy, hyper-local, fast
* City-level alert state: `🚨 М. ХАРКІВ - ОГОЛОШЕНА ПОВІТРЯНА ТРИВОГА` + sub-line (`Загроза по БпЛА 🟡`,
  `Балістична загроза з Курська 🔴`, `Загроза по Бандеролям 🔴`), and `❎ М. ХАРКІВ - ВІДБІЙ ТРИВОГИ`.
* Neighbourhood-level tracks: `Реактивний БПЛА курсом на Нову Баварію`, `3 на Куліни/ХТЗ`, `ХГ/Баварія`, `МД`,
  `Пісочин`, `Аеропорт`, `upd: без фіксації`, `upd: Вилетів в область`, `Вибух`, `Чисто`.
* **About two thirds of follow-ups have no reply link** (2026: 3,586 implicit vs 1,870 explicit short follow-ups within
  3 min). A bare `Аеропорт` only makes sense next to the message before it, so the parser needs the recent channel
  context.
* Slang and abbreviations (counts in 2025+): `КР` (cruise missile, 4.5k), `Молнія` (1.3k), `КАБ` (1.3k), `БНР`
  (Belgorod direction, 358), `ХГ`, `МД`, `реактив`, `Ланцет`, `МіГ-31`, `Кинджал`, `🟡/🔴` severity.
* Every message carries a footer (`Надіслати новину @Kharkiv_Lifebot / 👉ПІДПИСАТИСЯ`) that must be stripped.

### Which channel is faster? (rough, 2026 data)
I matched messages of the same kind within ±10 min. This is crude matching, so treat the numbers as indicative only:

| Event kind | Matched pairs | Median (Kharkiv Life − Air Force) | Kharkiv Life first |
|---|---|---|---|
| Ballistic threat | 442 | **−28 s** | 63% |
| KAB on Kharkiv oblast | 246 | **−68 s** | 64% |
| Jet UAV at/over Kharkiv city | 84 | +22 s | 42% |

**Takeaway:** for Kharkiv, the regional channel often posts tens of seconds earlier on the threats that matter most.
Pulling from several sources pays off.

### Ukrainian grammar is a real parsing problem
Place names arrive inflected: `на Лубни` / `Лубнів`, `повз Березну` (Березна), `на Дергачі`, `Броварів`, `Харковом`,
`Кременчука`. Matching against a gazetteer needs lemmatization or an alias table of inflected forms, whether or not an
LLM is used.

---

## R-2. map.war-monitor.org (project "monitor", @war_monitor, ~960k subscribers)

* It is a client-side MapLibre app. Data comes from `https://api.war-monitor.org/v2/map`. Session setup is
  `POST /v1/session {turnstile, device_pub}`: a **Cloudflare Turnstile** challenge plus a per-device key pair, which
  yields a short-lived `X-Pass`. Polling runs every ~20 s with threats and ~45 s without.
* **Their target schema is a good model for ours:**
  `{id, type, lat, lon, place, n(count), status(stale), first_seen, last_seen, heading(deg), dest{lat,lon,place},
  trail[[lat,lon,place]…], source:"@telegram_handle"}`, plus alerts `{title, kind: oblast|raion|hromada|city,
  level: yellow|red}`.
* **Their type taxonomy** (worth adopting as-is):
  `uav.geran_2 / geran_3 (jet) / geran_4 / gerbera / garpia / molnia / kub / recon / unknown`,
  `cruise.kh101 / kh55 / kh59 / kh69 / kh22 / kh31p / kh35 / kalibr / iskander_k / oniks / tsirkon / banderol /
  geran_5 / dan_m / unknown`,
  `ballistic.iskander_m / kn23 / kinzhal / 5v55 (S-300) / 48n6dm (S-400) / rm48u / oreshnik`, `unknown.fast`.
  The map filters out `kab`.
* Data sources they state: their own observation, radio, regional monitoring channels, and official alerts. The
  `source` field holds a Telegram handle, so they also aggregate Telegram.
* **No public API, and it is deliberately bot-protected.** Using it means asking them for partner access. Getting
  around Turnstile is off the table. Their Telegram channel is a legitimate text source.

## R-3. Official sources

**«Повітряна тривога» (Ajax/Stfalcon, Мінцифри, Міноборони), map.ukrainealarm.com**
* Since **17–18 Oct 2026** the app and official map show **approximate movement of Shaheds, cruise missiles and
  «Бандероль»**. The data comes from Air Force systems, is checked by the military, and is deliberately coarsened (zone
  only, 10×10 km grid, a "Підвищена небезпека" heatmap).
* **Ballistic threats are not shown** ("too fast for the map to be useful"; >2000 km/h targets excluded). Ballistic
  warnings stay in the Air Force Telegram channel.
* The web map gets this over an internal Centrifugo WebSocket (`/api/centrifuge/map/subscribe`, plus a `map/diia`
  variant). It is not a published API. The documented API (`api.ukrainealarm.com`) needs a key requested via a form, and
  it is not clear whether it includes targets.
* The Prime Minister has announced a Diia-based state alert app that will also show drone and missile movement (not
  released yet, as far as I found).

**alerts.in.ua API** (`api.alerts.in.ua`)
* Token by request. Alert types `air_raid, artillery_shelling, urban_fights, chemical, nuclear`; levels `red/yellow`;
  resolution down to **hromada/city UID**; IoT endpoints give a compact status string.
* Limits: soft 8–10, hard 12 requests/min per IP. Supports `If-Modified-Since`. Polling only, no push.
* Rules: **don't ship the token in a mobile app; proxy through your own server** (physical IoT devices are exempt).
  Not for critical infrastructure.

**єППО** (Google Play `ua.quick.brpg.pathfinder`, Technari volunteers)
* It is a **crowd-sourcing app for reporting** sightings (Shahed, cruise missile, aircraft) to the Air Force. The last
  Play update was Jan 2026 (Android 16 support).
* I found **no public outbound feed or API**. It is an input to the military picture, not something we can read from.
  (The official map's icon folder is called `vppo/`, which may hint that crowd reports feed the official map, but that
  is unconfirmed.)

## R-4. Other aggregators / channels

**NEPTUN (neptun.in.ua): open, free, documented API**, terms updated 09.07.2026
* REST `GET /api/v1/threats`, `/api/v1/alerts`, `/api/v1/messages`; **WebSocket `wss://neptun.in.ua/api/v1/stream`**
  (snapshot / upsert / remove / heartbeat / alerts). No key. Poll no more than every 5 s. Commercial use allowed.
  **Visible attribution required.** Must state that it is not an official warning system.
* Track schema (live sample taken today): `id "trk_…", type (uav|recon|missile|ballistic|kab|mig31k|fpv|unknown),
  region, district, locality, lat, lon, heading, velocity{bearingDeg, speedKmh}, uncertaintyKm (4–28 km in sample),
  sourceCount, confidenceLevel, lifecycle, trail[], flags advisory / areaOnly`.
* Caveat: positions are coarse. A Kyiv-oblast UAV's trail started at Kyiv's centroid. It is still the only
  ready-made, legal, structured feed with IDs and vectors that I found.

**Telegram channels named in 2026 guides** (none verified by me for quality):
`@kpszsu` (Air Force, official), `@air_alert_ua` (official alerts), `@war_monitor`, `@deraketaua`, `@eRadarrua`,
`@radar_raketaa`, `@povitryanatrivogaaa`. Kharkiv-specific: Kharkiv Life; Kharkiv Life itself promotes a "radar.kharkiv"
online UAV map; Kharkiv city hall is said to run a monitoring channel; ХОВА/Синєгубов and Терехов post aftermath and
sometimes threats.

## R-5. Threat kinematics (for ETA / "is it coming at me")

| Type | Typical speed | Notes for Kharkiv |
|---|---|---|
| Shahed / Geran-2 | ~150–200 km/h (a NEPTUN track today: 202 km/h) | ~3 km/min: minutes to tens of minutes of warning |
| Jet Shahed / Geran-3 | 290–370 typical, peaks reported 500+ | ~5–6 km/min; now the dominant type |
| «Бандероль» (S8000) | ~480–680 km/h, ~300 km range | Hybrid drone/cruise missile; used on Kharkiv |
| Cruise (Kh-101, Kalibr…) | ~700–900 km/h | Often routed around; "КР вилітає на Полтавщину" |
| Ballistic (Iskander-M, S-300/400, KN-23) | Mach 5+ | From the Belgorod area, flight time to Kharkiv is roughly a minute or less: **practically no lead time** |
| KAB (guided bombs) | Glide tens of km | Launch → impact in a couple of minutes; Kharkiv oblast is a frequent target |

For ballistics, the only useful signal is the earliest possible "threat from direction X". Every second of pipeline
latency counts.

## R-6. Getting Telegram data
* The **Bot API cannot read public channels** unless the bot is an admin there. You need an **MTProto user client**
  (TDLib, Telethon/Pyrogram, gramjs) logged into a real Telegram account, with `api_id/api_hash` from my.telegram.org.
* Real-time updates arrive over the open MTProto connection (sub-second). On a server that is easy. On a phone the
  connection has to survive Doze, OEM battery killers and Android 14/15 foreground-service rules. TDLib supports FCM
  push registration (`registerDevice`), but whether that works for a third-party app with its own Firebase project
  needs a spike.
* Risks: the account can be limited for "automation". Use a dedicated account. Respect FLOOD_WAIT. Read only.

## R-7. LLM options for parsing

**Constraints:** messages are short (median 36–56 chars), but you need context (the last N messages from the same
channel, plus currently active tracks). Ukrainian slang and inflection apply. Volume is ~400–1000 messages/day. The
latency budget is about 1 s for the critical path.

| Option | Where | Fit |
|---|---|---|
| **Rules / regex + emoji + gazetteer** | anywhere, <10 ms | Excellent for kpszsu's critical keywords (`балісти`, `над Харковом`, `☄️`, `🚀`), but brittle under format drift and weak on Kharkiv Life slang. **Use as the fast path, not the only path.** |
| **Claude Haiku 5.5** (`claude-haiku-5-5`, $0.10 in / $0.50 out per MTok for prompts ≤100K) | server API | Strong Ukrainian; JSON-schema structured outputs (`output_config.format`); prompt caching (min. 512 tokens), so a long frozen system prompt + slang dictionary is cheap. Rough cost: 1,000 msgs/day × ~2.5k in + ~150 out ≈ **$0.30/day ≈ $10/month uncached**, less with caching. Latency is network-bound, so measure it in a spike. Thinking can be switched off (effort ≤ high) to save latency. |
| **Gemini Nano via ML Kit GenAI Prompt API** | on-device | ❌ for this app: **inference is only allowed while the app is the top foreground app**, so it can't run from a background service. Also limited to some flagships (Pixel 10, Galaxy S26, …). |
| **LiteRT-LM + Gemma 3 1B / Gemma 3n E2B / (Gemma 4 small)** | on-device, background OK | Gemma 3 1B on S24 Ultra: ~1.9k tok/s prefill (GPU), ~45 tok/s decode, so a 100-token JSON takes ~2–3 s. Gemma 3n E2B: ~16 tok/s decode, ~6+ s. Out of the box a 1B model will struggle with the slang; it needs fine-tuning or distillation on our 150k messages (auto-label with a big model, then train). Adds ~0.5–1.5 GB to the app plus heat/battery. |
| **Small fine-tuned encoder (NER + classifier, e.g. XLM-R-small-class)** | on-device, ~10–30 ms | Most robust offline option once we have labels. Needs a labelled dataset; doesn't "reason" about context. |
| Ukrainian LLMs (MamayLM 9–12B, Lapa 12B, both Gemma-based) | server GPU only | Good Ukrainian but overkill. Useful as offline labelers, not runtime parsers. |

**Recommendation (to be confirmed by your answers):**
1. A deterministic fast path fires the critical alerts straight away (<100 ms after receipt).
2. An LLM extracts a strict JSON event (type, count, from, to/via, heading words, neighbourhood, update-of, all-clear,
   confidence) using the last ~10 messages of that channel and the current active tracks as context.
3. Geocoding is done by a gazetteer (OSM + a hand-curated Kharkiv alias list), **not** by the LLM.
4. A track-fusion layer merges events from all sources, estimates ETA and direction relative to the user, and decides
   the alert level.
5. Start with Haiku 5.5 on a server. Build an eval set from the exports early. Distill to on-device later only if
   "no server" becomes a hard requirement.

## R-8. Android + watch constraints (verify in spikes)
* **Background:** Android 14+ requires a declared foreground-service type. Android 15 caps `dataSync` at 6 h/24 h, so
  a 24/7 listener needs `specialUse` (needs a Play Console justification if published) or a server + FCM design.
  OEM killers (Xiaomi, Samsung, Huawei) need battery-optimisation exemptions. **High-priority FCM** is the most
  reliable way to wake the phone under Doze.
* **Loud alerts:** bypassing Do Not Disturb needs Notification Policy access granted by the user. Full-screen intents
  on Android 14+ are restricted to calling/alarm apps (Play policy). Alarm-stream audio is an alternative.
* **Watch:** notifications bridge to the watch automatically, but **per-level vibration patterns** on Wear OS need a
  small watch-side app (phone → watch over the Data Layer, then `Vibrator` waveform). Garmin needs a Connect IQ app
  and has tighter background limits. Zepp/Mi Band/Huawei each have their own SDKs or none, often allowing only
  per-app vibration via their companion app.

## R-9. Round-2 findings (after your answers)
* **Флюгер** is made by the Odesa bureau KB «Технарі» and described as *part of the єППО system*. It started as a
  simple radar for air-defence posts and was opened to the public because it "doesn't expose sensitive data". It
  shows azimuth plus 15/30/45 km distance rings, updates every 20–60 s, covers all of Ukraine, and runs on Android and
  iOS (since 18.07.2025). None of the coverage mentions ballistics, a watch app, or a public API, and none says where
  its data comes from. So єППО-derived data is reachable only by asking KB «Технарі» directly.
* **«Повітряна тривога»** (Ajax / Мінцифри): loud even in silent mode, Apple Watch support on iOS; I found no Wear OS
  app.
* **FCM priority:** high-priority messages that don't result in a user-visible notification "may be deprioritized to
  normal priority". FCM judges this over 7 days per app instance. A "send everything high-priority, let the phone
  filter" design would get downgraded; normal priority can be delayed in Doze.
* **This PC:** i5-12450H (8 cores), 32 GB RAM, RTX 3060 Laptop GPU with 6 GB VRAM, has a battery. 6 GB fits a 4B model
  at 4–5-bit fully on the GPU; an 8B model at 4-bit is tight; 12B+ needs partial CPU offload (several times slower).
* **Ballistic wording in the 2026 data:**

  | | Threat (no launch yet) | Launch / target named |
  |---|---|---|
  | Air Force | `☄️ Загроза застосування балістичного озброєння [з півночі / з півдня / зі сходу / з північно-східного напрямку]` (~450); all-clear `📢 Відбій загрози застосування балістичного озброєння` (~420) | `Балістика на Київ!`, `Ракета на Запоріжжя!`, `🚀Швидкісна ціль на Дніпро`, `🚀2 балістичні ракети на Київ!`, `🚀Балістична ракета на Полтавщині курсом на Кременчук` |
  | Kharkiv Life | `Загроза (пусків) балістики з Брянська / Таганрогу / Курська / Криму / БНР`, `Додалась загроза пусків балістики`, `Активність пускових`, `…з Криму, станом на зараз для нас без загрози` | `Ракета на Харків`, `Балістика на Харків`, `Швидкісна ціль на Харків`, `Ракета на Чугуїв`, `Повторні пуски балістики з Вороніжу` |

  Launch posts almost always name a target city. Launches with no target are rare. Kharkiv Life names the *launch
  area*, while the Air Force gives only a compass direction.

### Sources
* war-monitor: [map](https://map.war-monitor.org/), [site](https://war-monitor.org/), [dev.ua on the map](https://dev.ua/news/mapa-shakhediv-vid-monitor-1791880610), [DOU](https://dou.ua/lenta/news/monitor-beta-test-mapy-povitrianykh-tsilei/)
* Official map: [MediaSapiens 18.10.2026](https://ms.detector.media/trendi/post/39606/2026-10-18-u-zastosunku-povitryana-tryvoga-zyavylas-karta-rukhu-raket-i-shakhediv/), [informator.ua (Ігнат on ballistics)](https://informator.ua/uk/u-zastosunku-povitryana-trivoga-ne-pokazuvatimut-ruh-balistiki-ignat-poyasniv-prichinu), [map.ukrainealarm.com](https://map.ukrainealarm.com/), [DOU: «Повітряна тривога» API](https://dou.ua/lenta/news/air-alarm-application-version-3/)
* [alerts.in.ua API docs](https://devs.alerts.in.ua/) · [ukrainealarm wrapper (key form)](https://github.com/PaulAnnekov/ukrainealarm)
* [NEPTUN developers](https://neptun.in.ua/developers) · [NEPTUN API terms](https://neptun.in.ua/api-terms)
* єППО: [Google Play](https://play.google.com/store/apps/details?id=ua.quick.brpg.pathfinder), [DOU interview](https://dou.ua/lenta/interviews/air-defense-app/), [Ukrinform](https://www.ukrinform.net/rubric-ato/3930665-eppo-app-helps-ukraine-close-sky-by-80.html)
* Channel guides: [netfreedom 1](https://netfreedom.org.ua/karta-tryvog-telegram-povnyj-gid-po-kanalah-mapah-ta-spovishhennyah/), [netfreedom 2026](https://netfreedom.org.ua/de-raketa-v-telehram-povnyi-hid-z-monitorynhu-povitrianykh-zahroz-u-2026-rotsi/)
* Kinematics: [Pravda: jet Shaheds](https://www.pravda.com.ua/eng/articles/2026/05/19/8035370/), [Gwara: jet Shaheds in Kharkiv](https://gwaramedia.com/en/fast-and-almost-invisible-why-are-jet-powered-shahed-drones-harder-to-down-in-kharkiv/), [Слово і діло: Бандероль](https://slovoidilo.ua/2026/07/24/infografika/bezpeka/rosijska-banderol-vidomo-pro-novu-vorozhu-raketu-reaktyvnym-dvyhunom), [ТСН: Бандероль](https://tsn.ua/ato/rosiia-vdaryla-po-kyyevu-novoiu-banderolliu-chym-nebezpechna-tsia-dron-raketa-3106670.html)
* On-device LLM: [ML Kit GenAI overview](https://developers.google.com/ml-kit/genai), [LiteRT-LM benchmarks](https://ai.google.dev/edge/litert-lm/overview?hl=es-419), [MamayLM](https://huggingface.co/blog/INSAIT-Institute/mamaylm), [Ukrainian LLM leaderboard](https://dou.ua/lenta/news/ukrainian-ai-models-leaderboard/)
* Android: [Android 15 behaviour changes (FGS timeouts)](https://developer.android.com/about/versions/15/behavior-changes-15?hl=pt-br), [Wear OS notifications](https://d.android.com/wear/notifications/creating)
* Флюгер: [vikna.tv](https://vikna.tv/dlia-tebe/bezpeka/flyuger-zastosunok-dlya-poperedzhennya-povitryanyh-zagroz-v-ukrayini/), [Суспільне Одеса](https://suspilne.media/odesa/928529-radar-na-minimalkah-odeski-rozrobniki-vipustili-zastosunok-dla-viavlenna-povitranih-zagroz/), [dev.ua](https://dev.ua/news/fliuher-1737381024), [Komersant (iOS)](https://komersant.ua/en/dodatok-shcho-bachyt-shakhedy-fliuher-vzhe-pratsiuie-i-na-ios/)
* «Повітряна тривога»: [App Store](https://apps.apple.com/us/app/id1611955391), [KMU launch note](https://www.kmu.gov.ua/news/za-pidtrimki-mincifri-zapushcheno-zastosunok-povitryana-trivoga-dlya-operativnoyi-reakciyi-na-pochatok-i-zakinchennya-trivog)
* [FCM: Android message priority](https://firebase.google.com/docs/cloud-messaging/android-message-priority)
* TDLib: [registerDevice](https://tdlight-team.github.io/tdlight-docs/tdlight.api/it/tdlight/jni/TdApi.RegisterDevice.html), [account.registerDevice](https://gram.js.org/tl/account/RegisterDevice)
