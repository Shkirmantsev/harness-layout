---
id: interfaces.java-jar-analyzer
title: Java/JAR analyzer MCP hooks
kind: interface
status: active
summary: Optional jar_search and jar_api tools in project-context MCP that expose stub responses for Java/Maven inspection while a backing analyzer remains an opt-in future addition.
sourceRefs:
  - tools/mcp/project-context-mcp/project_context_mcp/server.py
maintenance:
  mode: authored
---

# Java/JAR analyzer MCP hooks

The project-context MCP server exposes two optional tools for Java and Maven
introspection. They live next to the always-available `kb_*`, `spec_context`,
and `code_symbol` tools but are explicitly marked as optional specialization
hooks.

## Source of truth

Both hooks are declared in
`tools/mcp/project-context-mcp/project_context_mcp/server.py:67-75`. Their
docstrings call them "Optional Java specialization hook" and state they are
"intentionally not part of the generic core."

## `jar_search(query)`

```python
@mcp.tool()
def jar_search(query: str) -> dict:
    """Optional Java specialization hook. Returns guidance when no Java/JAR index plugin is installed."""
    return {"query": query, "available": False,
            "message": "Install/enable a Java/JAR analyzer skill for deterministic Maven/JDK dependency inspection."}
```

Inputs:

- `query` — free-form string the analyzer would search against (artifact IDs,
  class FQNs, Maven coordinates, etc.).

Stub response (current, pre-analyzer behavior):

```json
{
  "query": "<echoed>",
  "available": false,
  "message": "Install/enable a Java/JAR analyzer skill for deterministic Maven/JDK dependency inspection."
}
```

## `jar_api(gav, class_name)`

```python
@mcp.tool()
def jar_api(gav: str, class_name: str) -> dict:
    """Optional Java specialization hook; intentionally not part of the generic core."""
    return {"gav": gav, "class": class_name, "available": False,
            "message": "Use the optional Java/JAR analyzer skill (source JAR, javap, jdeps) when enabled."}
```

Inputs:

- `gav` — Maven coordinate in the form `groupId:artifactId:version`.
- `class_name` — fully qualified class name within the artifact.

Stub response:

```json
{
  "gav": "<echoed>",
  "class": "<echoed>",
  "available": false,
  "message": "Use the optional Java/JAR analyzer skill (source JAR, javap, jdeps) when enabled."
}
```

## Contract vs implementation

The MCP server ships the **stub contract only**. The two responses above are
the complete documented shape for the current implementation. A future real
analyzer may return `available: true`, but its additional result fields are not
defined by this change and callers must not guess them. Adding that analyzer
and defining its response schema requires a future, explicitly opt-in change
(see the *Domain skills* row of `docs/REPORT_RECOMMENDATION_MATRIX.md`).

Until then, callers must treat `available: false` as "this hook is absent"
and fall back to native tools such as `javap`, `jdeps`, or
`mvn dependency:tree`. See the
[Java/Maven/JAR analysis module](../modules/java-maven-jar-analysis.md) for
the catalog skill that owns those fall-back rules.

## Why this is a hook, not a tool

The harness tool routing rule is default-deny. A skill cannot grant new
tools, and the MCP server is configured per client. Making Java analysis a
specialization hook rather than a default tool keeps the generic core small
and keeps a project that does not build with Maven from paying any startup
cost for Java tooling.

## Operational behavior

- Both calls are synchronous, deterministic, and perform no network or file
  I/O in the current implementation.
- Inputs are echoed without validation; callers must not treat them as proof
  that a coordinate, class, or artifact exists.
- The stubs have no authentication, retry, ordering, or idempotency concerns.
  Access remains controlled by whether project-context MCP is configured for
  the active client.
- Consumers are agent clients using project-context MCP. There is no producer
  beyond the local server process and no persisted analyzer state.

## Evidence

- Source: `tools/mcp/project-context-mcp/project_context_mcp/server.py`
- Adoption change: `openspec/changes/java-maven-jar-skill-adoption/`
- Routing row: `docs/REPORT_RECOMMENDATION_MATRIX.md` (*Domain skills*)
- Catalog skill: `.agents/skills/catalog/java-maven-jar-analysis/SKILL.md`
