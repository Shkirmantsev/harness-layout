# Production-readiness remediation

## Why

The production-readiness audit found that the advertised full workflow is not
currently reproducible or safe enough to ship. Most importantly, OpenCode runs
can enter `waiting_for_approval` without a resolver-backed pending approval,
which leaves delegated work permanently stuck. The audit also found portability,
integrity, timeout, secret-write, root-validation, concurrency, and continuous
verification gaps.

## What Changes

- Require a resolver-capable Hermes `/v1/runs` approval transport and fail closed
  before delegation when the worker cannot prove that capability.
- Preserve approval metadata in the OpenCode adapter and resolve only the named
  run; never enable unattended auto-approval as a compatibility workaround.
- Enforce configured project roots in the Hermes MCP server, not only in clients.
- Add a secret-free delegated verification profile so the restricted Hermes
  account can validate repository behavior without reading `.env`.
- Make request deadlines hard bounds, secret-bearing writes atomic and private,
  and skill synchronization lock-protected and atomic.
- Make session-state locking portable across supported platforms.
- Own generated OpenCode dependencies, artifact integrity, strict OpenSpec
  validation, and CI in the harness itself.
- Repair documentation links and replace historical QA claims with current,
  reproducible evidence.

## Scope

### In scope

- The OpenCode Hermes adapter and its generator.
- The native Hermes MCP sidecar and worker setup/verification code.
- Harness checks, artifact manifest tooling, CI, tests, and affected docs.
- Cross-platform locking for state and lesson-candidate writers.

### Out of scope

- Disabling Hermes approval controls or automatically approving guarded actions.
- Reading `.env` from the restricted Hermes account.
- General changes to Hermes Agent outside the resolver-backed API compatibility
  needed by this harness.
- New product features unrelated to audited production-readiness findings.

## Success criteria

1. A compatible worker emits a resolvable approval event, OpenCode surfaces it,
   and an explicit allow or deny resumes the same run.
2. An incompatible worker is rejected before a delegated task starts with an
   actionable compatibility error.
3. Project-root escapes are rejected by the server.
4. Secret writes never expose permissive intermediate files; waits respect their
   declared wall-clock deadline; concurrent skill sync cannot expose a missing or
   partial destination.
5. Linux tests, portable-lock tests, strict OpenSpec validation, manifest
   verification, MCP integration, and the full harness gate pass in CI and from a
   clean checkout.
