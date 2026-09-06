# Adaptive skill runtime implementation plan

**Goal:** Turn the installed project skills into a genuinely progressive,
cross-client catalog with deterministic routing, weak-model limits, resumable
state, and evidence-gated self-improvement.

**Architecture:** Keep only safety/router/checkpoint/verification directly
discoverable. Store optional skills one level deeper under the canonical skill
tree. A standard-library router returns a bounded ActivationPlan; a separate
atomic checkpoint CLI persists operational evidence. Existing client transports
and native tools remain authoritative.

## Gate 1: progressive skill activation

- Add failing router/layout/sync tests.
- Add `scripts/skill_router.py` and the `skill-router` contract.
- Move optional skills to `.agents/skills/catalog/` without changing contents.
- Sync only core skills to Claude/remote Hermes; preserve unrelated personal
  skills.
- Verify explicit aliases, conflicts, near misses, deterministic output, and
  local-small caps.

## Gate 2: resumable evidence state

- Add failing checkpoint, outside-root, and drift tests.
- Add `scripts/session_state.py` and `session-checkpoint` contract.
- Use locks, same-directory temporary files, fsync, atomic replace, project
  relative file hashes, and distinct exit codes.
- Store no raw reasoning, secrets, full logs, or repository copies.

## Gate 3: portable policy and documentation

- Record provider-neutral model classes, loop budgets, prompt-layer ordering,
  self-improvement constraints, and metrics in `.harness/runtime.json`.
- Update AGENTS/README/skills/operator documentation.
- Add a report recommendation matrix with adopted/adapted/deferred/rejected
  decisions.

## Gate 4: remaining kernel capabilities

- Add and evaluate a deterministic repository reconnaissance capsule. **Done.**
- Add a content-addressed ContextPack schema/generator. **Done.**
- Add a candidate-only, evidence/eval-backed learning loop. **Done.**
- Add host-side state-transition and no-progress enforcement. **Done for the
  checkpoint-driven runtime; no autonomous scheduler added.**
- Integrate routing profiles into generated local-worker prompts. **Done for
  generated Claude/LiteLLM workers; OpenCode and Codex inherit the project
  router rule from `AGENTS.md`.**
- Collect real provider/client usage before adding caching adapters or an
  embeddings/knowledge service. **Kept as an explicit future evidence gate;
  no savings are fabricated when a client does not expose usage telemetry.**

## Verification

- Focused red/green runtime tests.
- All unit tests.
- All project `SKILL.md` validations, including nested catalog skills.
- Python and JavaScript syntax checks.
- `make skills-sync-local` and `make skills-check`.
