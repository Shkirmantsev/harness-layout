#!/usr/bin/env python3
from __future__ import annotations
import json, os
from pathlib import Path
from common import ROOT, parse_env, bool_env, slug

GEN = ROOT / ".generated"

LOCAL_WORKER_INSTRUCTIONS = (
    "Before non-trivial work, route the compact task through "
    "`python3 scripts/skill_router.py --profile local-small` and read only the "
    "returned skill paths. Work from the supplied objective, acceptance criteria, "
    "constraints, and ContextPack; do not request the parent transcript or whole "
    "repository. Execute short sequential steps, verify observable behavior, and "
    "ask the parent when confidence is below the returned threshold. Return result, "
    "evidence, changed paths, checks, and unresolved risk; never expose hidden "
    "chain-of-thought.\n"
)

def write_json(path: Path, obj: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")

def model_catalog(env):
    out = {}
    for i in range(1, 5):
        if bool_env(env, f"LOCAL_MODEL_{i}_ENABLED"):
            alias = env.get(f"LOCAL_MODEL_{i}_ALIAS", f"local-{i}")
            out[alias] = {"name": env.get(f"LOCAL_MODEL_{i}_DISPLAY_NAME", alias)}
    if bool_env(env, "MINIMAX_ENABLED"):
        out[env.get("MINIMAX_ALIAS", "minimax")] = {"name": env.get("MINIMAX_DISPLAY_NAME", "MiniMax")}
    return out

def mcp_catalog(env):
    out = {}
    if bool_env(env, "WEB_SEARCH_ENABLED"):
        out["searxng"] = {"type": "remote", "url": f"http://127.0.0.1:{env.get('SEARXNG_MCP_PORT','18880')}/mcp"}
    if bool_env(env, "CRAWL4AI_ENABLED"):
        out["crawl4ai"] = {"type": "remote", "url": f"http://127.0.0.1:{env.get('CRAWL4AI_MCP_BRIDGE_PORT','18882')}/mcp"}
    if bool_env(env, "PLAYWRIGHT_ENABLED"):
        out["playwright"] = {"type": "remote", "url": f"http://127.0.0.1:{env.get('PLAYWRIGHT_MCP_PORT','8931')}/mcp"}
    return out

def hermes_base(env, sidecar: bool = False) -> str:
    scheme = env.get("HERMES_SIDECAR_SCHEME" if sidecar else "HERMES_REMOTE_SCHEME", "http")
    host = env.get("HERMES_REMOTE_HOST", "")
    port = env.get("HERMES_REMOTE_SIDECAR_PORT" if sidecar else "HERMES_REMOTE_OPENAI_PORT", "8775" if sidecar else "8642")
    return f"{scheme}://{host}:{port}"

def configure_claude(env, mcp):
    # Main Claude gets only optional local web/UI MCPs. Hermes is intentionally
    # subagent-scoped and talks directly to the REMOTE Claude-specific sidecar.
    write_json(ROOT / ".mcp.json", {"mcpServers": {k: {"type": "http", "url": v["url"]} for k, v in mcp.items()}})
    agents = ROOT / ".claude/agents"
    agents.mkdir(parents=True, exist_ok=True)
    for p in agents.glob("generated-*.md"):
        p.unlink()

    if bool_env(env, "CLAUDE_CODE_USE_LITELLM"):
        for i in range(1, 5):
            if not bool_env(env, f"LOCAL_MODEL_{i}_ENABLED"):
                continue
            alias = env.get(f"LOCAL_MODEL_{i}_ALIAS", f"local-{i}")
            claude_alias = env.get(f"LOCAL_MODEL_{i}_CLAUDE_ALIAS", f"claude-{alias}")
            name = f"{slug(alias)}-worker"
            (agents / f"generated-{name}.md").write_text(
                f"---\nname: {name}\ndescription: Independent local-model worker using {alias}.\nmodel: {claude_alias}\n---\n"
                + LOCAL_WORKER_INSTRUCTIONS,
                encoding="utf-8",
            )
        if bool_env(env, "MINIMAX_ENABLED"):
            (agents / "generated-minimax-worker.md").write_text(
                f"---\nname: minimax-worker\ndescription: Independent MiniMax worker/reviewer.\nmodel: {env.get('MINIMAX_CLAUDE_ALIAS','claude-minimax')}\n---\n"
                + LOCAL_WORKER_INSTRUCTIONS,
                encoding="utf-8",
            )

    if bool_env(env, "HERMES_ENABLED"):
        project_root = str(Path(env["PROJECT_ROOT"]).expanduser().resolve())
        token = env["HERMES_SIDECAR_TOKEN"]
        sidecar = hermes_base(env, sidecar=True)
        text = f'''---
name: hermes-worker
description: Delegate bounded autonomous repository work to the native remote Hermes Agent through the Claude-specific MCP control sidecar. Prefer for independent implementation, investigation, testing, or review that benefits from Hermes' own tools.
model: {env.get('CLAUDE_DISPATCHER_MODEL','haiku')}
maxTurns: 12
mcpServers:
  - hermes-native:
      type: http
      url: {sidecar}/mcp
      headers:
        Authorization: "Bearer {token}"
tools:
  - mcp__hermes-native__hermes_run
  - mcp__hermes-native__hermes_wait
  - mcp__hermes-native__hermes_status
  - mcp__hermes-native__hermes_result
  - mcp__hermes-native__hermes_steer
  - mcp__hermes-native__hermes_approve
  - mcp__hermes-native__hermes_cancel
---
You are a dispatcher, not the implementation agent. The working repository is `{project_root}` on the main machine.

Call `hermes_run` once with `project_root="{project_root}"` and a complete bounded task. Hermes itself must read/edit/search/test files with its native SSH-backed tools. Do not upload or proxy ordinary repository files through MCP. For images, PDFs and other repository files, tell Hermes the repository path and task; current Hermes handles repository image bytes through its own non-local backend/vision path. Preserve both returned `run_id` and `session_id`. A new `hermes_run` without `session_id` intentionally starts a fresh Hermes session; pass the prior `session_id` only for an intentional continuation. If `hermes_wait` returns `waiting_for_approval`, report the requested approval to the parent/user; call `hermes_approve` only after explicit authorization. Use status/result, steer and cancel as needed. Return the native Hermes result to the parent. Never launch Claude Code, OpenCode, or Codex recursively.
'''
        path = agents / "generated-hermes-worker.md"
        path.write_text(text, encoding="utf-8")
        path.chmod(0o600)

def configure_claude_gateway(env):
    path = ROOT / ".claude/settings.local.json"
    if not bool_env(env, "CLAUDE_CODE_USE_LITELLM"):
        if path.exists():
            path.unlink()
        return
    write_json(path, {
        "env": {
            "ANTHROPIC_BASE_URL": f"http://127.0.0.1:{env.get('LITELLM_PORT','18400')}",
            "ANTHROPIC_AUTH_TOKEN": env.get("LITELLM_MASTER_KEY", ""),
        },
        "model": env.get("CLAUDE_DEFAULT_MODEL", "opus"),
        "effortLevel": env.get("CLAUDE_DEFAULT_EFFORT", "medium"),
    })
    path.chmod(0o600)

def configure_opencode(env, mcp):
    # OpenCode delegates to Hermes through project-local custom tools that call
    # the native Hermes Runs API directly. Hermes is NOT exposed as an
    # OpenAI-compatible model/subagent because its server-side tool events are
    # part of a full agent loop, not a normal model-provider tool-call loop.
    config = {
        "$schema": "https://opencode.ai/config.json",
        "permission": {
            "read": {".env": "deny", ".env.*": "deny", "**/.env": "deny", "**/.env.*": "deny"},
        },
        "mcp": dict(mcp),
    }
    providers = {}
    if bool_env(env, "LITELLM_ENABLED"):
        providers["harness"] = {
            "name": "Harness LiteLLM",
            "npm": "@ai-sdk/openai-compatible",
            "options": {"baseURL": f"http://127.0.0.1:{env.get('LITELLM_PORT','18400')}/v1", "apiKey": "{file:.generated/litellm-master-key}"},
            "models": model_catalog(env),
        }
    if providers:
        config["provider"] = providers

    tool_dir = ROOT / ".opencode/tools"
    tool_dir.mkdir(parents=True, exist_ok=True)
    for p in [*tool_dir.glob("generated-hermes.*"), tool_dir / "hermes.js"]:
        if p.exists():
            p.unlink()

    # Remove the obsolete model-backed Hermes subagent from earlier revisions.
    agent_dir = ROOT / ".opencode/agents"
    agent_dir.mkdir(parents=True, exist_ok=True)
    for p in agent_dir.glob("generated-hermes*.md"):
        p.unlink()

    runtime_path = GEN / "opencode-hermes-runtime.json"
    if bool_env(env, "HERMES_ENABLED"):
        project_root = str(Path(env["PROJECT_ROOT"]).expanduser().resolve())
        runtime = {
            "apiBase": hermes_base(env),
            "projectRoot": project_root,
        }
        write_json(runtime_path, runtime)
        runtime_path.chmod(0o600)

        template = ROOT / "templates/opencode/hermes.js"
        target = tool_dir / "hermes.js"
        target.write_text(template.read_text(encoding="utf-8"), encoding="utf-8")
        target.chmod(0o600)

        # Custom tools are normal OpenCode tools. Delegation/status/result/etc.
        # may run automatically, but resolving a remote approval must remain a
        # human-visible confirmation point.
        config["permission"]["hermes_*"] = "allow"
        config["permission"]["hermes_approve"] = "ask"
    elif runtime_path.exists():
        runtime_path.unlink()

    write_json(ROOT / "opencode.json", config)

def configure_codex(env, mcp):
    # No Hermes integration here in this phase. Codex receives only optional
    # shared web/UI MCPs.
    lines = []
    for name, spec in mcp.items():
        lines += [f"[mcp_servers.{name.replace('-', '_')}]", f'url = "{spec["url"]}"', ""]
    path = ROOT / ".codex/config.toml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")

def write_secrets(env):
    GEN.mkdir(exist_ok=True)
    for name, value in (
        ("litellm-master-key", env.get("LITELLM_MASTER_KEY", "")),
        ("hermes-api-key", env.get("HERMES_REMOTE_API_KEY", "")),
    ):
        p = GEN / name
        p.write_text(value + "\n", encoding="utf-8")
        p.chmod(0o600)

def main():
    env = parse_env()
    GEN.mkdir(exist_ok=True)
    mcp = mcp_catalog(env)
    write_secrets(env)
    configure_claude_gateway(env)
    configure_claude(env, mcp)
    configure_opencode(env, mcp)
    configure_codex(env, mcp)
    print("Client configurations generated: Claude=remote MCP sidecar, OpenCode=direct Hermes Runs API tools, Codex=no Hermes transport.")

if __name__ == "__main__":
    main()
