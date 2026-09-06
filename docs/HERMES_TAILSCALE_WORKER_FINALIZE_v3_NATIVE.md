# Execution specification — finalize `hermes-tailscale-worker` for Harness Layout Native v3

> Give this entire file to the Hermes Agent/operator running on the **remote Hermes PC/VPS**. Execute phase by phase, make backups, and report PASS / FAIL / NOT RUN. Never print secret values.

## Goal

Finalize the **existing** `hermes-tailscale-worker` profile for the simplified native architecture:

```text
MAIN PC / PROJECT                                  REMOTE HERMES HOST
┌──────────────────────────────────┐              ┌──────────────────────────────┐
│ OpenCode                         │ Tailscale    │ existing Hermes Gateway      │
│  └─ OpenAI-compatible HTTP ──────┼─────────────►│ native API :8642             │
│                                  │              │ profile hermes-tailscale-    │
│ Claude Code                      │              │ worker                       │
│  └─ hermes-worker subagent       │              │                              │
│      └─ MCP control ─────────────┼─────────────►│ hermes-worker-mcp :8775      │
│                                  │              │   └─ localhost /v1/runs      │
│ PROJECT_ROOT                     │◄─────────────│ native Hermes SSH backend    │
│  └─ ACL access for hermes-worker │   SSH/TS     │                              │
└──────────────────────────────────┘              └──────────────────────────────┘
```

There is **no project binding database, project bridge, attachment relay, project-file MCP, second Hermes runtime, `/workspace` symlink, or project SSH container** in this design.

OpenCode does **not** use the Claude MCP sidecar. Its project-local `hermes_*` tools connect directly to the existing native Hermes Runs API.

---

## Existing state that must be preserved

The installation may already have:

- profile `hermes-tailscale-worker`;
- working provider/OAuth/subscription configuration;
- native Hermes API server;
- a user-systemd gateway service;
- `SOUL.md`, memory, skills and scheduled jobs;
- other Hermes profiles/services.

**Do not recreate the profile. Do not replace SOUL.md. Do not rotate provider/OAuth/API credentials. Do not modify other profiles or Telegram routing.**

---

## Phase 0 — inspect and back up

Run from a host-local shell/session on the remote Hermes machine:

```bash
set -euo pipefail
hermes --version || hermes version
hermes profile list
hermes profile show hermes-tailscale-worker
tailscale status || true
tailscale ip -4 || true
systemctl --user --no-pager status hermes-tailscale-worker-gateway.service || true
ss -tlnp | grep -E '(:8642|:8775)' || true
```

Resolve the exact worker profile directory from `hermes profile show` as `WORKER_PROFILE_HOME`.

Create a private backup:

```bash
BACKUP="$HOME/.local/state/hermes-native-finalize/$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$BACKUP"
chmod 700 "$BACKUP"
for f in config.yaml .env SOUL.md profile.yaml; do
  [ -e "$WORKER_PROFILE_HOME/$f" ] && cp -a "$WORKER_PROFILE_HOME/$f" "$BACKUP/$f.before"
done
```

Do not print `.env` or provider credential files.

---

## Phase 1 — Hermes version policy

Required baseline for this harness: **Hermes Agent >= 0.20.5**. The stable v0.20.5 API includes `/v1/runs`, run status/events/approval/steer/stop, the OpenAI-compatible API, SSH-backed file tools, and non-local image-path resolution used by this architecture.

If the installed version is already >= 0.20.5, **do not update merely because a newer source commit exists**.

If it is older, first back up and then use the supported updater:

```bash
hermes update
hermes --version
hermes doctor
```

After an update, verify that the existing gateway unit still points at a valid Hermes executable before continuing.

---

## Phase 2 — preserve and verify the native OpenAI-compatible API

The native API is the correct OpenCode ingress. Preserve its current API key and profile provider/model configuration.

Expected worker-profile `.env` semantics:

```dotenv
API_SERVER_ENABLED=true
API_SERVER_PORT=8642
API_SERVER_MODEL_NAME=hermes-tailscale-worker
```

Keep the existing secure bind policy. Do not expose it to the public Internet. A Tailscale-only bind is preferred.

Verify locally:

```bash
curl --fail http://127.0.0.1:8642/health
```

Load `API_SERVER_KEY` privately from the profile `.env` and verify without printing it:

```bash
curl --fail \
  -H "Authorization: Bearer $API_SERVER_KEY" \
  http://127.0.0.1:8642/v1/models
```

Expected advertised public identity:

```text
hermes-tailscale-worker
```

Also inspect capabilities:

```bash
curl --fail \
  -H "Authorization: Bearer $API_SERVER_KEY" \
  http://127.0.0.1:8642/v1/capabilities
```

Require run submission/status/steer/stop support. Approval support should also be present for coding runs that pause for permission.

### Important model rule

The public OpenAI model name `hermes-tailscale-worker` is an **agent/profile identity**, not necessarily the actual underlying provider model ID.

The Claude MCP sidecar must therefore **omit the `model` field on `POST /v1/runs`** so the worker profile's configured provider/model remains authoritative.

---

## Phase 3 — configure native project access through SSH

The main PC owns the repository. It has a dedicated unprivileged Linux account such as `hermes-worker` with ACL access to the selected project directory.

Merge into the worker profile `config.yaml`:

```yaml
terminal:
  backend: ssh
  cwd: "~"
  timeout: 900
  persistent_shell: true
```

Do **not** globally set a project path in this reusable profile. Each Claude/OpenCode delegated task carries the concrete absolute `PROJECT_ROOT` and begins by changing to it.

In the worker profile `.env`, configure the native SSH backend for the dedicated account:

```dotenv
TERMINAL_ENV=ssh
TERMINAL_SSH_HOST=<MAIN_TAILSCALE_DNS_NAME>
TERMINAL_SSH_USER=hermes-worker
TERMINAL_SSH_PORT=22
TERMINAL_SSH_PERSISTENT=true
```

If the final design uses Tailscale SSH, no new SSH keypair should be created merely for this harness. Hermes uses `BatchMode=yes`, so the tailnet SSH policy must allow this connection without an interactive re-authentication step.

Test from the remote Hermes host:

```bash
ssh -o BatchMode=yes -o ConnectTimeout=10 hermes-worker@<MAIN_TAILSCALE_DNS_NAME> \
  'pwd; id; test -r <ABSOLUTE_PROJECT_ROOT> && test -w <ABSOLUTE_PROJECT_ROOT> && echo PROJECT_ACCESS_OK'
```

Do not grant the worker sudo/docker/admin-group membership as a workaround.

---

## Phase 4 — prove native Hermes file and image confinement

Use the native API or a worker session to perform a harmless project smoke test. The task must explicitly name the real project root and tell Hermes to establish that cwd first.

Require Hermes to:

1. `cd <ABSOLUTE_PROJECT_ROOT>` and report `pwd`;
2. list the repository root;
3. read `AGENTS.md` or another harmless text file;
4. create a temporary file inside the project, read it, then remove it;
5. confirm that a private path outside the ACL-authorized project is inaccessible to the dedicated account.

All file operations must be native Hermes terminal/file operations over the configured SSH backend. There must be no binding DB/project relay/project-file MCP involved.

If a safe repository image exists, run one native vision-by-path smoke test. Hermes 0.20.5+ resolves non-cache media paths inside non-local backends. If the main model is text-only, verify a valid auxiliary vision route exists; otherwise report vision as NOT CONFIGURED/NOT RUN.

---

## Phase 5 — install the Claude-only MCP control sidecar

Use the supplied **`hermes-worker-mcp` 1.1** package. It is a separate small Python environment, not another Hermes runtime.

Expected remote location:

```text
$HOME/.local/share/hermes-worker-mcp/
```

From a host-local shell:

```bash
cd "$HOME/.local/share/hermes-worker-mcp"
make init
```

Edit the sidecar `.env` so it contains:

```dotenv
SIDECAR_TAILSCALE_HOST=<REMOTE_TAILSCALE_DNS_NAME>
SIDECAR_TAILSCALE_IP=<REMOTE_TAILSCALE_IPV4>
SIDECAR_PORT=8775
HERMES_SIDECAR_TOKEN=<generated by make init>
HERMES_API_BASE_URL=http://127.0.0.1:8642
HERMES_API_KEY=<imported existing API_SERVER_KEY>
HERMES_PROFILE_HOME=<exact existing worker profile path>
LOG_LEVEL=INFO
```

**`HERMES_API_BASE_URL` is the server root and must NOT contain `/v1`.**

Import the existing native API key without printing it:

```bash
make import-api-key
make check
make test
```

Install/start:

```bash
make install
make up
make status
make verify
```

The sidecar must bind only to the remote node's Tailscale IP on port `8775` and require its independent `HERMES_SIDECAR_TOKEN`.

Its only MCP tools must be:

```text
hermes_run
hermes_status
hermes_wait
hermes_result
hermes_steer
hermes_approve
hermes_cancel
```

Contract requirements:

- `hermes_run` -> `POST /v1/runs` and **no public-profile model override**;
- fresh Hermes session by default; explicit previous `session_id` only for intentional continuation;
- `hermes_steer` -> `POST /v1/runs/{id}/steer` with JSON `{ "input": "..." }`;
- `hermes_wait` returns when status is `waiting_for_approval` instead of waiting until timeout;
- `hermes_approve` accepts only `once`, `session`, `always`, or `deny` and must never be called automatically;
- `hermes_cancel` -> `POST /v1/runs/{id}/stop`;
- health probes native `/health` at the root server URL;
- no filesystem API, project upload, binding DB, TUI subprocess or second Hermes runtime.

---

## Phase 6 — validate Claude MCP path

From the main PC, Claude Code will connect directly to:

```text
http://<REMOTE_TAILSCALE_DNS_NAME>:8775/mcp
```

with:

```text
Authorization: Bearer <HERMES_SIDECAR_TOKEN>
```

Run a harmless Claude delegation and require:

- one `hermes_run` call;
- returned `run_id` **and** `session_id` retained by the dispatcher;
- polling through `hermes_wait`/`hermes_status`;
- final result through `hermes_result`;
- no repository file bytes sent through MCP;
- a second unrelated delegation without `session_id` receives a different Hermes session;
- a deliberate continuation using the prior `session_id` reuses that session;
- if a run pauses for approval, Claude surfaces that fact rather than auto-approving it.

---

## Phase 7 — validate OpenCode direct API path

OpenCode does **not** use this MCP sidecar.

Its provider should point directly to:

```text
http://<REMOTE_TAILSCALE_DNS_NAME>:8642/v1
```

using the existing `API_SERVER_KEY` and public model identity:

```text
hermes-tailscale-worker
```

OpenCode must not wrap Hermes as a model-backed subagent. `make client-config` generates project-local `hermes_*` tools which use `/v1/runs`; the normal OpenCode main agent invokes those tools to delegate bounded work.

Run one harmless read-only repository task from OpenCode and verify the actual file evidence comes from the native SSH-backed Hermes tools.

---

## Phase 8 — optional web/runtime services on the main harness

The simplified harness has no Firecrawl stack.

Optional local services are independent of remote Hermes:

```text
SearXNG          optional search/discovery
Crawl4AI 0.9.2  optional crawl/render/extraction
Playwright MCP   optional interactive UI/browser testing
LiteLLM          local model gateway; not used for OpenCode -> Hermes
```

Do not install Firecrawl, RabbitMQ or PostgreSQL for this layout.

---

## Phase 9 — retire obsolete bridge components only after E2E passes

After native SSH/file/vision smoke tests, Claude MCP, and OpenCode direct API all pass, remove/disable obsolete harness-specific pieces if they still exist:

- `harness_project` MCP;
- binding SQLite DB/session bridge;
- project relay/attachment relay;
- project-specific `/workspace` symlink;
- obsolete project-SSH container;
- stale bridge tokens/configuration.

Do not remove unrelated skills/MCP servers, memory, jobs, Telegram integration, provider credentials, or other profiles.

---

## Final verification matrix

Report PASS / FAIL / NOT RUN for:

- Hermes version >= 0.20.5;
- existing worker profile preserved;
- provider/OAuth/subscription configuration preserved;
- SOUL.md/memory preserved;
- native `/health`, `/v1/models`, `/v1/capabilities` healthy;
- Tailscale SSH BatchMode access to dedicated main-PC account;
- native project read/write/delete smoke;
- private non-project path denied by main-PC ACL/account permissions;
- native image-by-path test or explicit NOT RUN reason;
- sidecar config/test/service/health;
- unauthenticated sidecar request rejected;
- sidecar `/v1/runs` contract verified with no model override;
- fresh-session default verified;
- intentional session continuation verified;
- approval-pause behavior verified or NOT RUN;
- Claude Code MCP end-to-end delegation;
- OpenCode direct native OpenAI API end-to-end task;
- obsolete binding/project-bridge components absent/removed;
- no recursive Claude/OpenCode/Codex launch from Hermes.

Do not claim production-ready until the real main machine and remote Hermes machine have exercised both Claude and OpenCode paths.

---

## Required final report

Return a sanitized report with:

1. versions;
2. worker profile path/name;
3. backup path;
4. native API bind/identity without secrets;
5. exact non-secret config keys changed;
6. Tailscale SSH/project ACL test results;
7. native file/vision smoke results;
8. sidecar version/service endpoint/status;
9. Claude MCP E2E result;
10. OpenCode direct API E2E result;
11. obsolete bridge components removed/retained;
12. PASS/FAIL/NOT RUN matrix;
13. rollback commands.

Never include API keys, OAuth tokens, sidecar tokens, private provider credentials, or unrelated user files in the report.
