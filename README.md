# 🌊 LIKAS

*LIKAS is the Filipino word for "to evacuate" and "natural" — as in natural disaster. One word. Two meanings. One mission.*

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://likas.streamlit.app)

---

## The Problem

Existing disaster alert systems in the Philippines leave critical gaps that cost lives:

1. **Alert latency** — warnings reach communities 30–90 minutes after sensors breach thresholds, when roads may already be impassable.
2. **Language barrier** — official DRRM alerts are issued in English; most flood-affected residents in rural Bulacan and Pampanga are Tagalog-first speakers.
3. **No route guidance** — alerts say *evacuate* but not *where* or *how* — especially when the usual roads are already flooded.
4. **Offline blindness** — typhoons knock out internet and mobile data precisely when coordination is most critical; existing tools go dark.

---

## Solution

LIKAS gives DRRM officers a dual-interface AI assistant powered by Gemma 4:

| Interface | Who It Serves | What It Does |
|-----------|---------------|--------------|
| 🧭 Command View | DRRM officer | Inputs sensor data + field photo → Gemma reasons → calls 4 disaster tools in sequence → generates bilingual alert + safe route |
| 📢 Resident View | Evacuating resident | Displays the officer's latest alert in plain Tagalog with step-by-step route instructions |

---

## Gemma 4 Features

| Feature | How LIKAS Uses It | Why It Matters |
|---------|-------------------|----------------|
| Agentic function calling | Calls `get_flood_map → calculate_safe_route → broadcast_alert → escalate_to_ndrrmc` in sequence | Automates the full response chain; officer confirms, AI executes |
| Bilingual generation | Produces simultaneous English + Tagalog alerts in a single inference pass | Residents receive instructions in their primary language at Grade 4 reading level |
| Structured reasoning | Explains threat assessment before every function call | Officer can audit and override AI decisions before broadcast |
| Offline-resilient design | Pre-computed fallback responses activate when API is unreachable | System stays operational when typhoon knocks out internet |

---

## How It Works

```
DRRM Officer (Mobile Safari)
        │
        ▼
┌───────────────────────┐
│  LIKAS — Streamlit    │
│                       │
│  Sensor Input         │
│  Photo / Description  │
│         │             │
│         ▼             │
│  Gemma 4 via          │
│  Google AI Studio     │
│         │             │
│         ▼             │
│  Agentic Tool Loop    │
│  ┌─────────────────┐  │
│  │ get_flood_map   │  │
│  │ safe_route ×N   │  │
│  │ broadcast_alert │  │
│  │ escalate_ndrrmc │  │
│  └─────────────────┘  │
└──────────┬────────────┘
           │
    ┌──────┴───────┐
    ▼              ▼
Residents      NDRRMC
(SMS / WiFi)  (Queued)
```

---

## Demo Scenarios

| Scenario | Location | Alert Level | Internet | Key Feature Demonstrated |
|----------|----------|-------------|----------|--------------------------|
| A — WATCH | Patubig, Bulacan | 🟠 WATCH | Online | Proactive monitoring before breach; Zone 1 notified |
| B — CRITICAL | Patubig, Bulacan | 🚨 CRITICAL | Online | Breach confirmed; mandatory evacuation; 2-zone routing |
| C — CRITICAL + Offline | 3 Barangays, Bulacan | 🚨 CRITICAL | **Offline** | Multi-barangay; NDRRMC report queued; WiFi mesh alerts |

---

## Setup

No terminal required. Everything done through web interfaces.

1. **Fork this repository** on GitHub (top-right → Fork)
2. **Deploy to Streamlit Community Cloud** at [share.streamlit.io](https://share.streamlit.io) — connect your fork, set `app.py` as the entry point
3. **Add your API key** in the Streamlit dashboard: App → Settings → Secrets

```toml
GEMINI_API_KEY = "your-google-ai-studio-key-here"
```

4. **Open your app URL** — the app works immediately in offline simulation mode even before the key is set

---

## The 4 Disaster Tools

| Tool | When Called | Returns |
|------|-------------|---------|
| `get_flood_map` | Always first | Flooded roads, safe roads, cached zone routes |
| `calculate_safe_route` | Once per affected zone | Step-by-step route, distance (km), walk time (min) |
| `broadcast_alert` | Once per alert-level group | Confirmation, channels used, estimated reach |
| `escalate_to_ndrrmc` | CRITICAL + multi-barangay only | Report ID, queued for auto-upload when internet restores |

---

## Sample Output

```
🚨 AGARANG LUMIKAS — Brgy. Patubig, Zone 1.
Umapaw na ang ilog. Pumunta na agad sa Patubig Elementary School.
Daanan: Gomez St → Rizal Ave → Maharlika Hwy.
HUWAG dumaan sa Burgos St at Riverside Drive.
```

```
🚨 CRITICAL ALERT — Brgy. Patubig, Zone 1. MANDATORY EVACUATION.
River has breached embankment. Proceed immediately to Patubig Elementary School
via Gomez St → Rizal Ave → Maharlika Hwy.
AVOID Burgos St and Riverside Drive.
```

---

## Why This Matters

In November 2013, Typhoon Haiyan killed more than 6,000 people in the Philippines — many because evacuation orders arrived too late, in the wrong language, or not at all. The gaps LIKAS addresses are not hypothetical: they are documented failure modes from Haiyan, Ondoy, and every major Philippine flood event since. LIKAS is not a research prototype. It is built for the DRRM officer sitting in a barangay hall at 2 a.m. with a rising river, a dead radio, and 3,000 people who need to know where to go.

---

## Built With

- [Streamlit](https://streamlit.io) — web app framework, zero-ops deploy
- [Google AI Studio](https://aistudio.google.com) — Gemma 4 inference API
- [Gemma 4](https://ai.google.dev/gemma) (`gemma-3-27b-it`) — bilingual reasoning and function calling
- [Streamlit Community Cloud](https://share.streamlit.io) — free hosting, auto-deploys on push to `main`

---

## License

Apache 2.0 — see [LICENSE](./LICENSE)

---

*Built for the Kaggle Gemma 4 Good Hackathon 2026 — by a Filipino developer, for Filipino communities.*
