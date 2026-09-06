# Harness Layout Native v3 — Architecture and Usage Guide

## 1. What this framework is

`harness-layout` is a reusable project-side harness for running coding agents against one repository while keeping model routing, optional web tooling, and a remote Hermes worker explicit and separable.

The simplified architecture intentionally has no Firecrawl platform, no project bridge, no binding database, no attachment relay, no project SSH container, and no second Hermes runtime.

The main client split is deliberate:

```text
MAIN PC / WORKING REPOSITORY                      REMOTE HERMES HOST

Claude Code
  └─ generated hermes-worker subagent
       └─ MCP over Tailscale :8775
            └─ small Hermes control sidecar
                 └─ native Hermes /v1/runs on localhost:8642

OpenCode (normal main model, e.g. MiniMax)
  └─ project-local `hermes_*` custom tools
       └─ native Hermes `/v1/runs` API over Tailscale :8642

Hermes Agent
  └─ native SSH backend over Tailscale/SSH
       └─ dedicated unprivileged main-PC user `hermes-worker`
            └─ ACL access to PROJECT_ROOT

Local models
  Claude/OpenCode -> LiteLLM -> LM Studio

Optional web/UI tools
  SearXNG -> discovery/search
  Crawl4AI -> crawl/render/extract known URLs
  Playwright MCP -> interactive browser/UI testing
```

OpenCode does **not** need the Claude-specific Hermes MCP sidecar. The sidecar exists because Claude Code benefits from a small MCP control contract. OpenCode instead uses project-local custom tools that call the same native Hermes Runs API (`/v1/runs`) directly. Hermes is intentionally not exposed to OpenCode as a normal model provider/subagent.

## 2. Pinned/required versions in this revision

| Component | Version / policy | Purpose |
|---|---:|---|
| Hermes Agent | `>= 0.20.5` | Native OpenAI API, `/v1/runs`, SSH-backed file/media behavior |
| Hermes Claude MCP sidecar | `1.1.0` | Claude-only Hermes run control |
| MCP Python SDK | `2.1.0` | Streamable HTTP MCP server |
| httpx | `0.28.1` | Sidecar/adapter HTTP client |
| Starlette | `1.6.0` | MCP HTTP application runtime |
| Uvicorn | `0.52.4` | MCP HTTP server |
| LiteLLM | `1.98.0` | Local model/protocol gateway |
| Crawl4AI | `0.9.2` | Self-hosted crawler/extractor |
| SearXNG | `2026.8.22-9fea41204` | Optional search discovery |
| Playwright MCP | immutable image digest from `.env.example` | Optional UI/browser automation |

A version pin is not a request to upgrade a healthy remote service blindly. In particular, update Hermes only when the installed version is below the minimum required by this harness and only after backing up/regression-checking the existing profile and gateway.

## 3. Repository layout

Important paths:

```text
harness-layout/
├── .env.example                 user configuration template
├── .env                         generated/untracked actual configuration
├── Makefile                     management API for the local harness
├── AGENTS.md                    common project policy
├── opencode.json                generated OpenCode configuration
├── .mcp.json                    generated Claude local web/UI MCP config
├── .agents/skills/              four core skills + routed optional catalog
├── .claude/agents/              generated Claude subagents
├── .opencode/agents/            generated OpenCode agents
├── infra/
│   ├── litellm/                 local model/protocol gateway
│   ├── litellm-edge/            optional Tailscale exposure boundary
│   ├── searxng/                 optional search engine
│   ├── searxng-mcp/             custom thin MCP adapter for SearXNG
│   ├── crawl4ai-http-bridge/    custom Streamable-HTTP compatibility MCP bridge
│   └── compose.yaml
├── remote/hermes-worker-mcp/    source copied to the remote Hermes host
├── scripts/                      bootstrap/config/check/verify helpers
└── docs/                         operator documentation
```

The SearXNG MCP and Crawl4AI HTTP MCP bridge are harness adapters, not official upstream MCP products. Crawl4AI itself remains the actual crawler service; the bridge only gives clients one convenient local Streamable-HTTP MCP endpoint.

## 4. Main-PC prerequisites

Install/prepare:

```bash
python3 --version
docker --version
docker compose version
make --version
tailscale status
```

LM Studio is needed only when local model slots are enabled. Hermes is needed only when `HERMES_ENABLED=true`.

The working repository must be a real, specific directory. Do not use `/`, an entire home directory, or another broad parent as `PROJECT_ROOT`.

## 5. First startup

From the harness root:

```bash
make init
```

This creates/synchronizes `.env`, generates local secrets marked `AUTO_GENERATE`, synchronizes local skills, and generates client configuration.

Edit `.env` next. At minimum review:

```dotenv
PROJECT_ROOT=/absolute/path/to/current/repository
HARNESS_PROJECT_ID=my-project

LITELLM_ENABLED=true
CLAUDE_CODE_USE_LITELLM=false

# Optional remote Hermes
HERMES_ENABLED=false

# Optional web/UI stack
WEB_SEARCH_ENABLED=false
CRAWL4AI_ENABLED=false
PLAYWRIGHT_ENABLED=false
```

Then run:

```bash
make check
make plan
make up
make verify
```

`make plan` is useful before `make up`: it shows which optional Compose profiles are actually enabled.

## 6. Local LM Studio models through LiteLLM

The harness supports four configurable local slots. A slot has a normal OpenAI alias and a Claude-facing alias, for example:

```dotenv
LOCAL_MODEL_1_ENABLED=true
LOCAL_MODEL_1_ALIAS=gemma
LOCAL_MODEL_1_CLAUDE_ALIAS=claude-gemma
LOCAL_MODEL_1_MODEL_ID=google/gemma-4-26b-a4b-qat
LOCAL_MODEL_1_REASONING_MODE=system-guidance
LOCAL_MODEL_1_MAX_OUTPUT_TOKENS=4096
```

LiteLLM talks to LM Studio through:

```dotenv
LM_STUDIO_OPENAI_BASE_URL=http://127.0.0.1:1234/v1
```

`LOCAL_MODEL_N_REASONING_MODE` is **not an effort level**. It selects how the harness translates a client's effort request:

```text
off                    do not add reasoning behavior
system-guidance        translate effort into a short system instruction
native                 set LM Studio chat_template_kwargs.enable_thinking
native+system-guidance do both
```

The actual effort remains separate (`none`, `minimal`, `low`, `medium`, `high`, `xhigh`, etc.). Use `native` only if that exact local model/template supports `enable_thinking` correctly.

The default local output cap is 4096 tokens in this revision; the previous 512-token cap was too small for normal coding/tool-oriented responses.

## 7. Optional direct MiniMax route

MiniMax is independent of Hermes. When enabled, LiteLLM routes directly to MiniMax using the user's Token Plan credential:

```text
Claude/OpenCode -> LiteLLM -> MiniMax API
```

Relevant settings:

```dotenv
MINIMAX_ENABLED=true
MINIMAX_MODEL_ID=MiniMax-M3
MINIMAX_ANTHROPIC_BASE_URL=https://api.minimax.io/anthropic
MINIMAX_TOKEN_PLAN_KEY=sk-cp-...
MINIMAX_ALWAYS_ADAPTIVE=true
```

The harness forces MiniMax M3 adaptive thinking for this route. It does not route MiniMax through Hermes.

## 8. Enabling remote Hermes

On the main machine set:

```dotenv
HERMES_ENABLED=true
PROJECT_ROOT=/absolute/path/to/repository
HERMES_REMOTE_HOST=<remote-hermes-tailnet-dns-name>
HERMES_REMOTE_OPENAI_PORT=8642
HERMES_REMOTE_API_KEY=<existing Hermes API_SERVER_KEY>
HERMES_REMOTE_MODEL=hermes-tailscale-worker
HERMES_REMOTE_SIDECAR_PORT=8775
HERMES_SIDECAR_TOKEN=<token created by remote sidecar>
MAIN_TAILSCALE_HOST=<main-machine-tailnet-dns-name>
HERMES_PROJECT_USER=hermes-worker
```

Prepare the main-PC account/ACL once:

```bash
make hermes-host-setup ENABLE_TAILSCALE_SSH=1
```

This creates/reuses an unprivileged `hermes-worker` Linux account and grants it ACL access to the configured project. It must not be a member of sudo/docker/admin-style groups.

Generate a concrete remote runbook:

```bash
make hermes-remote-instructions
```

Or use the supplied generic `03-HERMES_TAILSCALE_WORKER_FINALIZE_v3_NATIVE.md`.

Copy the sidecar source to the remote host without secrets:

```bash
make hermes-sidecar-copy
```

After the remote setup is completed, regenerate clients and verify:

```bash
make client-config
make hermes-check
```

## 9. How Claude Code uses Hermes

Claude Code receives a generated project subagent named `hermes-worker`.

The main Claude process does not treat the sidecar as a filesystem MCP. The generated subagent can call only the Hermes run-control tools:

```text
hermes_run
hermes_status
hermes_wait
hermes_result
hermes_steer
hermes_approve
hermes_cancel
```

Flow:

```text
Claude main
 -> hermes-worker dispatcher (small Claude model)
 -> remote MCP sidecar :8775
 -> native Hermes /v1/runs on the remote machine
 -> Hermes own tools
 -> SSH-backed project access on the main machine
```

`hermes_run` receives the real absolute `PROJECT_ROOT` plus the delegated task. It does not upload project files.

A new delegation starts a **fresh Hermes session by default**. The sidecar returns both `run_id` and `session_id`. Reuse the prior `session_id` only when you intentionally want to continue the same Hermes context.

If Hermes enters `waiting_for_approval`, `hermes_wait` returns instead of hanging. The dispatcher must surface that state. `hermes_approve` is called only after explicit authorization; it is never an automatic “approve everything” mechanism.

## 10. How OpenCode uses Hermes

OpenCode deliberately bypasses the Claude MCP sidecar:

```text
OpenCode -> hermes_delegate/status/wait/result/... -> http://REMOTE-HERMES:8642/v1/runs -> native Hermes Agent
```

`make client-config` creates `.opencode/tools/hermes.js` plus a private generated runtime file. The tool calls Hermes `/v1/runs` directly and does not create a Hermes model provider. The remote identity advertised by `/v1/models` is normally:

```text
hermes-tailscale-worker
```

This public name is the Hermes agent/profile identity. It is not necessarily the actual provider model ID behind the worker.

OpenCode has no generated Hermes model/subagent. The normal OpenCode main model (for example MiniMax) calls `hermes_delegate` when it wants an independent Hermes workstream. `hermes_delegate` starts one native run; `hermes_wait`, `hermes_status`, and `hermes_result` continue that run without duplication. `hermes_approve` remains a human-visible approval point.

## 11. Why the Claude sidecar must not send `model=hermes-tailscale-worker` to `/v1/runs`

Hermes' native `/v1/runs` endpoint treats an explicitly supplied `model` as a real per-request model override. Therefore the sidecar omits `model` entirely and lets the `hermes-tailscale-worker` profile choose its configured provider/model.

OpenCode does not use `/v1/chat/completions` for Hermes delegation in revision 3.2. It uses the native Runs API and therefore also omits any per-request model override.

## 12. Crawl4AI and search

Enable Crawl4AI:

```dotenv
CRAWL4AI_ENABLED=true
```

Then:

```bash
make up
make verify
```

The harness runs Crawl4AI `0.9.2` locally and exposes a small compatibility MCP bridge on loopback. Use it for known public URLs, rendered pages and extraction.

If URL discovery/search is also needed:

```dotenv
WEB_SEARCH_ENABLED=true
```

This enables local SearXNG plus the harness's thin SearXNG MCP adapter.

There is no Firecrawl service in this revision.

## 13. Playwright MCP

Enable only when you need browser interaction/UI testing:

```dotenv
PLAYWRIGHT_ENABLED=true
```

Use Playwright for clicks, forms, stateful UI flows and browser verification. Use Crawl4AI for crawl/extraction. They solve different tasks.

## 14. Important Makefile commands

```text
make init                  create/sync .env, local secrets, skills, client configs
make env-sync              add newly introduced .env keys without overwriting values
make runtime               refresh automatic Tailscale identity/client files
make check                 validate configuration and safety invariants
make plan                  show enabled local services
make pull                  pull enabled service images
make build                 build enabled local images
make up                    reconcile/start enabled local stack
make stop                  stop all harness containers
make restart               down + up
make down                  remove all harness containers/network
make status                show all harness containers
make logs ARGS=-f          follow logs
make client-config         regenerate Claude/OpenCode/Codex configs
make verify                health-check enabled services
make verify-models         verify LM Studio/LiteLLM aliases
make test                  local static/unit tests
make hermes-host-setup     create/reuse dedicated main-PC account and project ACL
make hermes-sidecar-copy   copy sidecar source to remote Hermes host
make hermes-remote-instructions generate concrete remote setup runbook
make hermes-check          verify remote Hermes API + sidecar without paid inference
make skills-sync-local     sync canonical project skills to Claude
make skills-sync-remote    sync shared skills to the remote Hermes profile
```

## 15. Recommended validation order

After a new installation or significant configuration change, use this order:

```bash
make init
# edit .env
make check
make test
make plan
make pull
make build
make up
make client-config
make verify
make verify-models
```

For Hermes additionally:

```bash
make hermes-host-setup ENABLE_TAILSCALE_SSH=1
make hermes-sidecar-copy
make hermes-remote-instructions
# execute the generated runbook on the remote Hermes host
make client-config
make hermes-check
```

A real paid/remote inference smoke test should be run deliberately after the free health/config checks pass.

## 16. Security model and limitations

The main project boundary for Hermes is the dedicated Linux account plus POSIX ACLs. This is simpler than a project container and intentionally avoids project bridges. It protects the user's private home/project data that is not granted to `hermes-worker`, but it is not a full OS sandbox: world-readable operating-system files may remain readable by any normal unprivileged Linux user.

Tailscale should be the network boundary for the remote API and sidecar. Do not expose ports 8642 or 8775 to the public Internet.

Do not commit `.env`, `.generated/`, API keys, sidecar tokens or provider credentials.

## 17. Troubleshooting summary

If Claude cannot use Hermes, test the remote sidecar first and then its localhost Hermes upstream. Verify the sidecar `.env` uses `HERMES_API_BASE_URL=http://127.0.0.1:8642` **without `/v1`**.

If OpenCode cannot delegate to Hermes, ignore the Claude sidecar and first test native `/health` and authenticated `/v1/models`; then verify `.opencode/tools/hermes.js` and `.generated/opencode-hermes-runtime.json` were regenerated with `make client-config`.

If Hermes can answer but cannot access the project, test `ssh -o BatchMode=yes hermes-worker@<main-tailnet-host>` from the remote Hermes machine and inspect the main-PC ACLs.

If a Claude delegation waits indefinitely, inspect `hermes_status`. A run may be `waiting_for_approval`; that state must be surfaced and resolved explicitly rather than treated as a timeout.

If local-model replies are truncated, verify the slot's `LOCAL_MODEL_N_MAX_OUTPUT_TOKENS` value and LM Studio's own output/context settings.
