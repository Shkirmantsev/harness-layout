# Harness Layout v4.0.0

A reusable, vendor-neutral production development harness for new or existing
software projects. The core works with ordinary Python and Git; Claude Code,
Codex, OpenCode, OpenSpec, local models, LiteLLM, Hermes, web research and
browser tooling are optional adapters/modules.

## When to use this harness

| Scenario | Use it? |
|---|---|
| New project from scratch | Yes |
| Existing codebase that needs an LLM-agent workflow | Yes |
| Single-file script with no team | Too much overhead |
| Project already has its own AGENTS.md and dev flow | Evaluate before adopting |

## Core design

Start with the [documentation map](docs/README.md) for setup, operations,
conventions, and historical references. The [project structure](docs/PROJECT_STRUCTURE.md)
explains ownership and dependencies; the [Wiki index](.ai/wiki/INDEX.md)
retrieves current project knowledge. Apply the
[engineering conventions](docs/conventions/README.md) relevant to each task.

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

- **Persist broadly; inject narrowly.** Do not preload the repository or Wiki.
- **Markdown is canonical knowledge.** SQLite and JSON indexes are disposable.
- **OpenSpec and Wiki have different jobs.** OpenSpec owns normative behavior
  and change; Wiki explains the current system.
- **Search first, retrieve second.** `kb_search` returns compact cards;
  `kb_get` expands selected knowledge.
- **Deterministic evidence beats LLM guessing.** Source, build, symbol, and
  dependency tools stay first-class.
- **Portable core, optional infrastructure.** Useful without Docker, Hermes,
  LiteLLM, local models, or web services.

## Requirements

Core: Python 3.11+ and Git.

Optional: OpenSpec CLI for full schema/workflow validation, Claude Code/Codex/OpenCode,
Docker for LiteLLM/SearXNG/Crawl4AI/Playwright, Hermes and Tailscale for remote Hermes.

## Quick start

### New project (Linux, macOS, WSL)

```bash
cp -R harness-layout my-project
cd my-project
make init
make mcp-install
make client-config
make check
```

### New project (Windows PowerShell)

```powershell
Copy-Item -Recurse harness-layout my-project
Set-Location my-project
python .\harness.py init
python .\harness.py mcp-install
python .\harness.py client-config
python .\harness.py check
```

`init` creates `.env`, builds the initial local Wiki index, and generates
client configuration. When OpenSpec is installed, `init` also disables
OpenSpec telemetry in the user's global config; without OpenSpec, initialization
continues normally. Edit `.env` only when you want optional integrations or
different client behavior.

### Existing project adoption

Copy the harness files into the repository root, keeping your product code:

```bash
python harness.py init
python harness.py mcp-install
python harness.py check
```

Start by editing only these knowledge files:

- `.ai/wiki/architecture/system-overview.md`
- `.ai/wiki/project/project-map.md`
- `.ai/wiki/glossary/domain.md`

Do **not** try to document an entire brownfield codebase at once. Add Wiki and
OpenSpec knowledge around real work and high-value architecture or domain
areas.

## Daily commands

### Core

| Command | Purpose |
|---|---|
| `make init` | first-time setup: `.env` + disable OpenSpec telemetry |
| `make init-mcp` | `init` plus `mcp-install` (first run) |
| `make env-sync` | add new vars from `.env.example` without overwriting values |
| `make runtime` | refresh identities and regenerate client configs |
| `make mcp-install` | create local MCP venv under `tmp/local/` |
| `make client-config` | regenerate Claude, OpenCode, Codex adapters from `.env` |
| `make check` | operator gate: config + Wiki + OpenSpec + tests + manifest |
| `make check-delegated` | secret-free gate for CI / restricted worker |
| `make wiki-index` | rebuild local SQLite FTS index of the Wiki |
| `make wiki-validate` | check Wiki IDs and links |
| `make openspec-check` | strict OpenSpec schema and workflow validation |
| `make manifest-generate` | rebuild `ARTIFACT_MANIFEST.sha256` |
| `make manifest-check` | verify the deterministic source manifest |
| `make test` | run core unit tests |
| `make skills-sync-local` | sync routed skills into `.claude/skills/` |
| `make skills-check` | verify Claude skill exposure and directory isolation |
| `make clean` | remove generated files; keep source and `.env` |

The same targets exist as `python harness.py <command>` for Windows or systems
without GNU Make (subset: `init`, `check`, `check-delegated`, `test`, `index`,
`wiki-validate`, `openspec-check`, `mcp-install`, `client-config`,
`manifest-generate`, `manifest-check`, `clean`).

### Optional integrations

All are disabled in `.env.example`. After editing `.env`, run `make runtime`
to regenerate client configs.

| Command | Purpose |
|---|---|
| `make config` / `plan` / `pull` / `build` | prepare docker-compose for enabled local services |
| `make up` / `start` / `stop` / `restart` / `down` | manage docker-compose stacks |
| `make status` / `ps` / `logs` | inspect containers |
| `make hermes-host-setup` / `hermes-host-revoke` | ACL for the remote Hermes account |
| `make hermes-sidecar-copy` / `hermes-remote-instructions` | deploy remote Hermes |
| `make hermes-check` | smoke test remote Hermes without paid calls |
| `make hermes-import` | stage an external file into `.harness/inbox/` |
| `make verify` / `verify-models` | validate enabled local or LiteLLM models |

## OpenCode V1 and V2

OpenCode 2 is currently beta. The harness defaults to the stable
**V1-generation** configuration:

```dotenv
OPENCODE_CONFIG_GENERATION=v1
```

This produces V1 fields such as `provider`, `permission`, `mcp.<server>`.
If you intentionally install the `opencode2` beta, opt in:

```dotenv
OPENCODE_CONFIG_GENERATION=v2
```

then regenerate:

```bash
python harness.py client-config
```

The same `opencode.json` path is regenerated with native V2 structures:
`providers`, `permissions[]`, `mcp.servers.<server>`. Do not hand-merge V1 and
V2 schema into one configuration; switch the generation and regenerate.

## LLM Wiki workflow

Canonical durable knowledge:

```text
.ai/wiki/**/*.md
```

Generated search state (disposable):

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

# Material step / verification / handoff (current ID is auto-discovered)
python3 scripts/session_state.py checkpoint \
  --status executing \
  --done "inspection complete" \
  --todo "implement the change" \
  --next-action "edit the responsible module"

# Fresh empty-dialog session
python3 scripts/session_state.py resume
```

Commit the handoff files with work-in-progress changes when another machine or
clone must resume them. Do not store secrets, raw chats, or hidden reasoning
in task state.

## OpenSpec workflow

For a non-trivial behavioral change:

```text
proposal -> specs -> design -> context-impact -> tasks -> implementation -> tests -> Wiki update -> verify/archive
```

Current agreed behavior belongs in `openspec/specs/`. Proposed future behavior
stays in `openspec/changes/<id>/` until the workflow adopts or archives it.

## Skills

Canonical shared skills live under `.agents/skills/`. Only the compact
router, safety, checkpoint, and verification core is directly discoverable;
optional procedures are under `.agents/skills/catalog/` and loaded on demand.
Always start a non-trivial task with the `skill-router` skill; it returns the
smallest sufficient skill set for the work.

Key on-demand skills:

- OpenSpec: `openspec-explore`, `openspec-propose`, `openspec-update-change`,
  `openspec-apply-change`, `openspec-sync-specs`, `openspec-archive-change`
- Architecture and quality: `architecture-design`, `code-reviewer`,
  `requesting-code-review`, `verification`
- Implementation: `test-driven-development`, `safe-refactor`, `surgical-patch`,
  `systematic-debugging`
- Workflow: `brainstorming`, `grilling`, `hermes-delegation`, `delegation`,
  `finishing-a-development-branch`

## Repository layout

```text
my-business-app/
├── AGENTS.md                <- LLM control plane (always read)
├── README.md                <- this file
├── .env                     <- secrets / optional integrations (NEVER commit)
├── harness.py               <- CLI (init, check, test, clean, ...)
├── Makefile                 <- thin wrappers around harness.py
│
├── .harness/                <- runtime policy (runtime.json) + inbox/
├── .agents/skills/          <- canonical shared skills
│   ├── skill-router/        <- task router
│   ├── session-checkpoint/  <- task continuity
│   ├── project-safety/      <- secret and boundary protection
│   ├── verification/        <- pre-completion gate
│   ├── openspec-*/          <- OpenSpec workflow skills
│   └── catalog/             <- on-demand skills (architecture, review, ...)
│
├── .opencode/               <- OpenCode adapters
│   ├── agents/, commands/
│   └── skills/              <- openspec-* mirrors
│
├── .claude/skills/          <- synced routed-skill exposure
├── .codex/                  <- generated Codex client config
│
├── .ai/
│   ├── AGENTS.md            <- rules for working with .ai/wiki
│   ├── wiki/                <- canonical Markdown knowledge
│   │   ├── INDEX.md
│   │   ├── architecture/, project/, modules/, interfaces/,
│   │   │   domain/, glossary/, adr/
│   └── state/               <- CURRENT.md + handoffs/*.json (generated)
│
├── .generated/              <- generated credentials / configs (non-normative)
├── tmp/local/               <- local caches, indexes, MCP venv (not committed)
│
├── openspec/
│   ├── config.yaml          <- OpenSpec schema and artifact selection
│   ├── specs/               <- agreed current behavior
│   ├── changes/             <- proposed changes (until archived)
│   └── schemas/production-sdd/
│
├── scripts/                 <- service scripts (bootstrap, sync, session, ...)
├── tools/mcp/project-context-mcp/  <- local MCP server (kb_search, kb_get, ...)
├── schemas/                 <- JSON schemas for artifacts
├── tests/, evals/           <- unit tests and routing evaluations
├── infra/                   <- docker-compose for litellm, searxng, crawl4ai, playwright
├── remote/, third_party/, patches/, docs/, templates/
```

Empty Wiki folders (`adr/`, `domain/`, `interfaces/`, `modules/`) are
extension points, not missing dependencies. See `docs/PROJECT_STRUCTURE.md`
for the full ownership map.

## Optional runtime services

All are disabled by default in v4. Enable only what a project needs in `.env`:

- LiteLLM or local model routes
- Remote Hermes Agent
- SearXNG (web search)
- Crawl4AI (page rendering and extraction)
- Playwright MCP (interactive UI testing)

Then use `make plan`, `make up`, `make status`, `make verify` where applicable.

## Pre-commit checklist

Before your first commit in a new project:

```text
[ ] .env created and NOT added to git (.gitignore covers *.env)
[ ] make check -> PASS
[ ] Project README.md exists (one paragraph: what it is, who uses it, how to run)
[ ] .ai/wiki/architecture/system-overview.md exists (short, < 1 page)
[ ] .ai/wiki/project/project-map.md exists
[ ] .ai/state/CURRENT.md is empty or points to the correct task
[ ] No secrets, tokens, or private keys in the repository
[ ] Git remote is configured; version tags exist (e.g. v0.1.0)
```

## Where to find answers

| Question | File |
|---|---|
| How to start from scratch | `docs/QUICKSTART.md` |
| How to configure `.env` | `docs/CONFIGURATION.md` |
| What a skill does | `.agents/skills/<name>/SKILL.md` or `docs/SKILLS.md` |
| How OpenSpec works | `docs/README.md`, then `openspec/README.md` |
| LiteLLM / Hermes setup | `docs/CONFIGURATION.md`, `docs/HERMES_NATIVE_SETUP.md`, `docs/HERMES_REMOTE_AGENT_INSTRUCTION.md` |
| Coding and commit conventions | `docs/conventions/README.md` |
| Something broke | `docs/TROUBLESHOOTING.md` |
| Security and secrets | `docs/SECURITY.md` |
| Directory layout | `docs/PROJECT_STRUCTURE.md` |
| OpenCode V1 vs V2 | `docs/OPENCODE_COMPATIBILITY.md` |
| Upgrading from a previous version | `docs/migration/UPGRADE_TO_V4.md` |

## Security and repository hygiene

Never commit:

- `.env`
- `.generated/`
- `tmp/local/**`
- generated `opencode.json`, `.mcp.json`, `.codex/config.toml`
- client local settings containing tokens
- API keys, private SSH material, local auth stores
- `.git/`, IDE caches, `node_modules/`, build outputs inside a distributed
  template artifact

See `docs/SECURITY.md` and `docs/migration/UPGRADE_TO_V4.md`.

## One-line summary

Copy `harness-layout` into your project directory, run `make init`,
`make mcp-install`, `make client-config`, `make check`, fill in three Wiki
files, and start tasks through `session_state.py start`, `skill-router`, and
OpenSpec. Run `make check` before declaring any task complete.