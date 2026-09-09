# Design

## Context

OpenCode calls a generated JavaScript adapter, which calls Hermes Agent's
OpenAI-compatible `/v1/runs` API. Hermes owns the approval lifecycle. The native
MCP sidecar is a separate transport used by Claude-compatible clients. The audit
showed an upstream Hermes regression where `api_server` sessions are classified
as unattended before the resolver-backed callback registered by `/v1/runs` can
be used. This yields a contradictory state: the run reports
`waiting_for_approval`, but the approval endpoint has no pending item.

The remediation keeps each control at its responsible boundary: Hermes must
provide a real resolver, adapters must gate compatibility and bound network
operations, and the MCP sidecar must enforce filesystem authorization itself.

## Decisions

### Explicit resolver capability

The adapter will require an explicit, machine-readable capability from the
worker before it creates a run. Capability presence means the route binds a
resolver for the lifetime of that run; callback registration alone is not
sufficient. Worker setup and verification will test a guarded probe end to end,
not merely check that an endpoint exists.

This is intentionally fail-closed. Configuring `unattended_mode: approve` would
make delegation move again, but would silently authorize every guarded API
action and is therefore rejected.

### Compatibility boundary

The harness will carry the smallest worker compatibility patch or minimum
upstream revision needed for resolver-backed `/v1/runs`, plus a verification
probe. It will not fork unrelated Hermes behavior. The patch/revision boundary
must be explicit and reversible when upstream releases the fix.

### Root authorization

The MCP service receives an exact-root allowlist through configuration. Because
the paths live on the main machine behind Hermes' SSH backend, the remote sidecar
must not pretend its local `resolve()`/`stat()` authorizes them. It normalizes
POSIX paths and requires exact equality with an operator-configured root, which
also rejects caller-selected child and traversal paths. The absence of an
allowlist is a configuration error.

### Atomic publication

Secret writers use a private temporary file in the target directory, fsync it,
set mode before content becomes reachable at the destination, and publish with
`os.replace`. Skill synchronization uses an inter-process lock, builds a sibling
staging tree, and swaps complete trees with rollback cleanup.

### Portable locking

A small shared locking module selects `fcntl` on POSIX and `msvcrt` on Windows.
Callers use one context-manager API. Platform-selection tests simulate both
imports without requiring a Windows runner; CI also runs the unit suite on
Windows.

### Verification profiles

`harness.py check` remains the operator/full check and may validate local runtime
configuration. A delegated/CI-safe profile skips secret-dependent configuration
loading while retaining repository correctness checks. Documentation names both
profiles so omission of secret validation is explicit.

## Failure modes

- Missing resolver capability: reject before POST `/v1/runs`.
- Capability claimed but guarded probe cannot be resolved: worker verification
  fails and deployment is not marked healthy.
- Approval becomes unresolvable mid-run: surface a protocol error with run ID;
  never retry by auto-approving.
- Invalid allowed-root configuration: refuse filesystem-bearing sidecar calls.
- Interrupted atomic write/sync: old published state remains usable; stale staging
  data is safe to remove on the next run.
- Missing OpenSpec CLI in full gate: fail with an installation hint rather than
  silently reducing validation.

## Rollback

Each change is additive or restores stricter behavior. The worker compatibility
patch is removed once the pinned upstream revision includes equivalent resolver
semantics and the end-to-end probe passes. Atomic writers and portable locking
can be rolled back independently, but their regression tests remain the contract.
