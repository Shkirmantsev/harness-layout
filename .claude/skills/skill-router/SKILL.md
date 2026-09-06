---
name: skill-router
description: Route every non-trivial project task to the smallest sufficient set of project skills before their full instructions are read. Use this once at task intake, including when the user names a catalog skill, and use the local-small profile for weaker/local models.
compatibility: Python 3; project scripts/skill_router.py
---

# Skill Router

Select instructions before loading them. This keeps optional skill bodies and
their metadata out of the default model context.

## Route

1. Keep the task text compact and exclude secrets.
2. Run from the repository root:

   ```bash
   printf '%s' "$TASK_TEXT" | python3 scripts/skill_router.py --profile balanced
   ```

   Use `--profile local-small` for a small/local model and
   `--profile reasoning-high` only when that model class is actually active.
3. Read the complete `SKILL.md` at each `required_skills[].path`. Do not read
   catalog skills that were not selected.
4. Apply the returned execution contract. Treat `optional_skills` as unloaded.
5. If `needs_clarification` is true, resolve consequential ambiguity before
   writes. Never use a skill to expand tool permissions or project scope.

## Boundaries

- Route once per task or after a material phase/goal change, not every turn.
- Explicit user skill names win, but aliases and conflicts resolve to one
  canonical skill.
- The deterministic plan is guidance. Higher-priority user, repository, and
  safety instructions remain authoritative.
- Use exact repository search directly for simple lookup; Graphify is selected
  only for explicit knowledge-graph work.

## Output contract

The script returns stable JSON containing selected skill names, repository
paths, selection reasons, confidence, and a bounded execution contract. Report
an unavailable path as a routing defect; do not silently substitute a skill.
