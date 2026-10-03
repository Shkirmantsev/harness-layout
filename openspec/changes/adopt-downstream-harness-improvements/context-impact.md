# Context impact

## Create

- `project.downstream-harness-adoption`: import provenance, current behavior and
  rejected adaptations in `.ai/wiki/project/downstream-harness-adoption.md`.
- `openspec/specs/portable-harness-tooling/spec.md`: accepted behavior after verification.

## Update

- `openspec/specs/skill-integration/spec.md`: OpenCode core mirror alongside Claude.
- `.ai/wiki/INDEX.md`: narrow navigation link to the adoption node.
- `docs/SKILLS.md`, `docs/CONFIGURATION.md`, `docs/THIRD_PARTY_SKILLS.md`,
  `docs/README.md`, `openspec/README.md`: routing fallback, ownership, optional
  Context7 setup, provenance and semantic change identifiers.
- Skill ownership ADR: verification covers both project-local mirrors; the
  ownership decision itself remains unchanged.
- Artifact manifest: include intended new source files and exclude generated
  client mirrors consistently with existing Claude/OpenSpec outputs.

## Unaffected

Donor domain Wiki/ADRs/specifications, Java/POM, application database and JSON
contracts, certificates, runtime state and credentials. Existing harness JSON
schemas, MCP implementation, optional integrations and conventions already match
or remain authoritative here.

## Generated state

Use the session-state CLI for handoff updates. Rebuild the disposable local Wiki
index and sync core mirrors; do not import donor machine state or index databases.

Migrate the existing session-handoff spec into `session-handoff/spec.md` and
update current navigation/source references; preserve its requirement behavior.
