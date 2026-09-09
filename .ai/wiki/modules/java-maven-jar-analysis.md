---
id: modules.java-maven-jar-analysis
title: Java/Maven/JAR analysis catalog skill
kind: module
status: active
summary: Catalog skill that teaches the agent to recognize the MCP jar_search/jar_api stub contract, call it when wired up, and fall back to native javap/jdeps/mvn dependency:* when no backing analyzer is enabled.
sourceRefs:
  - .agents/skills/catalog/java-maven-jar-analysis/SKILL.md
  - tools/mcp/project-context-mcp/project_context_mcp/server.py
maintenance:
  mode: authored
---

# Java/Maven/JAR analysis catalog skill

This page describes the routed catalog skill that handles Java/Maven
dependency and JAR-introspection questions. It does **not** describe how the
underlying analyzer works; the analyzer itself is a future, opt-in addition.

## Ownership

- Catalog path: `.agents/skills/catalog/java-maven-jar-analysis/SKILL.md`
- Adopted in: `openspec/changes/java-maven-jar-skill-adoption/`
- Contract: [Java/JAR analyzer MCP hooks](../interfaces/java-jar-analyzer.md)

The skill lives in the on-demand catalog because Java/Maven analysis is
language-specific and the harness core intentionally stays language-neutral
(see [ADR: Separate harness core and integration skill ownership](../adr/0001-separate-core-and-integration-skill-ownership.md)).

## Routing triggers

`scripts/skill_router.py` returns this skill when the task matches a specific
analysis signal:

- a Maven project, dependency, dependencies, or coordinate;
- JAR contents or API inspection;
- `pom.xml`, `javap`, `jdeps`, or `mvn dependency:tree`.

Bare "Java" wording and Gradle-, Bazel-, sbt-, or Ant-only requests do **not**
activate it. Those build systems require their own catalog skills and are out
of scope here.

## Behavior

1. Identify either a Maven project or an explicit local JAR/class target.
2. If `jar_search` is in the active MCP toolset, recognize whether its backing
   analyzer is enabled by probing with a small query.
3. If `available: true`, route further questions through `jar_search` and
   `jar_api`.
4. If the tool is absent or returns `available: false`, fall back to:
   - `javap -classpath <jar> -p -c <class>` for class structure (no network),
   - `jdeps -v -R <jar>` for transitive package dependencies,
   - `mvn -o dependency:tree` for the full dependency graph (offline first).
5. If neither path answers the question, ask the operator to enable a backing
   Java/JAR analyzer or to provide the artifact path explicitly.

## What it does not do

- It does not grant new MCP tools.
- It does not modify the MCP source under `tools/mcp/project-context-mcp/`.
- It does not download artifacts from Maven Central without explicit operator
  approval.
- It does not cover Gradle/Bazel/sbt/Ant dependency graphs.

## Boundaries with other skills

- `skill-router` decides *whether* to load this skill; this skill decides
  *what to do* once loaded.
- `repo-recon` reports whether the project has a `pom.xml`; combined with this
  skill's routing rules, the agent can avoid running Maven tooling against
  non-Maven Java projects.
- `code_symbol` answers source-level symbol questions regardless of language;
  for binary class questions the agent should prefer this skill.

## Evidence

- Skill body: `.agents/skills/catalog/java-maven-jar-analysis/SKILL.md`
- MCP source: `tools/mcp/project-context-mcp/project_context_mcp/server.py:67-75`
- Hook contract: [interfaces/java-jar-analyzer.md](../interfaces/java-jar-analyzer.md)
- Adoption proposal: `openspec/changes/java-maven-jar-skill-adoption/proposal.md`
- Matrix row: `docs/REPORT_RECOMMENDATION_MATRIX.md` (*Domain skills*)
