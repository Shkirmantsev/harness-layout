## MODIFIED Requirements

### Requirement: current specifications participate in strict validation

Current specifications SHALL live at `openspec/specs/YYYY-MM-DD-domain-capability/spec.md`.
The harness SHALL reject loose Markdown specifications rather than silently
allowing the CLI to omit them. Accepted dated capability identifiers SHALL remain stable on subsequent
updates. Migration from undated identifiers SHALL preserve the original Git
acceptance date and update live links and active delta paths.

#### Scenario: a loose current specification exists

- **WHEN** the harness OpenSpec gate finds Markdown directly under `openspec/specs/`
- **THEN** it fails and identifies the expected capability-directory layout.
