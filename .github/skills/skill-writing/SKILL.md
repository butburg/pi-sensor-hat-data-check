---
name: skill-writing
description: 'Rules for creating, editing, or tightening skills in this repo. Use whenever writing a new skill, changing an existing one, or asked to shorten/optimize skills.'
---

# Writing skills

Audience = machine, not human. Goal = max information per token. Standalone (no dependency).

## Format

- Path `.github/skills/NAME/SKILL.md`; frontmatter `name` + one-sentence `description` (single-quoted; = load trigger, always in context, so keep short: what + when).
- Target <40 lines. Split by task, not by topic size; each skill loads independently.
- Register in AGENTS.md skills list (name — purpose (requires X)), in dependency/load order. Names only, no paths/links.

## Keep (gold)

Exact paths, container/service names, commands, ports, non-obvious rules, gotchas as `symptom → cause → fix`, ordering constraints, "ask user before X" rules, what lives where (local pi/ vs Pi vs HA).

## Cut

- Generic knowledge the model already has, defaults, tutorials, intros, "what is X" beyond one line.
- Anything stated in another skill → `Requires X first` instead of restating.
- Repeated facts: say once, in the most specific skill.
- Markdown links between skills (use names), duplicate URLs, politeness/filler.
- Full dir trees/tables of contents → give entry points (`/data/x/`), agent explores with `ls`/`grep`.

## Style

- Fragments over sentences; `key = value`, `A → B`, inline code, one-line YAML `{a: 1, b: 2}` when it fits.
- Docs: one base URL + list of path suffixes, only pages worth reading.
- Secrets/tokens never in skills.
- Learned something new the hard way (failed command, wrong assumption)? Add it as a gotcha line right away.

## Tightening existing skill

1. List every fact; 2. delete dupes/generic; 3. fold links→names, trees→entry points, lists→one block; 4. re-check no fact lost (esp. paths, names, gotchas); 5. tell user what changed.
