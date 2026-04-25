# Decisions: {{PROJECT_NAME}}

Append-only log of architectural and technical decisions. Each entry
answers: what did we pick, what did we reject, and why?

- **Never rewrite history.** Reversed decisions get a new entry that
  supersedes the old one. Cross-link them.
- **Keep entries short.** Link out if it needs more than a page.
- **Number sequentially** (ADR-0001, ADR-0002, ...).

## Template

```markdown
## ADR-NNNN: <short title>

- **Date:** YYYY-MM-DD
- **Status:** Proposed | Accepted | Superseded by ADR-XXXX | Deprecated

### Context
<problem and forces, 2–5 sentences>

### Decision
<the choice, 1–2 sentences>

### Alternatives Considered
- **Option A:** why rejected.
- **Option B:** why rejected.

### Consequences
- **Positive:** <what gets easier>
- **Negative:** <what gets harder>
- **Follow-ups:** <what this unlocks or requires next>
```

---

## ADR-0001: Push directly to `main`; branch only for destructive changes

- **Date:** {{CURRENT_DATE}}
- **Status:** Accepted

### Context

Solo developer working from iPad/Safari + Claude Code. PR review overhead
adds friction with no second reviewer. Most changes are small and
incremental. Auto-deploy on push to `main` is the desired feedback loop.

### Decision

Push directly to `main` for routine changes. Create a branch only when
the change is destructive or high-risk: schema rewrites, mass renames,
deletions, anything that could break the deployed site without an easy
rollback.

### Alternatives Considered

- **PR-per-change:** standard team practice, but no second reviewer here
  and it slows the iPad/web workflow.
- **Trunk-based with feature flags:** future option once the project has
  enough surface area to need it.

### Consequences

- **Positive:** fastest possible iteration; one source of truth; deploy
  preview = production preview.
- **Negative:** no review gate before deploy. Mitigation: Claude Code
  runs CI checks; `git revert` is the rollback path.
- **Follow-ups:** if a class of bug starts shipping to `main`, add a CI
  check that would have caught it.
