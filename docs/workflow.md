# Workflow: {{PROJECT_NAME}}

How work actually happens on this project. If a future doc contradicts
this file, this file wins.

## Operating Constraints

- **Devices:** iPad and iPhone only. No laptop, no desktop, no terminal.
- **Browser:** Safari only.
- **Editor:** the GitHub web editor for tiny edits; Claude Code (via
  GitHub integration) for everything else.
- **No package managers.** Never `npm`, `pip`, `uv`, `cargo`, `brew`,
  `apt`, etc. on the user's side. If a step needs one, it runs in CI or
  in Claude Code's own sandbox.
- **No localhost.** The user can't browse `http://localhost:anything`.

## Branching

- **Default: push directly to `main`.** Auto-deploy is the feedback loop.
- **Branch only for destructive or high-risk changes.** Examples:
  - schema rewrites
  - mass renames or moves
  - large deletions
  - anything where a `git revert` wouldn't be a clean rollback
- Branch name format: `claude/<short-description>-<random>`.
- Delete the branch after merge.

## Deploy

- Auto-triggered on push to `main`.
- Target: GitHub Pages or Netlify (per project — list which in
  `.ai/context.md` → Entry Points).
- Treat the deployed URL as the only "real" environment.
- Rollback path: `git revert` the bad commit; auto-deploy re-runs.

## Verification

The user can't run anything locally. Claude verifies changes by:

1. **CI** — whatever the repo wires up (lint, type-check, tests).
2. **Deploy preview** — fetch the deployed URL, inspect the response.
3. **Manual spot-check** — describe to the user what to tap/look at on
   the live site, in plain language.

If a change is impossible to verify any of those ways, say so explicitly
instead of claiming it works.

## Multi-Chat Workflow

The user maintains separate Claude chats per concern. Concerns vary by
project but commonly include things like:

- App Dev — code changes, features, bugs
- Prompt Refinement — prompt engineering, `.ai/prompts.md` updates
- Docs — README, workflow, architecture
- Ops — deploy config, CI, env vars

When a chat starts, the user names the concern. **Stay in that lane.**
If a task drifts into another concern, surface the drift and ask whether
to switch chats.

## Editing Etiquette (for Claude)

- **Be frugal with comments on GitHub.** Only comment when genuinely
  necessary.
- **Don't open PRs unsolicited.** Push to `main` per the branching rule;
  open a PR only when explicitly asked or when the branch policy required
  a branch.
- **Trim aggressively.** This setup is token-sensitive — short, accurate
  prose beats long, hedged prose.
