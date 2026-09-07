# Proposal

## Why

Projects created from this layout should not begin sending OpenSpec usage
telemetry merely because the optional CLI is present. The privacy preference
should be applied consistently by the normal cross-platform initialization
entry point instead of relying on every operator to remember a separate global
configuration command.

## What Changes

- During `python harness.py init` (and therefore `make init`/`make init-mcp`),
  disable OpenSpec telemetry when the `openspec` executable is available.
- Keep OpenSpec optional: initialization continues without error when the CLI is
  absent.
- Document the global configuration side effect and cover both branches with
  focused tests.

## Goal

Make telemetry opt-out the safe default for new projects initialized from the
harness while preserving vendor-neutral operation without OpenSpec.

## Affected capabilities

- Project initialization
- Optional OpenSpec integration

## Compatibility / migration impact

The setting is global to the active user's OpenSpec installation, so one
project initialization affects later OpenSpec use by that user. Users who want
telemetry can explicitly re-enable it after initialization. Environments
without OpenSpec retain the existing successful initialization path.

## Related knowledge

- `kb://architecture.system-overview`
- `docs/QUICKSTART.md`
- `docs/CONFIGURATION.md`
