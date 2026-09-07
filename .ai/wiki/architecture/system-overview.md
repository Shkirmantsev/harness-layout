---
id: architecture.system-overview
title: System Overview
kind: architecture
status: active
summary: High-level system boundaries, actors and principal runtime responsibilities.
sourceRefs: []
maintenance:
  mode: authored
---

# System Overview

Harness Layout supplies project knowledge retrieval, development workflows, and optional AI infrastructure for a repository.

## Purpose

Keep reusable project knowledge in Markdown and retrieve selected sections through a local MCP server. The portable CLI initializes configuration and runs validation.

## Boundaries

OpenSpec owns agreed and proposed behavior; the Wiki explains the implementation. SQLite is disposable search state. Docker services and remote Hermes are optional integrations.

## Principal components

- `harness.py`: initialization, indexing, installation, and checks.
- `project_context_mcp/core.py`: Markdown parsing, SQLite FTS indexing, retrieval, and validation.
- `project_context_mcp/server.py`: bounded MCP tools over stdio.
- `scripts/configure_clients.py`: Claude, OpenCode, and Codex configuration generation.
- `.agents/skills/`: four harness-owned core procedures, an on-demand catalog,
  and explicitly installed tool-owned workflows such as OpenSpec's Codex skills.

Skill ownership follows the generator boundary: the harness sync owns only its
named core, while integration CLIs own and refresh their generated workflows.
See [ADR: Separate harness core and integration skill ownership](../adr/0001-separate-core-and-integration-skill-ownership.md).

## Runtime flows

Client configuration passes the selected project root explicitly to the MCP server. Agents search for knowledge IDs and retrieve selected sections. Index refresh builds a replacement database before publishing it, preserving the old index when a rebuild fails.

Claude delegates to the remote Hermes MCP sidecar; OpenCode uses native Hermes Runs API tools. Codex has no Hermes transport. The sidecar carries run control, with repository access owned by native Hermes.

## Evidence

- [Management CLI](../../../harness.py)
- [Context core](../../../tools/mcp/project-context-mcp/project_context_mcp/core.py)
- [MCP server](../../../tools/mcp/project-context-mcp/project_context_mcp/server.py)
- [Client generator](../../../scripts/configure_clients.py)
