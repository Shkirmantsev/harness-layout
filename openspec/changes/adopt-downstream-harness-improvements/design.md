# Design

## Scope and evidence

Compare only reusable harness paths against donor commit `269fc50`, including
working-tree improvements present at inspection. Normalize Markdown line endings
before treating byte differences as meaningful. The donor's JSON schemas and
project-context MCP source have no content changes to import. Do not copy its
application Wiki, Java build system, contracts, or runtime data.

## Implementation

Retain POSIX parent-directory fsync after atomic replacement; skip it on Windows
in the three existing state writers. Use a callable regex replacement for literal
environment values. Resolve the executable with `shutil.which` in the existing
harness launcher.

Add `catalog_index` to router output: sorted name/description metadata only,
excluding selected skills, empty for confident plans. The calling model may
select relevant skills within the existing cap and dependency contract; low
confidence alone does not require interrupting the user. Add a compact Ponytail
adaptation without persistent persona, output restrictions or automatic activation.

Generalize the existing staged, locked sync to a destination function and invoke
it for Claude and OpenCode project directories. Codex already discovers the
canonical core in `.agents/skills/`; do not write into `CODEX_HOME` or home paths.
Preserve remote Hermes sync and integration-owned skills.

Context7 is disabled by default. Reuse existing HTTP transport support rather
than the donor's unsupported claim that Codex always needs stdio. Preserve bearer
headers in Claude/OpenCode JSON and Codex TOML. Write all potentially credential
bearing generated configs atomically with private POSIX mode. Accept only HTTPS
URLs without embedded credentials. Initialization does not contact Context7,
install npm packages or alter Claude approval preferences.

## Compatibility decisions

Do not adopt dated current-spec renames: they would change existing capability
identities, links and deltas without a portable behavioral benefit. Keep active
change identifiers semantic kebab-case. Do not copy generated OpenSpec 1.13
workflows into the installed 1.12 integration; their store commands and refresh
lifecycle belong to the generating tool. Do not adopt the detached stdio MCP
supervisor: clients need their own connected stdio process. The donor's transfer
script is tied to one audit, FIX2 markers and a commit; it is not a generic harness
feature and can export arbitrary committed business/credential files.

## Verification

Regression tests exercise actual generated JSON/TOML, private file modes, invalid
URLs, mirror isolation and drift detection, metadata routing and literal env
replacement. A simulated Windows branch checks that no directory handle is
opened; native Windows execution remains a separate platform check. Run focused
suites followed by Wiki/OpenSpec validation and `python harness.py check`.

The existing loose `session-handoff.md` is silently omitted by OpenSpec 1.12.
Adopt the donor's valid headings/scenario formatting at `session-handoff/spec.md`,
keeping the undated capability ID. Fail the gate on any loose current Markdown
spec to prevent recurrence. Archived historical references retain their context.
