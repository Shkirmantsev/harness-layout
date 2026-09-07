# Proposal

## Why

OpenSpec 1.12 installs Codex workflow skills directly under `.agents/skills/`,
but the harness currently treats every immediate skill directory as one of its
four core routing skills. That makes the requested Codex integration fail the
harness contract and causes `skills-sync-local` to reclassify and copy
OpenSpec-owned outputs as harness core.

## Goal

Allow tool-owned OpenSpec skills to coexist with the four harness-owned core
skills while keeping ownership, synchronization, and progressive-loading
boundaries explicit.

## Affected capabilities

- Skill exposure and ownership
- Local Claude skill synchronization
- OpenSpec client integration for Codex, OpenCode, and Claude Code

## Compatibility / migration impact

Existing core and catalog skill behavior remains unchanged. Re-running
`openspec init --tools opencode,claude,codex` remains the source of truth for
OpenSpec-generated files. The harness sync will copy only its named core skills
and will preserve OpenSpec-owned client skills rather than overwriting them.
Removing the OpenSpec integration remains reversible by removing its generated
client artifacts or rerunning OpenSpec initialization with a different tool set.

## Related knowledge

- `kb://architecture.system-overview`
- `docs/SKILLS.md`
- `docs/THIRD_PARTY_SKILLS.md`
