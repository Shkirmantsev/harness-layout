# Adopt downstream harness improvements

## Why

A downstream repository, a private downstream repository, evolved the reusable harness.
Port useful changes back without introducing its business code, build contracts,
application schemas, deployment configuration, or domain documentation.

## What changes

- Make atomic context, lesson and session writes portable on Windows.
- Preserve literal backslashes when replacing environment values.
- Provide unloaded catalog metadata when deterministic routing is uncertain.
- Add a bounded, on-demand Ponytail simplicity skill.
- Mirror the four core skills into project-local Claude and OpenCode discovery
  directories while preserving integration-owned skills and Codex's canonical
  `.agents/skills/` discovery location.
- Add optional authenticated Context7 HTTP configuration for all three clients.
- Resolve executable launchers before subprocess invocation for platform portability.

## Capabilities

### New capabilities

- `portable-harness-tooling`: portable writes, semantic routing fallback,
  minimal-implementation skill and optional hosted documentation MCP.

### Modified capabilities

- `skill-integration`: local core synchronization also targets OpenCode.

## Impact

Python harness scripts, one optional catalog skill, client configuration,
`.env.example`, tests, and harness documentation. Existing Hermes, LiteLLM,
web integrations, JSON schemas and Wiki/MCP implementation are retained.
No global skill directories or source project files are modified.

Normalize the existing session-handoff specification into the standard capability
directory so the strict CLI validates it; reject future loose specs.
