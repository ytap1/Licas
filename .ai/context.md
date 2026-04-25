# Context: LIKAS

> Single source of truth Claude reads at the start of every session.
> Keep under ~150 lines. Link out instead of inlining.

Last updated: April 25, 2026

## What This Is

LIKAS is an offline-first disaster intelligence Streamlit app for Philippine
DRRM officers powered by Gemma 4. LIKAS means "to evacuate" and "natural"
in Filipino.

- **Problem:** Philippine DRRM officers lack real-time AI-assisted flood analysis and bilingual (Filipino/English) evacuation alerts during disaster events.
- **User:** DRRM officers in Philippine local government units.
- **Success:** Officer generates a flood situation analysis and bilingual evacuation alert within 60 seconds from a single Streamlit interface.

## Current State

- **Phase:** pre-alpha
- **Version:** 0.1.0
- **Deployed?** No
- **Users?** None
- **Known broken:** App not yet built — no source files exist.

## Stack

Python · Streamlit · Streamlit Community Cloud · Google AI Studio API (Gemma 4)

## Key Constraints

- Single `app.py` entry point; no build step.
- API key via Streamlit secrets (`.streamlit/secrets.toml`) — never committed.
- All AI responses must be bilingual: Filipino and English.
- API unavailable → display error banner; no silent fallback.
- No local-dev assumption — verify only on Streamlit Community Cloud deploy preview.
- No new top-level Python dependencies without an ADR.

## Entry Points

- **Main file:** `app.py` (does not exist yet — first file to create)
- **Config:** `.streamlit/secrets.toml` (not committed; set in Streamlit Community Cloud dashboard)
- **Tests:** none yet
- **Deploy config:** Streamlit Community Cloud connected to GitHub `main`

## See Also

- `.ai/conventions.md` — coding rules
- `.ai/decisions.md` — ADRs
- `docs/workflow.md` — full working model
- `docs/architecture.md` — structure + data flow
