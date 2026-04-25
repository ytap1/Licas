# LIKAS

> Offline-first disaster intelligence Streamlit app for Philippine DRRM officers powered by Gemma 4. LIKAS means "to evacuate" and "natural" in Filipino.

## Status

- **Phase:** pre-alpha
- **Version:** 0.1.0 (see [CHANGELOG.md](./CHANGELOG.md))
- **Last updated:** April 25, 2026
- **Deployed?** No.

## How Work Happens Here

- Edits via Claude Code (GitHub integration) or the GitHub web editor on Safari.
- No local dev, no terminal, no package managers — never assume them.
- Push directly to `main` by default. Branch only for destructive or high-risk changes.
- Deploy is auto-triggered on push to `main` (Streamlit Community Cloud).
- Verification happens on the deployed preview, not on a localhost.

See [docs/workflow.md](./docs/workflow.md) for the full working model.

## What Works

- AI-first docs in [`.ai/`](./.ai/) — fully filled in for LIKAS.
- `CHANGELOG.md`, `docs/`, `.gitignore` scaffolding.

## What's Next

- [ ] Build `app.py` — Streamlit UI with flood-data input form.
- [ ] Wire Gemma 4 via Google AI Studio API.
- [ ] Bilingual (Filipino/English) alert generation.
- [ ] Safe route recommendation panel.
- [ ] Deploy to Streamlit Community Cloud.

## Documentation

- [CLAUDE.md](./CLAUDE.md) — read first; how Claude should work in this repo
- [.ai/context.md](./.ai/context.md) — what this is, current state, constraints
- [.ai/conventions.md](./.ai/conventions.md) — coding rules
- [.ai/decisions.md](./.ai/decisions.md) — ADRs
- [.ai/prompts.md](./.ai/prompts.md) — prompt templates
- [.ai/metrics.md](./.ai/metrics.md) — AI-assist log
- [docs/workflow.md](./docs/workflow.md) — working model + deploy
- [docs/architecture.md](./docs/architecture.md) — structure + data flow
- [CHANGELOG.md](./CHANGELOG.md) — release history
