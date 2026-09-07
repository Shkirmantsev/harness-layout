# Design

## Current state

`scripts/sync_skills.py` derives the harness core set by scanning every immediate
`*/SKILL.md` below `.agents/skills/`. Tests and documentation assume this set is
exactly four skills. OpenSpec 1.12 also uses `.agents/skills/` as Codex's standard
project skill directory, so its six generated workflow skills are accidentally
classified as harness core and copied by the harness into Claude's tool-owned
output directory.

## Proposed design

Define the four harness core skill names explicitly in `sync_skills.py` and
resolve only those paths for local and remote synchronization. Treat other
top-level skills as integration-owned and leave them untouched. Tests will
assert both invariants: the harness core remains exactly four, and supported
OpenSpec skills coexist without being removed by local synchronization.

This keeps ownership aligned with generators:

- `scripts/sync_skills.py` owns the four harness core copies.
- `openspec init` owns `openspec-*` skills and `opsx*` commands.
- The skill router continues to own optional catalog selection.

Alternatives rejected:

- Treating all ten top-level skills as core weakens the bounded-context design
  and causes the harness to overwrite another generator's output.
- Moving OpenSpec skills into `catalog/` preserves the four-skill count but
  breaks Codex's documented `$openspec-*` direct invocation.
- Relocating Codex output to `.codex/skills/` relies on a legacy path that
  OpenSpec 1.12 intentionally migrated away from.

## Affected modules / interfaces

- `scripts/sync_skills.py`: core ownership selection and sync reporting.
- `tests/test_skill_runtime.py`: core and integration coexistence contract.
- `docs/SKILLS.md`, `docs/THIRD_PARTY_SKILLS.md`, and the architecture Wiki:
  current ownership and invocation behavior.
- OpenSpec-generated directories remain unmodified and are refreshed only by
  the upstream CLI.

## Data / persistence / concurrency impact

No application data, persistence, network, or concurrent runtime is affected.
Synchronization remains a local filesystem operation. Failure remains
fail-fast: a missing named core skill is an error rather than silently reducing
the core set.

## Compatibility and migration

Existing users without OpenSpec retain the same four core skills. Users with
OpenSpec keep direct Codex discovery and client-specific Claude/OpenCode command
syntax. Local and remote harness syncs exclude integration-owned skills; remote
Hermes therefore retains its existing core-only contract.

## Risks and rollback

The main risk is a renamed or missing core directory. Explicit validation and
tests cover that failure. Rollback is the inverse patch to the sync logic and
documentation; OpenSpec-generated artifacts can be removed or regenerated
independently with the OpenSpec CLI.
