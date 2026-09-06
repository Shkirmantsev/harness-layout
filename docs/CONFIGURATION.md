# Configuration

Root `.env` is the only normal user configuration file. Run `make init`, then edit `.env`; routine setup should not require editing Compose or subfolder config files.

## Feature flags

| Variable | Default | Purpose |
|---|---:|---|
| `LITELLM_ENABLED` | true | Local gateway for LM Studio/direct MiniMax model slots. |
| `HERMES_ENABLED` | false | Enable external Hermes client generation/verification. Adds **no local container**. |
| `WEB_SEARCH_ENABLED` | false | Optional SearXNG discovery/search. |
| `CRAWL4AI_ENABLED` | false | Optional Crawl4AI render/extract service. |
| `PLAYWRIGHT_ENABLED` | false | Optional interactive browser MCP. |
| `LITELLM_EXPOSE_ON_TAILSCALE` | false | Expose local LiteLLM only on the main Tailscale IP. |

## Hermes variables

- `HERMES_REMOTE_*` — native Hermes API used by OpenCode project-local `/v1/runs` tools and by verification.
- `HERMES_REMOTE_SIDECAR_PORT` + `HERMES_SIDECAR_TOKEN` — remote Claude-only MCP sidecar.
- `HERMES_PROJECT_USER` — unprivileged account on the main project machine.
- `HERMES_PROJECT_DENY_GLOBS` — current sensitive paths whose ACL is explicitly denied for that account.

The sidecar token and native Hermes API key are different credentials. Both stay in untracked `.env`; generated client key/material is under gitignored `.generated` or generated Claude agent files.

## Local models

Four generic model slots exist. Slot 1/2 contain example defaults and can be replaced entirely by editing `.env`. No Compose/Python modification is required.

## Secrets

`make init` generates only local values marked `AUTO_GENERATE`. Remote Hermes credentials are intentionally not fabricated; obtain them from the configured remote Hermes API/sidecar setup.
