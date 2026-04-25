# CLAUDE.md

Read this first. Then `.ai/context.md`, then `.ai/conventions.md`.

## Working Model (non-negotiable)

- **iPad/iPhone + Safari only.** No terminal, no laptop.
- **No package managers, no localhost, no CLI instructions in docs.**
- **Push directly to `main`** for routine changes. Branch only for
  destructive/high-risk work (schema rewrites, mass renames, deletions).
- **Deploy auto-triggers on push to `main`** (GitHub Pages or Netlify).
  Verify on the deployed URL, never localhost.
- **Multi-chat workflow.** Each chat covers one concern (App Dev, Prompt
  Refinement, Docs, etc.). Stay in the lane named in the current chat.

## Token Discipline

- Short, accurate prose beats long, hedged prose.
- No restating obvious context back to the user.
- No CLI walkthroughs (the user can't run them).
- Trim every doc you touch.

## Read in Order

1. [.ai/context.md](./.ai/context.md) — what this is, current state, stack
2. [.ai/conventions.md](./.ai/conventions.md) — coding rules
3. [.ai/decisions.md](./.ai/decisions.md) — ADRs
4. [docs/workflow.md](./docs/workflow.md) — full working model
5. [docs/architecture.md](./docs/architecture.md) — structure + data flow
6. [.ai/prompts.md](./.ai/prompts.md) — session templates
