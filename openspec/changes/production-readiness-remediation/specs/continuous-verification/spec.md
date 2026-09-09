## ADDED Requirements

### Requirement: Deterministic full verification

The full harness gate SHALL run successfully from a clean supported environment
and SHALL use compatible pinned or constrained dependencies for protocol-level
integration tests.

#### Scenario: project-context MCP initialize handshake

- **GIVEN** the declared project-context dependencies are installed
- **WHEN** the integration test initializes the stdio MCP server
- **THEN** the server responds within the test deadline

### Requirement: Strict OpenSpec validation

The harness OpenSpec check SHALL validate every current spec and active change in
strict mode, in addition to validating the selected schema.

#### Scenario: malformed active change exists

- **WHEN** the full harness gate runs
- **THEN** strict OpenSpec validation fails and identifies that change

### Requirement: Verifiable artifact manifest

The repository SHALL provide deterministic commands to regenerate and verify its
artifact manifest. Verification SHALL fail for stale, missing, or unexpected
manifest-owned artifacts.

#### Scenario: tracked artifact changes

- **WHEN** a manifest-owned file changes without regeneration
- **THEN** the manifest verification command fails

### Requirement: Continuous integration gate

The repository SHALL run portable tests and the full Linux harness gate in CI on
every proposed change and protected-branch update.

#### Scenario: change breaks a supported workflow

- **WHEN** CI evaluates the change
- **THEN** the corresponding required job fails before merge

### Requirement: Current documentation evidence

Documentation links SHALL resolve within the repository, and QA reports SHALL
distinguish historical evidence from current reproducible results.

#### Scenario: QA report states a passing total

- **WHEN** a reader follows the documented verification command
- **THEN** its current expected result and environment are stated
- **AND** obsolete totals are not presented as current evidence
