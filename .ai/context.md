# Context: {{PROJECT_NAME}}

> Single source of truth Claude reads at the start of every session.
> Keep under ~150 lines. Link out instead of inlining.

Last updated: {{CURRENT_DATE}}

## What This Is

{{PROJECT_NAME}} is {{PROJECT_DESCRIPTION}}.

Answer in one sentence each:

- **Problem:** <what specific pain this solves>
- **User:** <who uses it>
- **Success:** <observable outcome that means it works>

## Current State

- **Phase:** pre-alpha / alpha / beta / production (pick one)
- **Version:** 0.1.0
- **Deployed?** No / URL
- **Users?** None / count
- **Known broken:** <list load-bearing things that fail>

## Stack

{{TECH_STACK}}

Fill in once chosen. Do not assume a stack — this template is intentionally
neutral. List only what is actually picked: language, framework, storage,
deploy target.

## Working Model

Hard rules about how work happens here. Do not violate without asking.

- **No local execution.** The user works from iPad/iPhone via Safari + Claude
  Code. There is no terminal, no `make`, no `npm`, no `curl localhost`.
- **No CLI instructions in docs.** If a step needs a command, it has to run
  in CI or in Claude Code's own sandbox — never on the user's machine.
- **Push directly to `main`** by default. Branch only for destructive or
  high-risk changes (schema rewrites, mass renames, deletions).
- **Deploy is automatic** on push to `main` (GitHub Pages or Netlify).
  Verification happens on the deployed preview, not localhost.
- **Multi-chat workflow.** The user maintains separate Claude chats per
  concern (e.g. App Dev, Prompt Refinement). Stay in the lane named in
  the current chat unless told otherwise.

## Key Constraints

Project-specific rules. Edit per project.

- <e.g. "Single HTML file — no build step.">
- <e.g. "No new top-level dependencies without an ADR.">
- <e.g. "Secrets only via Netlify env vars, never committed.">

## Entry Points

Where Claude should start reading when picking up cold. Links, not commands.

- **Main file(s):** <path(s)>
- **Config:** <path>
- **Tests (if any):** <path>
- **Deploy config:** <path, e.g. `netlify.toml` / `.github/workflows/pages.yml`>

## See Also

- `.ai/conventions.md` — coding rules
- `.ai/decisions.md` — ADRs
- `docs/workflow.md` — full working model
- `docs/architecture.md` — structure + data flow
