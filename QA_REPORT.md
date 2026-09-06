# Harness Layout v4.0.0 — Release QA Report

## Post-migration verification — 2026-09-07

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
