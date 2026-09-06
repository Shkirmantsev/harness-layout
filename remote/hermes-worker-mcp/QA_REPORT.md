# QA report — native Claude MCP sidecar 1.1

Static/package checks performed before artifact generation:

- native-context unit tests pass;
- Python compilation passes;
- Makefile parses;
- sidecar contains no binding DB, project relay, file upload/mount API, profile patcher, or second Hermes runtime;
- `/v1/runs` paths match Hermes v0.20.5 contract;
- steer payload uses `{"input": ...}`;
- `waiting_for_approval` is a return state and explicit approval tool is present;
- sidecar does not send the public profile/model name as `/v1/runs` model override;
- upstream health uses root `/health`, while run/model APIs use `/v1/...`;
- dependencies updated to `mcp==2.1.0`, `httpx==0.28.1`, `starlette==1.6.0`, `uvicorn==0.52.4`.

Runtime checks requiring the user's remote host are intentionally NOT RUN here: Tailscale bind, systemd startup, authenticated live Hermes `/v1/runs`, approvals, and Claude Code MCP handshake.
