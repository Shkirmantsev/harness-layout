---
id: project.downstream-harness-adoption
title: Downstream Harness Adoption
kind: project
status: active
summary: Reusable harness improvements adopted from the downstream CMC project, with compatibility and scope decisions.
sourceRefs:
  - scripts/sync_skills.py
  - scripts/skill_router.py
  - scripts/configure_clients.py
  - tests/test_downstream_harness.py
maintenance:
  mode: authored
---

# Downstream harness adoption

Reviewed on 2026-10-03 against the working tree of
`/home/dmytro/workspace/CMC_interface/RpaCMCMachineTCPGateway`, whose HEAD was
`269fc50`. The donor was read-only. Compare normalized text before importing:
several apparent differences in conventions and generated skills were only
line endings or generator version metadata.

## Adopted behavior

| Area | Adoption and adaptation |
|---|---|
| Atomic JSON/session writes | Retain POSIX directory durability; skip unsupported directory handles on Windows. JSON schemas and record shapes are unchanged. |
| Environment updates | Callable regex replacement preserves literal backslashes and digit sequences. |
| Skill routing | Uncertain plans expose sorted unloaded metadata for semantic selection within the existing cap; confident plans keep an empty index. Existing language, web and Hermes routes are retained. |
| Ponytail | Compact catalog-only simplicity procedure; no persistent persona, forced tiny output or weakened acceptance criteria. |
| Client skill sync | Four core skills mirror into project-local Claude/OpenCode directories. Codex uses `.agents/skills/`; no global writes. Integration/personal skills and remote Hermes sync remain available. |
| Context7 | Disabled by default. Existing HTTP transport in all clients preserves optional bearer authentication in atomically written private configs. No npm requirement or auto-enabling of Claude approvals. |
| Executable launch | Resolve platform wrappers through command lookup before subprocess execution. |
| OpenSpec coverage | Normalize the previously loose session-handoff spec into `session-handoff/spec.md`, preserving behavior and capability identity. The gate rejects loose current specs so the CLI cannot silently omit them. |

## Reviewed without importing

| Donor material | Decision |
|---|---|
| JSON schemas, runtime budget structure, project-context MCP source | Content already matches this harness. No donor SQLite index, state records or runtime databases are imported. |
| Engineering conventions | Normalized contents match; retain the current canonical files. |
| Integration removal patches | Donor removed LiteLLM, Hermes, SearXNG/Crawl4AI and other supported adapters; retain this template's integrations and safety boundaries. |
| User-global Codex skill synchronization | Conflicts with project isolation and canonical discovery; replaced by project-local mirrors. |
| Detached stdio MCP supervisor | Redirects protocol output to a log and has no client connection transport; keep the client-managed process lifecycle. |
| Dated current capability names | Initially deferred; explicitly adopted on user request on 2026-10-03. Original Git acceptance dates are retained and live links/deltas migrated. See the central [current state](../../../openspec/CURRENT.md). |
| Generated OpenSpec 1.13 workflows | Additional workflows include store commands from a different generator version; external-tool ownership governs refresh. Do not copy them into the 1.12 integration. |
| Implementation-transfer script | Tied to FIX2 audit files and a specific source commit, with whole-tree exports and commit replay. No generic harness import. |
| Gateway Wiki, OpenSpec specs, build/runtime scripts and contracts | Business-specific material is outside the requested scope; no imports. |

## Verification and limits

`tests.test_downstream_harness` covers environment replacement, simulated Windows
write branches, metadata routing, both client mirrors, Context7 renderers,
authentication, private POSIX modes, invalid URLs, executable resolution and
rejection of ignored loose specs. The full gate is `python harness.py check`.
Native Windows execution and live Context7 requests are separate optional checks;
passing local configuration tests does not establish either.

See [configuration](../../../docs/CONFIGURATION.md),
[skills](../../../docs/SKILLS.md), and
[current portable tooling requirements](../../../openspec/specs/2026-10-03-portable-harness-tooling/spec.md).


Recorded evidence on 2026-10-03: the full harness gate passed 82 tests with no
skips, strict OpenSpec validation passed seven items, Wiki validation passed nine
documents, both core skill mirrors passed, and the 350-file manifest passed.
The installed OpenSpec 1.12 used Node 22 on PATH. The MCP handshake needed an
authorized run with local socket permissions after the sandbox denied Trio's
socket option; MCP implementation was unchanged.


## Remote integration corrections

The first feature PR run exposed missing PyYAML setup and Windows-specific test
assumptions in the previously unexercised remote matrix. `requirements-dev.txt`
now pins that test/configuration dependency and both CI jobs install it. Harness
environment reads and affected source-document tests explicitly use UTF-8.
Windows assertions compare resolved paths and native permission semantics; the
CLI test fixture runs through Python. Optional Hermes ACL setup imports POSIX
account support only on its supported host and ancestor traversal terminates at
native roots. These fixes were made on the feature branch before merging.


Remote evidence: feature commit `0a4c801` passed all five GitHub CI jobs: Linux
and Windows unit suites on Python 3.11/3.13 and the full Linux harness gate.
After the CI corrections, the local full gate passed 84 tests, seven strict
OpenSpec items, nine Wiki documents and the 351-file manifest. Live Context7
access remains untested. Changes are integrated through feature-to-dev and
then dev-to-main pull requests with merge commits through the remote repository.


## Supported platform gate

Linux and Windows are required platforms for the portable harness core. The
workflow also runs full Windows gates on Python 3.11/3.13 with installed MCP
runtime dependencies, strict OpenSpec, state/Wiki checks and artifact integrity.
These jobs exercise actual stdio initialization and requests. Docker/Compose
checks remain in full Linux verification, and POSIX ACL setup is an optional
host adapter. The user handles the final dev-to-main merge on GitHub.

The generic donor line-ending policy is adopted in `.gitattributes`: text
checkouts use LF on both systems, while Git detects binary files automatically.
This preserves artifact-manifest byte hashes on Windows without importing
business-specific file rules.


Full Linux/Windows verification passed on feature commit `d83244b`: all seven CI
jobs passed, including actual Windows MCP exchanges on Python 3.11 and 3.13,
84 tests without skips and the 352-file manifest. Local dev integration preserved
history with merge commit `88358ee` and was published. The agent leaves main to
the user through GitHub PR #2; main was not changed by this integration step.


## OpenSpec current-state follow-up

On explicit user request, accepted spec folders now use the donor's dated naming.
Active change IDs remain undated; archive IDs carry archive dates. The central
`openspec/CURRENT.md` lists every accepted capability without copying requirements
or mixing proposals with current behavior. `scripts/openspec_layout.py` verifies
real calendar dates, naming and exact current-state coverage on Linux/Windows.
Historical archives retain their original paths. Generated integration skills
remain tool-owned; shared policy in AGENTS, OpenSpec config and the catalog skill
supplies the project-specific naming and adoption rules.

Follow-up evidence: feature `8f5583e` passed all seven native CI jobs, including
full Windows 3.11/3.13 gates. The local full gate passed 88 tests. Development
integration was published as merge `ba8e049`; this change and the prior completed
adoption are archived with 2026-10-03 prefixes. Final strict validation passed
seven current/active items, Wiki validation passed nine documents, and the
363-file manifest passed. The earlier agent-created main PR was closed without
merge so the user can create their own dev-to-main PR.
