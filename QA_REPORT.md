# Harness Layout v4.0.0 — Release QA Report

## Current verification — 2026-09-09

This section is the current reproducible evidence. Older migration snapshots are
retained below as history and are not current release claims.

| Check | Current result |
|---|---|
| `python3 harness.py check` | **PASS** — configuration, state, Wiki, strict OpenSpec, 69 isolated root tests, 5 project-context tests including stdio, and 331-file manifest |
| `python3 -m unittest discover -s tests -v` | **PASS** — 69 tests |
| Project-context stdio integration | **PASS** — MCP 1.30.0 + AnyIO 4.10.0 using Trio server backend |
| `openspec validate --all --strict` | **PASS** — 3 items |
| Hermes sidecar unit tests | **PASS** — 5 tests |
| Hermes compatibility patch check | **PASS** — exact-revision patches validate for upstream `4f2254350` and legacy worker `981101239`; modified sources compile |
| Live Hermes health/model/sidecar | **PASS** — API, model advertisement, hardened sidecar, and exact-root policy active |
| Live resolver-scoped approval capability | **PASS** — worker advertises `resolver_scoped_run_approvals`; generated OpenCode module surfaced the redacted guarded command and resumed the exact run for `deny`; `once` was also proven before the metadata-only extension |

The stdio integration uses a Trio backend because the SDK's asyncio stdio
memory-stream path reproduced a deterministic initialize deadlock in this
environment. The sandbox blocks Trio's internal wakeup socketpair, so the final
local integration/full-gate evidence was collected outside that sandbox; CI and
normal hosts do not have that restriction.

OpenCode→Hermes delegation is enabled with explicit resolver-scoped approvals.
`approvals.unattended_mode: approve` remains prohibited as a workaround.

## Historical migration evidence — 2026-09-07

### Post-migration verification

The following results supersede the original build-environment limitations below:

- Project-local MCP installation: PASS with MCP SDK 2.1.1.
- `python3 harness.py check`: PASS, 56 tests including an actual stdio MCP session (initial post-migration check).
- Wiki index rebuild and link validation: PASS.
- Client configuration regeneration and core skill synchronization: PASS.
- OpenSpec CLI validation: NOT RUN; executable is not installed.
- Optional service health checks: PASS after explicit user approval and starting the existing stopped local containers. LiteLLM, Hermes native API/model authentication, Claude Hermes sidecar, SearXNG MCP, and Crawl4AI MCP returned HTTP 200. Remote inference was not submitted.

Documentation follow-up connects the root README, agent contract, Wiki index,
engineering conventions, and OpenSpec artifact rules. `docs/README.md` covers all
documentation pages and distinguishes historical references. `docs/PROJECT_STRUCTURE.md`
maps canonical inputs, consumers, generated output, and extension directories.
Two navigation regressions cover reachability and entry-point link targets.
Follow-up `python3 harness.py check`: PASS, all 58 tests including those navigation
regressions and the live local MCP session. Wiki validation and skill sync also pass.

Automatic handoff follow-up adds durable structured task checkpoints, a generated
current-task view, ID-free resume, legacy checkpoint promotion, active-task
replacement protection, completion invariants, and a consistency gate in the
normal harness check. The adopted behavior is documented in OpenSpec and the Wiki.
Final `python3 harness.py check`: PASS, all 63 tests including the installed MCP
stdio integration. The first restricted-sandbox MCP attempt timed out; the required
outside-sandbox rerun passed.

Post-migration fixes pin client MCP launches to the configured repository, preserve
the last index on rebuild failure, retain numeric section order, reject external
Wiki/source symlinks, constrain OpenSpec change lookup, and escape quoted executable
paths in Codex TOML. Editable-install metadata is ignored. Architecture and project
map Wiki pages now describe the repository. The local quality gate uses the installed
MCP environment when available and otherwise reports the stdio test as skipped.

The manifest describes the corrected working tree, not the original ZIP byte-for-byte.

## Release intent

This release converts the previous harness into a reusable, vendor-neutral project layout centered on bounded context retrieval, a Markdown-first LLM Wiki, OpenSpec-driven behavioral change, shared skills, and optional client/runtime adapters.

## Compatibility decisions

- OpenCode V1-generation configuration is the default (`OPENCODE_CONFIG_GENERATION=v1`).
- OpenCode V2 is an explicit beta opt-in (`OPENCODE_CONFIG_GENERATION=v2`).
- V1 and V2 client files are generated independently; mixed schemas are rejected by tests.
- Claude Code and Codex use the same portable project contract and project-context MCP.
- Hermes, LiteLLM, local models, SearXNG, Crawl4AI and Playwright remain optional.

## Validation performed

The release tree passed `python harness.py check` before final artifact sanitization:

- configuration validation: PASS;
- Markdown Wiki validation: PASS (zero issues);
- project OpenSpec schema structural validation: PASS;
- repository test modules: PASS;
- project-context core/index/search tests: PASS;
- OpenCode V1 generation/parsing tests: PASS;
- OpenCode V2 generation/parsing tests: PASS;
- Python source compilation used during implementation: PASS.

## Environment-limited checks

The official OpenSpec CLI was not installed in the build environment, so CLI-level `openspec schema validate production-sdd` was not executed here. The repository's structural validator passed.

The isolated build environment could not download Python packages from the internet, so creation of the MCP virtual environment could not be completed. The project-context MCP source, dependency-free core indexer/search implementation, current MCP v2 API shape, and tests were validated. On a connected machine run `python harness.py mcp-install`.

## Artifact hygiene

Before packaging, generated/runtime files, local secrets, client-generated configurations, local indexes, virtual environments, Python bytecode/cache directories and IDE/repository metadata are removed. Canonical source files and `.gitkeep` placeholders are retained.
