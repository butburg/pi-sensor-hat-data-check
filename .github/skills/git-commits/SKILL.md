---
name: git-commits
description: 'Writing commit messages in this repo. Use whenever committing changes, e.g. new/updated skills or docs.'
---

# Commit messages

Format: `<type>(<scope>): <description>` — imperative, lowercase, no trailing period, ≤72 chars.
Scope = skill/dir touched (e.g. `pi`, `ha`, `chart`, `skills`); omit if repo-wide.

Types: `feat` (new feature/skill), `fix` (bug or wrong info), `docs`, `refactor`
(reorganize without behavior change), `chore`.

Body (optional, blank line first): the *why*, not a restatement of the diff — e.g. what was
wrong/missing and how it was discovered. Wrap at ~72 chars.

Breaking/behavior change for existing skill users → `!` after type, e.g. `fix!:`.

```
fix(pi): write merged json atomically

http.server sometimes served a half-written two_week_merge.json,
causing ValueError in visualize_sensors.py and unavailable in HA.
```

## Rules

- One logical change per commit — don't bundle unrelated skill edits.
- Never invent a scope/type that doesn't fit; drop the scope rather than force one.
- Never commit on your own initiative. Draft the message, show it, and wait for the user to say
  "commit"/"yes" — or for them to tell you to hold off. Applies even after a multi-step task
  that clearly ends in a commit.

## Docs

https://www.conventionalcommits.org/en/v1.0.0/
