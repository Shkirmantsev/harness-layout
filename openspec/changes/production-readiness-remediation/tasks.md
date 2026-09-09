# Tasks

## 1. Approval lifecycle

- [x] Add regression tests for incompatible workers, approval metadata, exact-run
  resolution, and hard request deadlines.
- [x] Add the resolver capability gate to the generated OpenCode adapter.
- [x] Add a scoped Hermes worker compatibility patch without enabling unattended
  auto-approval.
- [x] Deploy the patch and pass an end-to-end guarded allow/deny approval probe on
  the live worker.
- [x] Update worker setup and native Hermes documentation.

## 2. Remote boundary hardening

- [x] Test and implement canonical allowed-root enforcement in the Hermes MCP
  sidecar.
- [x] Add bounded per-request deadlines and safe run-ID URL construction.
- [x] Add and document a secret-free delegated verification profile.
- [x] Deploy the updated sidecar with `HERMES_ALLOWED_PROJECT_ROOTS` configured on
  the live worker and rerun its health/authorization checks.

## 3. Local reliability and portability

- [x] Add regression tests and a shared POSIX/Windows inter-process lock.
- [x] Convert secret-bearing writers to private atomic replacement.
- [x] Make local skill synchronization locked and atomically published.
- [x] Generate and verify the OpenCode package dependency declaration.

## 4. Reproducible verification

- [x] Repair the project-context MCP compatibility failure.
- [x] Run strict OpenSpec validation from the harness gate.
- [x] Add deterministic artifact-manifest generation and verification.
- [x] Add Linux and Windows CI jobs covering the supported workflows.

## 5. Documentation and closeout

- [x] Repair broken catalog links and update current QA evidence.
- [x] Update the project Wiki and `HERMES_REVIEW.md` with verified resolutions.
- [x] Run focused tests, the full unit suite, strict OpenSpec validation, manifest
  verification, and `python harness.py check`.
