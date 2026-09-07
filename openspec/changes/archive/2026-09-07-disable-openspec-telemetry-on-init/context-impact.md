# Context impact

## Knowledge to create

- none

## Knowledge to update

- `docs/QUICKSTART.md`
- `docs/CONFIGURATION.md`

## Knowledge to review for staleness

- `README.md`
- `Makefile`
- `kb://architecture.system-overview`

## Affected implementation

Modules/paths:

- `harness.py`
- `tests/test_harness_init.py`

Primary symbols/interfaces:

- `configure_openspec()`
- `cmd_init()`

## ADR impact

- none; this is a reversible initialization default at an existing optional
  integration boundary.

## Acceptance criteria

- [ ] Relevant operator documentation reflects the global setting.
- [ ] Generated local context index was refreshed.
- [ ] Links and stable knowledge IDs validate.
- [ ] Spec/implementation mismatches are resolved or explicitly documented.
