# Context impact

## Knowledge to create

- `.ai/wiki/adr/0001-separate-core-and-integration-skill-ownership.md`

## Knowledge to update

- `docs/SKILLS.md`
- `docs/THIRD_PARTY_SKILLS.md`
- `.ai/wiki/INDEX.md`
- `.ai/wiki/architecture/system-overview.md`

## Knowledge to review for staleness

- `docs/REPORT_RECOMMENDATION_MATRIX.md`

## Affected implementation

Modules/paths:

- `scripts/sync_skills.py`
- `tests/test_skill_runtime.py`
- OpenSpec-generated `.agents/skills/openspec-*`, `.claude/`, and `.opencode/`

Primary symbols/interfaces:

- `exposed_skills()`
- `local()`
- `remote()`
- `check()`

## ADR impact

- Record the ownership boundary between harness core skills, the optional
  catalog, and integration-generated top-level skills.

## Acceptance criteria

- [ ] Relevant Wiki pages reflect shipped implementation.
- [ ] Generated local context index was refreshed.
- [ ] Links and stable knowledge IDs validate.
- [ ] Spec/implementation mismatches are resolved or explicitly documented.
