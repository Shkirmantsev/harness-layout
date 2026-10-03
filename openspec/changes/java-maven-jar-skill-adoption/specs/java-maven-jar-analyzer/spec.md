## ADDED Requirements

### Requirement: Catalog skill for Java/Maven/JAR analysis

The harness SHALL expose a routed catalog skill under
`.agents/skills/catalog/java-maven-jar-analysis/SKILL.md` that teaches the
agent how to answer dependency and JAR-introspection questions for Java and
Maven projects.

#### Scenario: skill is routed for a Java dependency question

- **GIVEN** an agent is asked to identify what a Java class depends on from its
  Maven coordinates
- **WHEN** `skill-router` evaluates the request against the catalog
- **THEN** `java-maven-jar-analysis` is returned in `required_skills`
- **AND** no tool permissions are added by the skill itself

#### Scenario: skill body references the MCP contract

- **WHEN** the agent reads the skill body
- **THEN** the body names both `jar_search` and `jar_api` MCP tools
- **AND** states that the tools may return `{"available": false, ...}` until a
  backing Java/JAR analyzer is enabled

#### Scenario: Gradle-only request does not route the Maven skill

- **GIVEN** an agent is asked only about a Gradle dependency graph
- **WHEN** `skill-router` evaluates the request
- **THEN** `java-maven-jar-analysis` is not returned in `required_skills`

### Requirement: Skill documents the fall-back strategy

The skill SHALL instruct the agent to fall back to native command-line tools
(`javap`, `jdeps`, `mvn dependency:tree`) whenever the MCP hooks are absent or
report that the backing Java/JAR analyzer is unavailable.

#### Scenario: MCP hook reports unavailable

- **GIVEN** a `jar_search` call returns `{"available": false, ...}`
- **WHEN** the agent follows the skill's guidance
- **THEN** the agent chooses one of `javap`, `jdeps`, or
  `mvn dependency:tree` rather than retrying the hook
- **AND** the agent records the chosen command in its evidence

### Requirement: Wiki describes the Java/JAR analyzer contract

The Wiki SHALL contain one interface page describing the `jar_search` and
`jar_api` MCP hooks and one module page describing the catalog skill.

#### Scenario: Wiki pages reference MCP source

- **WHEN** the agent retrieves `interfaces.java-jar-analyzer`
- **THEN** the page points to
  `tools/mcp/project-context-mcp/project_context_mcp/server.py` for both
  tools
- **AND** distinguishes the stubbed response from a future real-analyzer
  response

#### Scenario: Wiki pages use stable IDs

- **WHEN** `make wiki-validate` runs
- **THEN** the new pages contribute exactly two additional stable IDs
  (`interfaces.java-jar-analyzer`, `modules.java-maven-jar-analysis`)
- **AND** no broken internal links are introduced

### Requirement: Recommendation matrix reflects adoption

The *Domain skills* row of `docs/REPORT_RECOMMENDATION_MATRIX.md` SHALL be
updated from *Deferred by design* to *Adopted* and SHALL state a remaining
opt-in gate for any future analyzer-module addition.

#### Scenario: matrix is reviewed after the change

- **WHEN** an operator reads the *Domain skills* row
- **THEN** the row reports adoption of the catalog skill and Wiki pages
- **AND** it explicitly states that adding a real analyzer module requires a
  separate opt-in change

### Requirement: No breaking changes to MCP source

The change SHALL NOT modify `tools/mcp/project-context-mcp/` source. The
stubbed `jar_search` and `jar_api` responses SHALL remain byte-for-byte
identical to their pre-change form.

#### Scenario: MCP source untouched

- **WHEN** the change is committed
- **THEN** `git diff tools/mcp/project-context-mcp/` is empty
- **AND** the contract continues to advertise the optional analyzer hook
