# Tasks

- [x] Locate private references without accessing any foreign repository.
- [x] Redact private provenance and retire completed historical state safely.
- [x] Enforce current-root setup/client selection and add security regression tests.
- [x] Verify full local and native Linux/Windows gates and update copying guidance.
- [x] Adopt accepted requirements and integrate into dev; main remains user-owned.

Evidence: feature `90282e4` passed all seven native CI jobs and the local
107-test full gate. Private references are absent from current tracked text.
Feature merged locally and published to dev; existing copies need the patch and
regenerated configs, and main merge remains user-owned. Git history is unchanged.
