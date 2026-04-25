# Architecture: LIKAS

How the pieces fit together. Keep in sync with the code — stale
architecture docs are worse than none.

## Directory Structure

```
LIKAS/
├── CLAUDE.md
├── .ai/
│   ├── context.md
│   ├── conventions.md
│   ├── decisions.md
│   ├── prompts.md
│   └── metrics.md
├── .streamlit/
│   └── secrets.toml          # never committed; set in dashboard
├── docs/
│   ├── workflow.md
│   └── architecture.md
├── app.py                    # Streamlit entry point (not yet created)
├── requirements.txt          # not yet created
├── .gitignore
├── CHANGELOG.md
└── README.md
```

When a top-level directory is added, update this tree in the same commit.

## Data Flow

```
User (Safari) → Streamlit UI (app.py)
             → Google AI Studio API (Gemma 4)
             ← bilingual AI response (Filipino + English)
             → Streamlit renders alert + route recommendation
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

| Dependency          | Purpose                                            | Timeout  | Retry?              | Failure mode                          |
|---------------------|----------------------------------------------------|----------|---------------------|---------------------------------------|
| Google AI Studio    | Gemma 4 flood analysis + bilingual alert generation | 30 000 ms | No (user-triggered) | Show error banner; officer retries manually |

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
