# Metrics: {{PROJECT_NAME}}

Track AI-assisted work so later you can tell what actually helped.
Add a row per meaningful session ("meaningful" = code shipped, not
"asked a quick question").

## Columns

- **Date:** YYYY-MM-DD the session ended.
- **Feature:** short tag. Match a commit/PR/ADR when possible.
- **Sessions:** distinct chats it took to finish.
- **Tokens:** approximate, from the provider dashboard.
- **Bugs Found:** discovered during/because of the session.
- **Notes:** one line. What worked, what didn't, what to try next.

## Log

| Date             | Feature                  | Sessions | Tokens | Bugs Found | Notes                                |
|------------------|--------------------------|----------|--------|------------|--------------------------------------|
| {{CURRENT_DATE}} | repo scaffolding (.ai/*) | 1        | ~12k   | 0          | Initial template. No app code yet.   |

## Rollups (update weekly)

- **This week's sessions:** <n>
- **Avg sessions per feature:** <n>
- **Features shipped with zero follow-up bugs:** <n>
- **Biggest time sink:** <one line>

## Prompts Worth Saving

When a prompt works unusually well, lift it into `.ai/prompts.md`.
When one fails repeatedly, note it here so future-you doesn't repeat it.
