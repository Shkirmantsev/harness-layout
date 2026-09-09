# Harness Layout v4.0.0

A reusable, vendor-neutral production development harness for new or existing software projects. The core works with ordinary Python and Git; Claude Code, Codex, OpenCode, OpenSpec, local models, LiteLLM, Hermes, web research and browser tooling are optional adapters/modules.

## Core design

Start with the [documentation map](docs/README.md) for setup, operations, conventions,
and historical references. The [project structure](docs/PROJECT_STRUCTURE.md) explains
ownership and dependencies; the [Wiki index](.ai/wiki/INDEX.md) retrieves current
project knowledge. Apply the [engineering conventions](docs/conventions/README.md)
relevant to each task.

```text
small AGENTS.md
      |
      v
Markdown LLM Wiki (.ai/wiki) -------- OpenSpec (behavior/change)
      |                                      |
      +------------ project context ---------+
                       |
              local SQLite FTS index
              tmp/local/project-context
                       |
                 project-context MCP
                       |
          Claude / Codex / OpenCode / others
```

Principles:

- **Persist broadly; inject narrowly.** Do not preload the repository/Wiki.
- **Markdown is canonical knowledge.** SQLite/JSON indexes are generated/disposable navigation data.
- **OpenSpec and Wiki have different jobs.** OpenSpec owns normative behavior/change; Wiki explains the current system.
- **Search first, retrieve second.** `kb_search` returns compact cards; `kb_get` expands selected knowledge.
- **Deterministic evidence beats LLM guessing.** Source/build/symbol/dependency tools stay first-class.
- **Portable core, optional infrastructure.** The project is useful without Docker, Hermes, LiteLLM, local models or web services.

## Requirements

Core:

- Python 3.11+
- Git (recommended)

Optional:

- OpenSpec CLI for full OpenSpec schema/workflow validation
- Claude Code, Codex and/or OpenCode
- Docker only if using LiteLLM/SearXNG/Crawl4AI/Playwright stack
- Hermes/Tailscale only if enabling remote Hermes

## Fastest start

### Linux / macOS / WSL

```bash
cp -R harness-layout my-project
cd my-project
make init
make mcp-install       # install local project-context MCP
make client-config
make check
```

### Windows PowerShell

```powershell
Copy-Item -Recurse harness-layout my-project
Set-Location my-project
python .\harness.py init
python .\harness.py mcp-install
python .\harness.py client-config
python .\harness.py check
```

`init` creates `.env`, builds the initial local Wiki index and generates client
configuration. When OpenSpec is installed, it also disables OpenSpec telemetry
in the user's global OpenSpec configuration; without OpenSpec, initialization
continues normally. Edit `.env` only when you want optional integrations or
different client behavior.

## Existing project adoption

Copy the harness files into the repository root, keeping your product code. Then:

```bash
python harness.py init
python harness.py mcp-install
python harness.py check
```

Start by editing only these knowledge files:

- `.ai/wiki/architecture/system-overview.md`
- `.ai/wiki/project/project-map.md`
- `.ai/wiki/glossary/domain.md`

Do **not** attempt to document an entire large brownfield codebase at once. Add Wiki/OpenSpec knowledge around real work and high-value architecture/domain areas.

## Daily commands

| Command | Purpose |
|---|---|
| `python harness.py init` | first-time/safe re-init; disables installed OpenSpec telemetry |
| `python harness.py mcp-install` | create local MCP venv under `tmp/local/` |
| `python harness.py client-config` | regenerate Claude/OpenCode/Codex adapters from `.env` |
| `python harness.py index` | rebuild local Markdown Wiki SQLite FTS index |
| `python harness.py wiki-validate` | check Wiki IDs and links |
| `python harness.py openspec-check` | validate schema and all specs/changes strictly |
| `python harness.py test` | run core tests |
| `python harness.py check` | operator gate: config + Wiki + strict OpenSpec + tests + manifest |
| `python harness.py check-delegated` | secret-free CI/restricted-worker gate |
| `python harness.py manifest-check` | verify the deterministic source manifest |
| `python harness.py clean` | remove generated client/index/runtime state, keep source and `.env` |

Equivalent Make targets exist on systems with GNU Make.

## OpenCode V1 and V2

OpenCode 2 is currently beta. Therefore the harness defaults to the production/stable **V1-generation** configuration:

```dotenv
OPENCODE_CONFIG_GENERATION=v1
```

This produces V1 fields such as:

```text
provider
permission
mcp.<server>
```

If you intentionally install/run the `opencode2` beta, opt in:

```dotenv
OPENCODE_CONFIG_GENERATION=v2
```

then regenerate:

```bash
python harness.py client-config
```

The same `opencode.json` path is regenerated using native V2 structures:

```text
providers
permissions[]
mcp.servers.<server>
```

Do not hand-merge V1 and V2 schema into one configuration. Switch the generation and regenerate instead.

## LLM Wiki workflow

Canonical durable knowledge:

```text
.ai/wiki/**/*.md
```

Generated search state:

```text
tmp/local/project-context/knowledge.db
tmp/local/project-context/state.json
```

Typical agent flow:

```text
AGENTS.md -> kb_search -> selected kb_get -> source/spec -> change -> tests -> Wiki/OpenSpec update -> check
```

## Resumable task workflow

Every non-trivial task has durable structured state in
`.ai/state/handoffs/<session-id>.json`. `scripts/session_state.py` regenerates
`.ai/state/CURRENT.md` whenever a task starts, advances, or resumes.

```bash
# New task
python3 scripts/session_state.py start \
  --goal "Implement the feature" \
  --acceptance "focused tests pass" \
  --todo "inspect the affected module"

# Material step / verification / handoff (current ID is discovered automatically)
python3 scripts/session_state.py checkpoint \
  --status executing \
  --done "inspection complete" \
  --todo "implement the change" \
  --next-action "edit the responsible module"

# Fresh empty-dialog session
python3 scripts/session_state.py resume
```

Commit the handoff files with work-in-progress changes when another machine or
clone must resume them. Do not store secrets, raw chats, or hidden reasoning in
task state.

## OpenSpec workflow

For a non-trivial behavioral change:

```text
proposal -> specs -> design -> context-impact -> tasks -> implementation -> tests -> Wiki update -> verify/archive
```

Current agreed behavior belongs in `openspec/specs/`. Proposed future behavior stays in `openspec/changes/<id>/` until the workflow adopts/archives it.

## Skills

Shared canonical skills live under `.agents/skills/`. Only the compact router/safety/checkpoint/verification core should be directly discoverable; optional procedures are under `.agents/skills/catalog/` and loaded on demand.

Important generic v4 skills include:

- `llm-wiki-maintenance`
- `openspec-change`
- `project-exploration`
- `architecture-design`
- `systematic-debugging`
- `test-driven-development`
- `safe-refactor`
- `code-reviewer`
- `verification-before-completion`
- `web-research-routing`

## Optional runtime services

All are disabled by default in v4. Enable only what a project needs in `.env`:

- LiteLLM/local model routes
- remote Hermes Agent
- SearXNG
- Crawl4AI
- Playwright MCP

Then use `make plan`, `make up`, `make status`, `make verify` where applicable.

## Security and repository hygiene

Never commit:

- `.env`
- `.generated/`
- `tmp/local/**`
- generated `opencode.json`, `.mcp.json`, `.codex/config.toml`
- client local settings containing tokens
- API keys, private SSH material, local auth stores
- `.git/`, IDE caches, `node_modules/`, build outputs inside a distributed template artifact

See `docs/SECURITY.md` and `docs/migration/UPGRADE_TO_V4.md`.
