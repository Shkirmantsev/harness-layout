# Design

## Current state

`make init` and `make init-mcp` delegate to `python harness.py init`. The Python
entry point initializes the environment, Wiki index, core skill copies, optional
MCP environment, and client configuration, but it does not configure OpenSpec's
global telemetry preference. OpenSpec is intentionally optional to the core
harness.

## Proposed design

Add a small `configure_openspec()` lifecycle helper in `harness.py` and call it
from `cmd_init()` after the local environment is prepared. The helper checks the
active `PATH` with `shutil.which("openspec")`:

- when present, run `openspec config set telemetry.enabled false` through the
  existing fail-fast command wrapper;
- when absent, print an explicit `NOT RUN` message and return successfully.

Keeping the behavior in the cross-platform Python entry point automatically
covers both Make targets without duplicating shell logic or making Make the
source of truth.

## Affected modules / interfaces

- `harness.py`: initialization orchestration and optional CLI boundary.
- `tests/test_harness_init.py`: executable-path and absent-tool behavior.
- `docs/QUICKSTART.md` and `docs/CONFIGURATION.md`: operator-visible global
  side effect and re-enable guidance.

## Data / persistence / concurrency impact

The only persistent data change is OpenSpec's user-level configuration, owned by
the OpenSpec CLI. No repository secrets, application data, network services, or
concurrent processes are introduced.

## Compatibility and migration

Core initialization continues unchanged when OpenSpec is absent. When present,
an OpenSpec configuration failure stops initialization rather than claiming the
privacy default was applied. The command is idempotent. Existing users who want
telemetry may run `openspec config set telemetry.enabled true` after harness
initialization.

## Risks and rollback

The setting is user-global rather than project-local, so the documentation must
make its scope explicit. Rollback removes the helper call and lets users choose
their OpenSpec default manually; the persisted setting can be reversed with the
OpenSpec CLI. This operational default does not alter the harness architecture,
so no ADR is required.
