# Proposal

## Why

The structured session checkpoint was stored only under ignored local runtime
state, while `.ai/state/CURRENT.md` was maintained manually. A new AI session
could therefore start with stale or empty task context even when implementation
was in progress.

## Goal

Make task handoff state durable, automatically render the current human-readable
handoff at every lifecycle update, and let a fresh session resume the active task
without knowing its session ID.

## Affected capabilities

- Session checkpoint persistence and discovery.
- Agent task-intake and handoff workflow.
- Documentation of operational state ownership.

## Compatibility / migration impact

Existing checkpoints under `tmp/local/sessions/` remain readable and are
promoted to the durable store when resumed or updated. The JSON schema version
remains compatible.

## Related knowledge

- `kb://architecture.system-overview`
- `kb://project.project-map`
- `kb://project.task-handoff`
