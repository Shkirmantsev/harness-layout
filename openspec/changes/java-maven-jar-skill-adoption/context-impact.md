# Context impact: Java/Maven/JAR analyzer skill adoption

## Knowledge nodes

### Create

- `.ai/wiki/interfaces/java-jar-analyzer.md`
  - `id: interfaces.java-jar-analyzer`
  - `kind: interface`
  - Describes the `jar_search` and `jar_api` MCP tools, their current stub
    responses and undefined future-response boundary, and points back to
    `tools/mcp/project-context-mcp/project_context_mcp/server.py:67-75`.
- `.ai/wiki/modules/java-maven-jar-analysis.md`
  - `id: modules.java-maven-jar-analysis`
  - `kind: module`
  - Describes the new catalog skill, its routing triggers, and its relationship
    to the interface page above.

### Update

- `.ai/wiki/INDEX.md` (only if and when a follow-up change decides to surface
  the new pages in *Start here*; this change does not edit `INDEX.md`).
- `docs/REPORT_RECOMMENDATION_MATRIX.md`, the *Domain skills* row only, to
  reflect adoption and the remaining opt-in gate for any future analyzer module.

### Invalidate

- None. No existing Wiki node contradicts the new content; the previous matrix
  row simply becomes outdated and is updated in the same change.

## Specifications

### Create

- `openspec/changes/java-maven-jar-skill-adoption/specs/java-maven-jar-analyzer/spec.md`
  describing the catalog skill's observable behavior: routing triggers,
  fall-back strategy, contract reference, and matrix linkage.

### Update

- None. The harness's current specs (`openspec/specs/project-initialization`,
  `openspec/specs/session-handoff.md`, `openspec/specs/skill-integration`) do
  not mention Java/Maven and need no edit.

## ADRs

### Create

- None. The existing `adr/0001-separate-core-and-integration-skill-ownership`
  already governs where new language skills belong (the catalog, not the
  core). The new skill complies; no new decision is required.

### Update

- None.

## Source/config files

- Update `scripts/skill_router.py` with one deterministic signal for the new
  catalog skill.
- Update `evals/routing/cases.json` with one positive Maven case and one
  Gradle-only near miss.
- Update `tests/test_skill_runtime.py` with a direct positive/negative routing
  assertion so aggregate recall cannot hide a regression in the new skill.
- Do not edit `tools/`, `harness.py`, `Makefile`, or `.harness/`; the MCP stub
  remains unchanged.

## Generated/index artifacts

- Regenerate the tracked `ARTIFACT_MANIFEST.sha256` after all intended feature
  files are selected. Session state remains excluded by manifest policy.
- After Wiki pages land, `python harness.py index` (or `make wiki-index`) must
  rebuild the disposable SQLite FTS index under
  `tmp/local/project-context/knowledge.db` so `kb_search` returns the new
  nodes. This change verifies the rebuild locally and does not commit the
  generated index.

## Verification impact

- `make wiki-validate` must report no broken stable IDs or local links
  introduced by the new pages.
- `make skills-check` must report the catalog isolation contract is still
  intact (the new skill sits under `catalog/`, not the four-skill core).
- `python harness.py check` (or `make check`) must run the strict OpenSpec
  validator on the new spec and report PASS.
- `python harness.py manifest-check` must report PASS after the manifest is
  regenerated with the selected new files.
