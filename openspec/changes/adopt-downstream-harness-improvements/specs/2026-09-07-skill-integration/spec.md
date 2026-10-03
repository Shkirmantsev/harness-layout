## MODIFIED Requirements

### Requirement: local skill sync preserves integration-owned outputs

Local skill synchronization MUST copy only harness-owned core skills to the
project-local Claude Code and OpenCode skill directories and MUST NOT delete or
overwrite tool-owned OpenSpec or unrelated personal skills. Codex MUST continue
using canonical `.agents/skills/` discovery without writes to global skill paths.

#### Scenario: sync after multi-client OpenSpec initialization

- **GIVEN** OpenSpec skills exist in canonical and client-specific directories
- **WHEN** local harness skill synchronization runs
- **THEN** the four harness core skills are refreshed in both project-local mirrors
- **AND** the OpenSpec-generated and personal skills remain present and tool-owned
- **AND** no user-global Codex directory is modified.
