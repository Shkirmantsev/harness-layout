# Design

## Current state

`scripts/session_state.py` previously wrote JSON below ignored
`tmp/local/sessions/`. `.ai/state/CURRENT.md` was a disconnected manual summary.

## Implemented design

Canonical task JSON lives at `.ai/state/handoffs/<session-id>.json`.
`.ai/state/CURRENT.md` is generated after every successful `start`, `checkpoint`,
or `resume`. A machine-readable marker lets current-task commands omit the ID.

The shared agent policy requires lifecycle updates after material steps,
decisions, failures, verification, and before handoff or completion. The normal
harness check rejects a current view that differs from its structured source.

## Data / persistence / concurrency impact

JSON and Markdown use temp-file, fsync, and atomic replacement. A single local
lock serializes selection and writes. Starting another incomplete current task
requires an explicit replacement flag.

## Compatibility and migration

The reader accepts schema-v1 checkpoints from the legacy ignored path and writes
them into the durable store when resumed or updated. Legacy data is not deleted.

## Risks and rollback

Task prose is source-visible, so policy forbids secrets, raw transcripts, and
large command output. Rollback can restore the legacy path and manual view
without transforming the plain JSON data.
