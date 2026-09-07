---
id: project.map
title: Project Map
kind: project
status: active
summary: Repository navigation map for modules, source roots, build/test entry points and important files.
sourceRefs: []
maintenance:
  mode: hybrid
---

# Project Map

## Main source areas

- [scripts](../../../scripts/): environment, client generation, skill routing, and optional service operations.
- [project-context MCP](../../../tools/mcp/project-context-mcp/): Wiki retrieval server and indexer.
- [infra](../../../infra/): optional local Compose services.
- [remote sidecar](../../../remote/hermes-worker-mcp/): Claude's remote Hermes control adapter.
- [OpenSpec](../../../openspec/): current specifications, proposed changes, and production-SDD templates.
- [AI task handoffs](task-handoff.md): durable active-task context and empty-dialog resume lifecycle.

## Build and test entry points

- `python3 harness.py init`: initialize environment, index, skills, and clients.
- `python3 harness.py mcp-install`: install the project-local MCP environment.
- `python3 harness.py client-config`: regenerate client adapters after configuration changes.
- `python3 harness.py index`: rebuild the Wiki index after Markdown changes.
- `python3 harness.py check`: configuration, Wiki, OpenSpec structure, and regression tests; includes stdio MCP tests when installed.
- `python3 scripts/session_state.py resume`: discover the current task and validate its working-set hashes.
- `make verify`: health checks for enabled optional services; remote inference is opt-in.

## Important configuration

[.env.example](../../../.env.example) documents supported local configuration; `.env` contains private machine settings. [Makefile](../../../Makefile) wraps the CLI and optional service commands. Canonical skills live under `.agents/skills/`.

## Generated/runtime directories

Generated local context/index data and session locks belong under `tmp/local/`
and must not become canonical knowledge. Durable operational task state belongs
under `.ai/state/`; it is separate from the project Wiki and OpenSpec.
