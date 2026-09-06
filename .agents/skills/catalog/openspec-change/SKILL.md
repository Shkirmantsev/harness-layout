---
name: openspec-change
description: Drive a non-trivial behavioral change with OpenSpec while keeping current specs, proposed deltas, implementation, and project Wiki temporally distinct.
---

# OpenSpec change

1. Identify current behavior from `openspec/specs/`, implementation, and relevant Wiki pages.
2. Create/use one bounded change under `openspec/changes/<id>/`.
3. Produce proposal, behavioral specs, design, context-impact, and tasks in dependency order.
4. Requirements describe observable behavior; design contains implementation detail.
5. Mark proposed behavior as future until shipped/verified/archived.
6. Include focused tests and Wiki/ADR maintenance in tasks.
7. Run `python harness.py openspec-check`; run the installed OpenSpec CLI validator when available.
8. Report spec/implementation mismatches instead of hiding them.
