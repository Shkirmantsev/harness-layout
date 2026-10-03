# Design

## Context

Donor AGENTS and OpenSpec README date accepted capabilities and archives, while
active changes remain undated. The accepted specs collectively represent current
state; this harness adds a checked central navigation view for discoverability.

## Decisions

Preserve original Git dates: initialization, skills and handoff 2026-09-07;
portable tooling and governance 2026-10-03. Update live links and active delta
paths, leaving archived artifacts and prior task records as historical evidence.
Keep normative bodies in per-capability specs rather than a duplicated monolith.
Use pathlib, ISO calendar date validation and relative POSIX links on both OSes.
Generated integration skills remain tool-owned; project policy/config governs them.

## Migration and rollback

Dated IDs replace undated current IDs once. Reverse path and link changes together
to roll back; no runtime data or product API changes. The central inventory is
maintained during adoption/retirement and checked by the existing harness gate.
