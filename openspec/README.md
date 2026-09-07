# OpenSpec workflow

[Documentation map](../docs/README.md) · [Engineering conventions](../docs/conventions/README.md)

[config.yaml](config.yaml) selects [production-sdd](schemas/production-sdd/schema.yaml).
The schema names templates and their prerequisites:

| Artifact | Template | Requires |
|---|---|---|
| proposal | [proposal.md](schemas/production-sdd/templates/proposal.md) | none |
| specs | [spec.md](schemas/production-sdd/templates/spec.md) | proposal |
| design | [design.md](schemas/production-sdd/templates/design.md) | proposal, specs |
| context-impact | [context-impact.md](schemas/production-sdd/templates/context-impact.md) | proposal, specs, design |
| tasks | [tasks.md](schemas/production-sdd/templates/tasks.md) | specs, design, context-impact |

Create a bounded change under `changes/<id>/` using these artifacts. Implementation
follows tasks, with verification and affected Wiki updates before adoption/archive.
See the [OpenSpec skill](../.agents/skills/catalog/openspec-change/SKILL.md).

`specs/` contains adopted requirements; `changes/` contains proposed deltas.
Empty directories indicate no requirements or active changes have been authored.
The Wiki explains current implementation without promoting proposals into facts.

## Current capabilities

- [Session handoff](specs/session-handoff.md): durable active-task state and
  empty-dialog resume behavior.

Completed change evidence is retained under `changes/archive/`; for example,
[automatic session handoff](changes/archive/2026-09-07-automatic-session-handoff/proposal.md).

Run `python harness.py openspec-check`. Its built-in structural check is limited;
full schema validation runs only when the OpenSpec CLI is installed.
