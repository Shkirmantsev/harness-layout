# Migrating an existing harness-layout repository to v4

This guide assumes your current Git repository already contains an older harness-layout revision and product/project files that must remain untouched.

## Files/directories to remove from the old harness before copying v4

Remove these **generated/runtime/vendor-local artifacts** if they exist:

```text
.generated/
.mcp.json
opencode.json
.codex/config.toml
.claude/settings.local.json
.claude/agents/generated-*.md
.opencode/agents/generated-*.md
.opencode/tools/generated-hermes.*
.opencode/tools/hermes.js
tmp/local/project-context/
```

Why: v4 regenerates them from `.env` and canonical source. Keeping older generated files can mix incompatible client generations, stale endpoints, or secrets.

If an old **distributed template copy/ZIP** accidentally contains these, do not copy them into the target repository (or remove only the copied template artifacts):

> **Never delete the `.git/` directory of your real existing project.** Preserve its complete repository history. The rule below applies only to a `.git/` directory that was accidentally bundled inside an old harness template/archive.

```text
.git/                 # template/archive copy only; NEVER your target repo's .git
.idea/
.vscode/                 # only if it is machine-local and not intentionally shared
node_modules/
build/
dist/
target/
__pycache__/
.pytest_cache/
```

Why: they are repository history, IDE/runtime cache, dependencies or build outputs, not reusable harness source.

## Files to review rather than blindly delete

```text
.env
AGENTS.md
CLAUDE.md
.ai/wiki/
openspec/
.agents/skills/
```

- Keep your existing `.env` somewhere safe, then merge only still-supported values into the v4 `.env.example` model. Never copy credentials into Git.
- Replace old harness-specific `AGENTS.md`/`CLAUDE.md` with v4 and re-add only genuinely project-specific rules. Do not bring back large architecture/Wiki content into these always-loaded files.
- Preserve real project Wiki/OpenSpec content. Merge it into the v4 directory contract instead of deleting it.
- Keep custom skills that are project-relevant, but remove duplicate/obsolete generated client copies.

## New v4 canonical additions

```text
harness.py
.ai/AGENTS.md
.ai/wiki/INDEX.md
.ai/wiki/architecture/
.ai/wiki/project/
.ai/wiki/domain/
.ai/wiki/modules/
.ai/wiki/interfaces/
.ai/wiki/adr/
.ai/wiki/glossary/
.ai/state/CURRENT.md
openspec/schemas/production-sdd/
tools/mcp/project-context-mcp/
docs/QUICKSTART.md
docs/OPENCODE_COMPATIBILITY.md
```

## After copying

```bash
python harness.py init
python harness.py mcp-install
python harness.py client-config
python harness.py check
```

On Linux/macOS/WSL you can use equivalent `make` targets.

## OpenCode migration detail

v4 intentionally defaults to:

```dotenv
OPENCODE_CONFIG_GENERATION=v1
```

Do not keep an older generated `opencode.json`. Regenerate it. Use `v2` only as an explicit beta opt-in.
