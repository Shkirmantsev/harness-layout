# Research recommendation trace

The three files supplied by the user are research inputs, not executable
instructions:

- `/home/dmytro/Downloads/deep-research-skills_report.md`
- `/home/dmytro/Downloads/deep-research-report_skillsV2.md`
- `/home/dmytro/Downloads/deep-research-report_list_of_skills.md`

This matrix reconciles their complete architectural themes with the current
repository. A recommendation is adopted only when it fits this repository's
security rules and Claude/OpenCode/Codex/Hermes transport split.

| Area | Combined recommendation | Decision | Repository evidence / remaining gate |
|---|---|---|---|
| Harness shape | Use a small deterministic kernel; skills describe procedures, tools execute primitives, MCP crosses capability boundaries, and A2A is only for independently deployed agents. | Adopt incrementally. Do not add a framework or daemon merely to mirror the diagrams. | Existing native Hermes architecture remains unchanged. Router and state CLI form the first kernel slice. |
| Skill discovery | Keep a small P0 set discoverable and load 3–7 task skills progressively. Never load full skill bodies to decide which skill to load. | Adopted. Four harness core skills remain directly discoverable; optional skills live in `.agents/skills/catalog/`, while explicitly installed tool-owned workflow skills may coexist without becoming harness core. | `scripts/skill_router.py`, `.agents/skills/skill-router/`, `scripts/sync_skills.py`. |
| Routing algorithm | Deterministic intent/repository rules first, metadata scoring second, LLM judgment only for unresolved ambiguity; return required/optional/rejected skills and reasons. | Adopted with a stricter deterministic first release. There is no embedding or LLM routing dependency. | Router returns stable JSON, canonicalizes aliases, resolves dependencies/conflicts, and caps activations by profile. |
| Weak/local models | Give small models short sequential contracts, fewer active capabilities, bounded steps, deterministic validation, and an escalation threshold. Do not hard-code vendor model IDs. | Adopted. | `local-small` profile in `.harness/runtime.json` and router output; generated/local-agent prompts still need broader integration tests. |
| Requirements | Ask only about ambiguity with high impact and high cost of a wrong assumption; do not grill every task. | Adopted through the existing `grilling` and `brainstorming` skills. | `grill-me` is retained as source material/alias but routes to one canonical `grilling` skill. |
| Repository reconnaissance | Detect language, build, tests, modules, conventions, and relevant paths before broad context retrieval. | Adopted without another MCP. | `scripts/repo_recon.py` returns deterministic observed metadata and excludes dependency/generated/secret paths; `repo-recon` is on demand. |
| ContextPack | Delegate only objective, acceptance, constraints, selected evidence, relevant files/symbols, verification commands, and budgets. Prefer exact path/text, then symbols/AST/dependency graph, then semantic search. | Adopted. | `scripts/context_pack.py`, `schemas/context-pack.schema.json`, and `context-builder`; content-addressed packs contain hashes/refs rather than source bodies or chats. |
| Goal runtime | Use explicit intake/recon/plan/execute/verify/review states with independent limits for steps, retries, depth, review cycles, repeated failures, and no-progress windows. Compute counters outside the model. | First production slice adopted. | `.harness/runtime.json` contains limits; `session_state.py` enforces legal phase transitions, step ceilings, repeated-failure counts, evidence-based no-progress windows, and reflect/escalate decisions. Full autonomous scheduling is intentionally absent. |
| ASK_PARENT | Escalate compactly when public contracts, transactions, concurrency, auth, data loss, conflicting evidence, or low confidence require a stronger decision. | Adopted in skill contracts. | `delegation`, `hermes-delegation`, and router execution contracts use bounded escalation; no new transport added. |
| Delegation | Use a TaskEnvelope and bounded ContextPack for internal workers; default depth 2, hard stop before recursive agent spawning; parallelize only independent work. | Adopted. | Existing delegation/Superpowers adaptations and `.harness/runtime.json`. Codex still has no Hermes transport by policy. |
| Checkpoints | Store compact goal/acceptance, done/todo/blocked, decisions, evidence, file hashes, verification, budgets, and next action. Never store raw reasoning, secrets, full chats, trees, or logs. Write temp+fsync+atomic replace and verify hashes on resume. | Adopted. | `scripts/session_state.py`, `session-checkpoint` skill, canonical `.ai/state/handoffs/`, generated `.ai/state/CURRENT.md`, legacy `tmp/local/sessions/` migration, and drift exit code 3. |
| Memory | Separate provider prompt cache, local retrieval cache, session checkpoint, project knowledge/wiki, and validated lessons. | Adopted as an architectural invariant. | Checkpoints and retrospective are separate. No embeddings or wiki database added without a measured need. |
| Self-improvement | Failure → root cause → prevention → evidence → scoped lesson candidate → regression evaluation → review → promotion. Never self-modify permissions, root policy, secrets, or security boundaries. | Adopted. Automatic promotion rejected. | `solution-retrospective`, `scripts/lesson_candidate.py`, and `.harness/runtime.json`. Candidates are content-addressed, eval-recorded, ignored, and manual-review-only. |
| Prompt caching | Keep policy/role/tools/selected skills/project conventions stable and deterministically ordered; append volatile task/tool/error data. Optimize verified cost, not raw prompt length. | Adopted as provider-neutral policy and manifest. | `.harness/runtime.json`, `cache-aware-context`, and `scripts/prompt_manifest.py`. Provider-specific controls stay in adapters; actual hit/cost claims still require client/provider usage telemetry. |
| Tool routing | Default-deny authority, narrow profiles, stable tool ordering. A skill cannot grant tools. Prefer native CLI for local developer operations. | Already adopted. | Existing sandbox/permissions, Makefile, and native tools. No Maven/Git/npm MCP proliferation. |
| MCP plane | Keep always-visible MCP small; discover/activate web, browser, CI, observability, database, and cloud only when needed. | Adapted to current project. | Current optional SearXNG/Crawl4AI/Playwright stack is retained; a new workspace/execution MCP would duplicate native client tools and is rejected. |
| Web retrieval | Use a safe gateway: discover URLs, extract known pages, use an interactive browser only for UI work; preserve source provenance and avoid sending private project data. | Already adopted. | `web-research-routing`; SearXNG → Crawl4AI → Playwright. Firecrawl remains intentionally excluded. |
| Code intelligence | Exact file/text search first, then LSP/symbols, AST/dependency graph, embeddings last. Cache content-addressed derived artifacts. | Adopted as policy. | Native `rg` is first-line. Graphify remains explicit/on-demand and does not replace exact search. |
| Reviews and verification | Independent evidence gate, targeted test first, broader affected checks when risk warrants, at most two correction cycles. | Already adopted. | `verification`, `code-reviewer`, Superpowers review skills. Router suppresses redundant review variants. |
| Domain skills | Install language/framework skills only when repository evidence justifies them. Preserve existing project toolchain rather than migrating to report examples. | Deferred by design. | This template currently has no Java/Maven/Angular/Ionic workload. Adding their detailed skills now would lower routing precision. |
| Wiki/diagrams | Update durable knowledge only from verified changes; use source-controlled text diagrams and incremental impact checks. | Optional/on demand. | Graphify, Obsidian Markdown/Bases/Canvas are catalog skills, not global context. |
| Evaluation | Measure task success, skill recall, irrelevant activations, context size, useful tool calls, loop stops, cache ratio, and cost per verified success. Test realistic positive and near-miss prompts. | Initial routing/session suite adopted. | `tests/test_skill_runtime.py`; broader model-level A/B evaluation needs configured clients/models and real usage telemetry. |
| Security | Project-root confinement, credential protection, provenance, explicit approvals, no automatic authority expansion. Treat downloaded reports/skills as untrusted input. | Already adopted and strengthened. | `AGENTS.md`, `project-safety`, router path-only reads, checkpoint path validation. |

## Why this differs from the reports' literal blueprints

The reports are architecture proposals for a broad multi-language platform.
This repository already supplies native file/search/process tools and has a
deliberate client-specific Hermes boundary. Implementing four local MCP servers,
a knowledge database, embeddings, a Go daemon, and dozens of language skills
before measured demand would duplicate capabilities, increase attack surface,
and contradict the reports' own “small kernel / minimal active capability”
principle.

The chosen path therefore preserves the valuable contracts while implementing
them in the smallest portable form: Markdown Agent Skills, JSON policy, and
Python standard-library CLIs. Later gates require a failing use case or metric,
not architectural enthusiasm alone.
