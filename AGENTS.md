# Harness agent policy

This repository is a reusable layout for local and remote coding agents.

- Work only inside the active `PROJECT_ROOT`/repository unless the user explicitly changes scope.
- Never print or commit `.env`, generated API-key files, provider credentials, or private SSH material.
- Remote Hermes is a **native autonomous agent**, not a filesystem proxy target. It reads/edits/tests/analyzes repository media through its own configured SSH backend.
- Preserve the client split: Claude Code -> dedicated remote Hermes MCP sidecar; OpenCode -> project-local `hermes_*` tools calling the native Hermes `/v1/runs` control API directly; Codex -> no Hermes transport in this phase.
- The Claude MCP sidecar is control-plane only. Do not add project mounts, binding DBs, file upload/read APIs, or a second Hermes runtime to it.
- Do not reintroduce the removed project-bridge/session-binding/attachment-relay architecture.
- Do not recursively launch Claude Code, OpenCode, or Codex from remote Hermes.
- Canonical project skills live in `.agents/skills`; use `make skills-sync-local` / `make skills-sync-remote`.
- For each non-trivial task, run the directly discoverable `skill-router` once before reading optional skill instructions. Read only the returned `.agents/skills/catalog/*/SKILL.md` paths; reroute only after a material goal or phase change. Use its `local-small` profile for weaker/local models.
- Store resumable operational evidence with `session-checkpoint`; never put raw reasoning, full chats, or secrets into checkpoint state.
- Web routing: SearXNG discovers URLs, Crawl4AI reads/renders/extracts public pages, Playwright MCP performs interactive UI checks. Firecrawl is intentionally not part of this layout.
- Run the smallest relevant verification and report PASS/FAIL/NOT RUN accurately.

- OpenCode must not represent Hermes as a normal model/provider subagent. Delegate with `hermes_delegate`; continue an existing run with `hermes_wait`/`hermes_status`/`hermes_result`, and never start a duplicate run merely because a wait timed out.
