# Tasks: Java/Maven/JAR analyzer skill adoption

## 1. Catalog skill

- [x] Add `.agents/skills/catalog/java-maven-jar-analysis/SKILL.md` with stable
      YAML frontmatter (`name`, one-line `description`), a body that names the
      `jar_search` and `jar_api` MCP tools, and explicit fall-back rules to
      `javap`, `jdeps`, and `mvn dependency:tree` when the hooks return
      `available: false`.
- [x] Confirm the skill description is concise enough that `skill-router`
      picks it up deterministically (no embedding or LLM routing required).
- [x] Add a bounded `scripts/skill_router.py` signal plus positive Maven and
      negative Gradle coverage in `evals/routing/cases.json` and
      `tests/test_skill_runtime.py`.

## 2. Wiki nodes

- [x] Add `.ai/wiki/interfaces/java-jar-analyzer.md` with stable frontmatter
      (`id: interfaces.java-jar-analyzer`, `kind: interface`) and explicit
      pointers to the MCP source lines.
- [x] Add `.ai/wiki/modules/java-maven-jar-analysis.md` with stable
      frontmatter (`id: modules.java-maven-jar-analysis`, `kind: module`)
      describing the skill's triggers, ownership, and link to the interface
      page.

## 3. OpenSpec spec delta

- [x] Add
      `openspec/changes/java-maven-jar-skill-adoption/specs/java-maven-jar-analyzer/spec.md`
      with one or more `### Requirement:` blocks describing observable
      behavior (routing triggers, contract reference, fall-back strategy,
      matrix linkage). Each requirement has at least one `#### Scenario:`
      block.

## 4. Recommendation matrix

- [x] Update only the *Domain skills* row in
      `docs/REPORT_RECOMMENDATION_MATRIX.md` to *Adopted* with an explicit
      remaining gate: any future analyzer-module addition must remain opt-in
      and must not be enabled by default.

## 5. Verification

- [x] Run `make wiki-validate`. Expect: PASS with no new broken IDs or links.
- [x] Run `make skills-check`. Expect: catalog isolation intact; the new
      skill is reported as catalog-only, not core.
- [x] Run `python harness.py openspec-check` (or `make openspec-check`).
      Expect: change listed; strict validator passes on the new spec.
- [x] Run `python harness.py check` (or `make check`). Expect: same set of
      pre-existing PASS lines plus the new spec.
- [x] Regenerate `ARTIFACT_MANIFEST.sha256` with only the intended new files,
      then run `python harness.py manifest-check`.
- [x] Run `git diff --stat` and confirm only the eight new feature files plus
      the router, routing-evaluation, regression-test, matrix, and generated
      artifact-manifest/session-state files changed.

## 6. Closeout

- [x] Run `python3 scripts/session_state.py checkpoint` after each material
      step; update `decisions`, `done`, and `verification.passed` so a later
      compaction or handoff can resume without losing context.
- [x] Record the verified pre-integration checkpoint; the enclosing session
      tracks commit, merge, and post-merge verification separately.

Verification: the focused routing suite, Wiki and skill checks, strict
OpenSpec 1.12.0 validation, full harness test suite, Wiki index rebuild, and
artifact-manifest check passed on 2026-09-09.
