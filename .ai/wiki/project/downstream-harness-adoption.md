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
| Dated current capability names | Would rename stable capabilities and links without behavioral benefit. Adopt standard spec directories while retaining undated IDs. |
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
[current portable tooling requirements](../../../openspec/specs/portable-harness-tooling/spec.md).


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
