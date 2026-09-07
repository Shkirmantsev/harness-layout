# Shared skills

Canonical source: `.agents/skills/`.

```text
.agents/skills
   |-- skill-router/          directly discoverable core
   |-- project-safety/        directly discoverable core
   |-- session-checkpoint/    directly discoverable core
   |-- verification/          directly discoverable core
   `-- catalog/               optional skills read only after routing
```

For every non-trivial task, run the router once from the project root:

```bash
printf '%s' "$TASK_TEXT" | python3 scripts/skill_router.py --profile balanced
```

The result is a stable activation plan. Read only each
`required_skills[].path`; do not scan or preload the catalog. Explicit skill
names are supported, including `grill me`, which resolves to the combined
canonical `grilling` workflow. The router applies deterministic rules before
metadata scoring, bounds the selection to 3–7 skills, and uses a four-skill,
eight-step contract for `local-small` models.

`make skills-sync-local` copies only the four core skills to `.claude/skills`
and removes stale project-managed catalog copies. It does not remove unrelated
personal Claude skills. OpenCode and Codex discover the core directly from
`.agents/skills`.

The remote sync uses ordinary `rsync` over SSH/Tailscale and deletes only stale
content inside Hermes' dedicated `harness-layout` skill subdirectory. Optional
catalog skills remain available to native Hermes at their repository paths
through its configured SSH backend; they are not made globally discoverable.

## Resumable state

Use `session-checkpoint` for every non-trivial task and update it after material
steps, decisions, failures, and verification. The standard-library helper stores
compact canonical JSON under `.ai/state/handoffs/`, atomically regenerates
`.ai/state/CURRENT.md`, and validates project file hashes on resume:

```bash
python3 scripts/session_state.py resume
```

Exit code `3` reports drift and requires re-inspection. Checkpoints contain no
raw chain-of-thought, full transcript, credential, or repository snapshot.
Compatible old checkpoints under `tmp/local/sessions/` are promoted on resume
or update. The current session ID is discovered from generated Markdown, so an
empty-dialog session does not need the prior chat or an ID copied by hand.
`python3 scripts/session_state.py verify` detects a stale/manual current view and
is included in `python3 harness.py check`.

Third-party and adapted skills, their pinned audit revisions, licensing, selection decisions, and conflict-resolution notes are documented in [THIRD_PARTY_SKILLS.md](THIRD_PARTY_SKILLS.md).

When updating a vendored skill, preserve project-specific safety and client-routing adaptations. Review upstream changes against the recorded revision instead of replacing the directory wholesale.

Provider-neutral budgets, model classes, cache ordering, metrics, and
self-improvement constraints live in `.harness/runtime.json`. Skills cannot
grant themselves tools or expand the project boundary.
