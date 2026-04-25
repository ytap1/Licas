# Architecture: {{PROJECT_NAME}}

How the pieces fit together. Keep in sync with the code — stale
architecture docs are worse than none.

## Directory Structure

Fill this in once the stack is picked. Skeleton:

```
{{PROJECT_NAME}}/
├── CLAUDE.md                 # Claude Code reads this first
├── .ai/                      # AI-first context
│   ├── context.md
│   ├── conventions.md
│   ├── decisions.md
│   ├── prompts.md
│   └── metrics.md
├── docs/
│   ├── workflow.md           # how work happens (no terminal)
│   └── architecture.md       # this file
├── <source files>            # depends on stack
├── <tests, if any>
├── <deploy config>           # netlify.toml / .github/workflows/pages.yml / etc.
├── .gitignore
├── CHANGELOG.md
└── README.md
```

When a top-level directory is added, update this tree in the same commit.

## Data Flow

Describe the one path a typical request/interaction takes through the
system. Keep it small enough to read at a glance.

```
<fill in once the stack and shape are decided>
```

## Key Design Principles

1. **Small core, thin edges.** Each layer should be boring.
2. **Explicit over implicit.** No magic; a reader should be able to trace
   behavior with grep.
3. **Make the right thing easy.** If a convention is constantly being
   violated, fix the tooling, not the people.
4. **Irreversible decisions get an ADR.** See `.ai/decisions.md`.
5. **Types at the boundaries.** Public functions, handlers, data models.
6. **Tests describe behavior, not implementation.**
7. **Delete aggressively.** Dead code is a tax on every reader.

## External Dependencies

Every outbound call the app makes. Each one is a failure mode. Fill in
when there is anything to list.

| Dependency | Purpose | Timeout | Retry? | Failure mode |
|------------|---------|---------|--------|--------------|
| <name>     | <why>   | <ms>    | <y/n>  | <behavior>   |

Rules:

- **Every outbound call has a timeout.** No exceptions.
- **Idempotent retries only.** If it isn't idempotent, don't retry.
- **Degrade gracefully** when a non-critical dep is down.

## Verification

The user has no terminal. Verification happens in two places:

- **CI** — whatever checks the project wires up (lint, type-check, tests).
- **Deploy preview** — the auto-deployed site after push to `main`.

Tests that need a localhost don't fit this model. Prefer:

- Unit tests that run in CI.
- Smoke checks against the deployed URL.
- Manual spot-checks the user can do in Safari.
