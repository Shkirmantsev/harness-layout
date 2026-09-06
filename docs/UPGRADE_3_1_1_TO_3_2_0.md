# Upgrade: Harness Layout 3.1.1 -> 3.2.0

## Why this upgrade exists

Revision 3.1.1 exposed remote Hermes to OpenCode as a normal OpenAI-compatible model and generated an `@generated-hermes` subagent. That path can fail when Hermes executes its own server-side tools because OpenCode expects a normal model-provider tool-call response shape.

Revision 3.2.0 removes that model-backed path. OpenCode now delegates through project-local custom tools which call Hermes' native `/v1/runs` control API directly.

Claude Code -> Hermes remains unchanged: Claude still uses the dedicated remote MCP control sidecar.

## Safe upgrade

1. Back up your current root `.env` outside the replacement directory.
2. Extract the 3.2.0 project.
3. Copy your existing `.env` into the new root.
4. Run:

```bash
make env-sync
make check
make client-config
```

`make env-sync` adds new non-secret variables without overwriting existing values. In particular, review:

```dotenv
HERMES_REMOTE_OS_USER=dimitri             # example: SSH/copy login account
HERMES_REMOTE_RUNTIME_USER=hermes         # actual Hermes service Linux account
HERMES_REMOTE_RUNTIME_HOME=/srv/ai/hermes
HERMES_REMOTE_STAGING_DIR=/var/tmp/harness-hermes-worker-mcp
```

5. Restart OpenCode so it reloads project-local custom tools.

## Expected generated OpenCode state

After `make client-config`:

- `.opencode/tools/hermes.js` exists;
- `.generated/opencode-hermes-runtime.json` exists;
- `.generated/hermes-api-key` exists with mode 0600;
- `opencode.json` has no `hermes-remote` model provider;
- `.opencode/agents/generated-hermes.md` is removed.

OpenCode exposes these tools:

```text
hermes_delegate
hermes_status
hermes_wait
hermes_result
hermes_steer
hermes_approve
hermes_cancel
```

## Test

Start OpenCode normally with your preferred main model (for example MiniMax) and ask:

```text
Investigate this project. Delegate repository analysis to Hermes and use its result.
```

The main model should call `hermes_delegate`. If Hermes is still running after the local wait window, the main model should reuse the returned `run_id` with `hermes_wait`, `hermes_status`, or `hermes_result`; it must not start a duplicate run.

## Existing remote Hermes installation

You do not need to reinstall Hermes or the Claude sidecar merely to get the OpenCode 3.2 delegation fix. The already-working native API on port 8642 is sufficient.

The updated `make hermes-sidecar-copy` also fixes a separate setup problem for future installations: it stages sidecar source under `/var/tmp` rather than the SSH copy user's home, so a different Hermes runtime user can read it safely.
