# Design: Java/Maven/JAR analyzer skill adoption

## Architectural fit

The current harness keeps four skills directly discoverable and routes every
other capability through a deterministic catalog under
`.agents/skills/catalog/`. A new language skill therefore belongs in the
catalog, not in the always-loaded core. This matches the
`adr/0001-separate-core-and-integration-skill-ownership` decision and lets the
harness decide at routing time whether the request actually requires Java/Maven
analysis.

The MCP hook surface is owned by `project-context-mcp/server.py`, which already
exposes the optional `jar_search` and `jar_api` tools. We treat those tools as
the **stub contract** and leave their real implementation as a future change.
The skill therefore has to:

- recognize the contract's stub response and tell the agent to use native
  tooling instead;
- avoid guessing any future real-analyzer response fields that this change
  does not define;
- remain useful even if the hooks are never enabled.

## What we mirror from the previous-layout pack

`tmp/local/previous-layout/erp-agent-skill-pack-powershell51-fix-v1.9.2/`
ships:

- a PowerShell lifecycle script (`tools/mcp/manage-erp-context-mcp.ps1`),
- an agent-facing note (`docs/agent/powershell-compatibility.md`),
- an MCP package that previously included `erp_context_mcp/java.py` and
  `erp_context_mcp/maven.py`.

We use only the **shape**:

- **Agent-facing note → Wiki page.** The previous project documented runtime
  constraints in `docs/agent/`. The current harness documents durable runtime
  knowledge in `.ai/wiki/`. We mirror by writing Wiki pages under
  `interfaces/` and `modules/` instead of `docs/agent/`.
- **Lifecycle script → catalog skill.** The previous project's
  `manage-erp-context-mcp.ps1` was an out-of-band controller. The current
  harness replaces such controllers with catalog skills that the agent can read
  on demand. We add `java-maven-jar-analysis` as the catalog skill.
- **MCP analyzer modules → future change, not this one.** The previous project
  shipped `java.py` / `maven.py` next to the MCP server. The current harness's
  MCP server already exposes the contract; we leave the implementation as a
  later, opt-in change. Adding it here would smuggle in toolchain changes that
  the user explicitly asked to defer.

## Module map

| Layer | New artifact | Mirror source in previous project |
|---|---|---|
| Catalog skill | `.agents/skills/catalog/java-maven-jar-analysis/SKILL.md` | `tools/mcp/manage-erp-context-mcp.ps1` (controller role) |
| Wiki interface | `.ai/wiki/interfaces/java-jar-analyzer.md` | `docs/agent/powershell-compatibility.md` (agent-facing note role) |
| Wiki module | `.ai/wiki/modules/java-maven-jar-analysis.md` | (no direct equivalent; explains the catalog skill) |
| OpenSpec spec | `openspec/changes/java-maven-jar-skill-adoption/specs/java-maven-jar-analyzer/spec.md` | (new — current harness requires OpenSpec-tracked behavior) |
| Recommendation matrix row | `docs/REPORT_RECOMMENDATION_MATRIX.md` (single row update) | (new — overrides the previous deferral) |
| Deterministic routing | `scripts/skill_router.py` + `evals/routing/cases.json` + `tests/test_skill_runtime.py` | (new — current harness requires explicit signals and regression evidence) |

## Boundaries

- The skill does **not** grant new MCP tools. The harness tool authority remains
  default-deny; the agent continues to use `jar_search` / `jar_api` only when
  the project-context MCP is configured for the active client.
- The skill does **not** fetch JARs from Maven Central or any other registry.
  Network calls remain the operator's responsibility.
- The skill does **not** modify `project-context-mcp/server.py`. The stub
  response stays a contract; replacing it with a real analyzer is a separate,
  explicitly opt-in change.
- The previous-layout patch under `/tmp/opencode/prev-layout-inspect/` is never
  copied into the repository. It exists only as evidence during this change.

## Failure modes

- If `kb_refresh` is not run after the Wiki pages land, `kb_search` keeps
  returning the stale index. The canonical Markdown remains available
  directly, and project initialization or `python harness.py index` rebuilds
  the disposable index.
- If the MCP server or its Java hooks are unavailable, the skill proceeds
  directly to native CLI fallback. It never assumes the hook is wired up.
- If a future change replaces the stub with a real analyzer, the skill remains
  valid because its body describes the contract, not the implementation.

## Verification

The change is complete when:

- `make wiki-validate` is green,
- `make skills-check` reports the new skill as catalog-only,
- `python harness.py check` runs the OpenSpec strict validator on the new
  delta and passes,
- `python harness.py openspec-check` reports the new change,
- `python harness.py manifest-check` accepts the new release artifacts,
- and `git diff --stat` shows the eight new feature files plus the bounded
  router, routing-evaluation, regression-test, and matrix edits.
