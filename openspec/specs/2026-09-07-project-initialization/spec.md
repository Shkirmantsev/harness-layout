# project-initialization Specification

## Purpose
Define safe, repeatable project initialization behavior for optional tooling
and privacy-preserving defaults.

## Requirements

### Requirement: initialization disables optional OpenSpec telemetry

The harness initialization command MUST set `telemetry.enabled` to `false`
through the installed OpenSpec CLI before completing project initialization.

#### Scenario: OpenSpec is available

Given `openspec` is available on the active `PATH`
When an operator runs `python harness.py init` or a Make target that delegates to
it
Then initialization runs `openspec config set telemetry.enabled false`
And continues with the remaining initialization steps only if that command
succeeds.

#### Scenario: initialization is repeated

Given OpenSpec telemetry is already disabled
When project initialization runs again
Then it reapplies the same setting without requiring operator input
And initialization remains successful.

### Requirement: OpenSpec remains optional

The harness MUST complete its core initialization path without invoking
OpenSpec when the CLI is unavailable.

#### Scenario: OpenSpec is absent

Given `openspec` is not available on the active `PATH`
When an operator runs project initialization
Then the harness reports that OpenSpec telemetry configuration was not run
And continues with core initialization.

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
