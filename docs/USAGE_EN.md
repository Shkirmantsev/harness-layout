# Harness Layout v4 — Usage Guide

## What it is

A reusable project-side development harness with a portable core:

- small `AGENTS.md` control plane;
- Markdown-first LLM Wiki;
- OpenSpec change workflow;
- bounded local project-context index/MCP;
- deterministic skill routing and resumable task state;
- Claude Code, Codex and OpenCode adapters;
- optional LiteLLM/local models, Hermes, web research and browser services.

## First use

Portable on Linux/macOS/Windows:

```bash
python harness.py init
python harness.py mcp-install
python harness.py client-config
python harness.py check
```

With GNU Make:

```bash
make init
make mcp-install
make client-config
make check
```

See `docs/QUICKSTART.md` for the detailed path.

## Normal development flow

```text
understand goal
  -> skill-router when non-trivial
  -> kb_search / targeted repository search
  -> selected kb_get + source/spec evidence
  -> OpenSpec change when behavior changes
  -> implementation
  -> focused verification
  -> Wiki/ADR/OpenSpec synchronization
  -> python harness.py check
```

Do not recursively load `.ai/wiki/` or all source/dependency trees into model context.

## Continue work in a new AI session

Agents read `.ai/state/CURRENT.md` at intake. If it describes a non-complete
task, restore its structured checkpoint and validate the recorded working files:

```bash
python3 scripts/session_state.py resume
```

No session ID is needed. Exit code `3` means the working files changed since the
last checkpoint and must be inspected before continuing.

For a new non-trivial task, start state with its outcome and initial steps:

```bash
python3 scripts/session_state.py start \
  --goal "<outcome>" \
  --acceptance "<observable result>" \
  --todo "<next implementation step>" \
  --context "<relevant path>"
```

Use `checkpoint` after every material step and before a final response or
handoff. It atomically updates `.ai/state/handoffs/<id>.json` and regenerates
`.ai/state/CURRENT.md`. The files are visible to Git; commit them with WIP work
when another machine or clone must continue the task.

## OpenCode

The default is production/stable V1 generation:

```dotenv
OPENCODE_CONFIG_GENERATION=v1
```

OpenCode 2 is beta and is an explicit opt-in:

```dotenv
OPENCODE_CONFIG_GENERATION=v2
```

Regenerate after switching. See `docs/OPENCODE_COMPATIBILITY.md`.

## Optional Hermes

The existing v3 native transport design is retained as an optional module:

```text
Claude Code -> dedicated remote Hermes MCP sidecar -> native Hermes /v1/runs
OpenCode    -> project-local hermes_* tools        -> native Hermes /v1/runs
Codex       -> no Hermes transport by default
```

Enable only when needed and follow `docs/HERMES_NATIVE_SETUP.md`.

## Optional local/web stack

Enable in `.env`, then on a Make-capable host:

```bash
make plan
make up
make verify
```

- LiteLLM: optional model gateway
- SearXNG: search discovery
- Crawl4AI: crawl/render/extract
- Playwright MCP: interactive browser/UI work

## Cleanup

```bash
python harness.py clean
```

This removes generated client/runtime/index state while preserving source and `.env`.
