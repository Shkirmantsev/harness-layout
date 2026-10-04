# Enforce the current project boundary

## Why

Private provenance in reusable documentation and task state can misdirect agents.
A copied .env also previously accepted a different repository as PROJECT_ROOT.
The user explicitly requires immediate removal and current-project isolation.

## What Changes

- Redact private provenance in docs, skills and one historical archive.
- Remove a completed historical private checkpoint through the state CLI.
- Bind root selection to the current harness, rejecting external paths before setup/configuration.
- Ignore implicit PROJECT_ROOT environment overrides in the standalone MCP server; explicit --root remains available.
- Document safe template copying and regenerate current local indexes/mirrors.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `2026-09-07-project-initialization`: enforce current-project setup/configuration.

## Impact

Harness root resolution, environment bootstrap, client generation, safety guidance,
provenance and historical state maintenance. Stale copied configuration now fails
closed. No product logic changes and no foreign repository is accessed.
