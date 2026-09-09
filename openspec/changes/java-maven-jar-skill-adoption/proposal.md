# Java/Maven/JAR analyzer skill adoption

## Why

The harness exposes optional `jar_search` and `jar_api` hooks in
`tools/mcp/project-context-mcp/project_context_mcp/server.py` so projects that
ship Java artifacts can answer "what does this class need from its Maven
dependencies?" without re-implementing a language-specific analyzer. Today the
hooks return `{"available": false, "message": "Install/enable a Java/JAR
analyzer skill for deterministic Maven/JDK dependency inspection."}`. There is
no catalog skill that explains when the hooks are usable, no Wiki page that
describes the contract, and the recommendation matrix explicitly defers
language-specific skills. Operators investigating a Java/Maven codebase cannot
follow a documented path; they either ignore the hooks or improvise.

A previous project (`tmp/local/previous-layout/erp-agent-skill-pack-*`) shipped
an `erp_context_mcp/java.py` and `erp_context_mcp/maven.py` analyzer pair
together with a PowerShell lifecycle script and an agent note under
`docs/agent/`. We use that pack as a *layout reference only*: the new artifacts
must fit the current harness's separate-core / catalog-on-demand ownership
boundary (see `adr/0001-separate-core-and-integration-skill-ownership`).

## What Changes

- Add one routed catalog skill `.agents/skills/catalog/java-maven-jar-analysis/SKILL.md`
  that teaches the agent how to call `jar_search` / `jar_api`, how to fall back
  to native `javap` / `jdeps` / `mvn dependency:*` when the hooks are stubbed,
  and when to ask for a backing analyzer to be enabled.
- Add two Wiki pages:
  - `.ai/wiki/interfaces/java-jar-analyzer.md` — the `jar_search` / `jar_api`
    contract, inputs, current stub responses, undefined future-response
    boundary, and reference back to the MCP source.
  - `.ai/wiki/modules/java-maven-jar-analysis.md` — the catalog skill: routing
    triggers, dependencies, and which other Wiki/ADR nodes it relates to.
- Add the corresponding OpenSpec spec delta
  `openspec/changes/java-maven-jar-skill-adoption/specs/java-maven-jar-analyzer/spec.md`
  describing observable behavior of the new skill + Wiki + matrix update.
- Update the existing "Domain skills" row in
  `docs/REPORT_RECOMMENDATION_MATRIX.md` from *Deferred by design* to *Adopted*
  with explicit reasoning and a remaining gate that any later analyzer-module
  addition must remain opt-in.
- Do not modify `tools/mcp/project-context-mcp/` source; the MCP stub remains a
  contract-only hook. Do not add a real analyzer module in this change; that
  would expand the project's toolchain beyond its current capability surface
  and is out of scope here.
- Extend the deterministic routing signals and regression coverage in
  `scripts/skill_router.py`, `evals/routing/cases.json`, and
  `tests/test_skill_runtime.py` so Maven/JAR questions load the new skill while
  a Gradle-only near miss does not.

## Scope

### In scope

- `.agents/skills/catalog/java-maven-jar-analysis/` (new skill + optional
  references).
- `.ai/wiki/interfaces/java-jar-analyzer.md` (new).
- `.ai/wiki/modules/java-maven-jar-analysis.md` (new).
- `openspec/changes/java-maven-jar-skill-adoption/` (new change folder).
- `docs/REPORT_RECOMMENDATION_MATRIX.md` (single row update).
- `scripts/skill_router.py`, `evals/routing/cases.json`, and
  `tests/test_skill_runtime.py` (one bounded routing rule plus direct and
  aggregate positive/negative coverage).
- `ARTIFACT_MANIFEST.sha256` (regenerated release inventory for the adopted
  source, tests, specifications, and documentation).

### Out of scope

- Adding `java.py` / `maven.py` modules to
  `tools/mcp/project-context-mcp/project_context_mcp/`.
- Re-wiring the MCP server to load a real analyzer plugin.
- Sub-dependency class extraction logic, source JAR fetching, or any
  network-based Maven Central calls.
- Other language skills (Angular/Ionic/Kotlin-only tooling, etc.) — each
  adoption must be justified by a separate change.
- Editing the previous-layout patch file. It is unpacked under `/tmp/opencode`
  and used only as a structural reference, never as a committed source.

## Success criteria

1. The new catalog skill is reachable via `skill-router` and renders as
   Markdown with stable frontmatter, a one-line description, and a body that
   references the `jar_search` and `jar_api` MCP tools by name.
2. The two new Wiki pages exist under `interfaces/` and `modules/`, both have
   unique stable frontmatter `id` values, and both link to the MCP source and
   to each other where useful.
3. `make wiki-validate` reports no broken IDs or links introduced by these
   additions.
4. `make skills-check` reports the new catalog skill as discoverable without
   disturbing the fixed core skill list.
5. `python harness.py check` (or `make check`) reports the same set of
   pre-existing passes plus the new spec under the strict OpenSpec validator.
6. `docs/REPORT_RECOMMENDATION_MATRIX.md` no longer defers Java/Maven skills
   and states the remaining gate clearly.
7. `python harness.py manifest-check` passes with the new release artifacts.
8. No file outside the listed new artifacts, matrix row, router/evaluation
   support, and generated artifact manifest was modified.
