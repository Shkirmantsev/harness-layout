## ADDED Requirements

### Requirement: initialization and clients remain in the current project

The reusable harness SHALL bind configured PROJECT_ROOT to the repository
containing the harness. Auto, empty and current-directory values SHALL select
that repository. A copied external root SHALL fail before setup or client
configuration, including when project-context MCP is disabled. Rejection SHALL
occur before following a foreign path. Historical provenance SHALL not authorize
cross-project access. Public template content SHALL omit private project names
and personal workspace paths. Disposable configs and caches SHALL be regenerated
for the current project after copying the tracked template.

#### Scenario: copying an environment from another project

- **WHEN** a copied .env selects an external PROJECT_ROOT
- **THEN** initialization and client configuration fail with instructions to use PROJECT_ROOT=auto
- **AND** no foreign project is inspected or selected.

#### Scenario: initializing a fresh template

- **WHEN** PROJECT_ROOT is auto or identifies the current harness repository
- **THEN** setup and generated client configuration use that repository only.
