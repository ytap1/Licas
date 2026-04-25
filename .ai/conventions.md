# Conventions: {{PROJECT_NAME}}

Rules Claude must follow when writing code in this repo. When a rule
conflicts with a framework default, the rule wins — log the exception
in `.ai/decisions.md`.

## File Naming

- Match the language norm (`snake_case.py`, `kebab-case.ts`, etc.).
- Test files mirror source paths (`foo.py` → `test_foo.py` / `foo.test.ts`).
- One public export per file when practical.
- No "utils" / "helpers" / "common" / "misc" modules.
- Scripts go in `scripts/`, named by verb.

## Code Style

- **Naming:** functions/vars in language-idiomatic case; `PascalCase` types;
  `UPPER_SNAKE_CASE` constants; booleans read as predicates (`is_active`).
- **Types at boundaries** (public functions, HTTP handlers, data models).
  Inference inside functions is fine.
- **Errors are values, not control flow.** Raise/throw for truly exceptional
  states; return a `Result`/tuple for expected failures.
- **No single-letter names** except loop indices and standard math.
- **Imports:** stdlib, third-party, local — three groups, alphabetized.

## Architecture

- Pure functions where possible; push I/O, time, randomness to the edges.
- Dependency injection via arguments; no global singletons except config + logger.
- Project-specific layering (if any) belongs in `.ai/context.md`, not here.

## Forbidden

Do not do these without first updating `.ai/decisions.md`.

- `TODO` / `FIXME` without a linked issue.
- `print()` / `console.log()` in checked-in code — use the logger.
- Catching bare `Exception` / `catch (e)` without re-raising or handling
  a specific type.
- Adding a new top-level dependency.
- Disabling a test silently. Fix it or delete it.
- Committing generated files (other than lockfiles).
- Committing secrets. Use the project's env var mechanism.
- CLI instructions in docs (the user has no terminal — see `.ai/context.md`
  → Working Model).

## When Adding New Code

1. **Belongs in an existing module?** Prefer extending over creating.
2. **Has a test (where the project has tests)?** New logic needs one that
   would fail without the change.
3. **Types / schemas updated?**
4. **Docs updated?** If public-facing behavior changed: `README.md`,
   `.ai/context.md`, or `docs/`.
5. **Verifiable on the deploy preview?** The user can't run anything
   locally — if the change isn't observable on the deployed site or via
   CI, say so explicitly.
6. **Diff minimal?** No drive-by renames, no unrelated formatting.
7. **Removed what you replaced?** No dead code, no commented-out blocks.
