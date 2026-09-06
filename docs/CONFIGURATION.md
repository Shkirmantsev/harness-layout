# Configuration

Root `.env` is the normal local configuration file. It is created from `.env.example` by `python harness.py init` and must not be committed.

## Portable/core flags

| Variable | Default | Purpose |
|---|---:|---|
| `PROJECT_CONTEXT_MCP_ENABLED` | true | Generate project-context MCP client entries. Install it with `python harness.py mcp-install`. |
| `OPENCODE_CONFIG_GENERATION` | v1 | `v1` = stable/production OpenCode generation; `v2` = OpenCode 2 beta native generation. |

## Optional runtime flags

| Variable | Default | Purpose |
|---|---:|---|
| `LITELLM_ENABLED` | false | Optional local model/protocol gateway. |
| `HERMES_ENABLED` | false | Optional external Hermes delegation/verification; no local Hermes container. |
| `WEB_SEARCH_ENABLED` | false | Optional SearXNG discovery/search. |
| `CRAWL4AI_ENABLED` | false | Optional Crawl4AI render/extract service. |
| `PLAYWRIGHT_ENABLED` | false | Optional interactive browser MCP. |
| `LITELLM_EXPOSE_ON_TAILSCALE` | false | Optional Tailscale exposure for LiteLLM. |

The default v4 core therefore works without Docker, LiteLLM, Hermes, local models or web services.

## OpenCode generation

Keep:

```dotenv
OPENCODE_CONFIG_GENERATION=v1
```

for normal OpenCode V1 work. Use `v2` only when intentionally testing/running `opencode2` beta. Always regenerate with:

```bash
python harness.py client-config
```

See `docs/OPENCODE_COMPATIBILITY.md`.

## Project-context MCP

The server source is versioned under:

```text
tools/mcp/project-context-mcp/
```

Its Python environment is local/disposable:

```text
tmp/local/project-context/venv/
```

Install/update it with:

```bash
python harness.py mcp-install
python harness.py client-config
```

## Optional Hermes variables

- `HERMES_REMOTE_*` — native remote Hermes API used by OpenCode custom run-control tools and verification.
- `HERMES_REMOTE_SIDECAR_PORT` + `HERMES_SIDECAR_TOKEN` — Claude-only Hermes MCP sidecar.
- `HERMES_PROJECT_USER` — unprivileged account on the main project machine.
- `HERMES_PROJECT_DENY_GLOBS` — sensitive paths denied to that account.

Hermes credentials remain in untracked `.env`/generated local material.

## Optional local models

Four generic model slots are retained from v3, but all are disabled by default. Enable only slots actually used by a project.
