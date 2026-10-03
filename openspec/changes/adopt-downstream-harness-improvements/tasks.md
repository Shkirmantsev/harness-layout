# Tasks

- [x] Compare normalized reusable donor paths and record import/rejection decisions.
- [x] Port Windows durability and literal environment replacement fixes.
- [x] Add bounded router fallback metadata and the optional Ponytail adaptation.
- [x] Generalize project-local skill mirrors while retaining remote integrations.
- [x] Add opt-in Context7 authentication and private generated config writes.
- [x] Add focused regression checks for the changed behavior.
- [x] Update current requirements and Wiki/documentation after verification.
- [x] Review the complete diff, rebuild Wiki index and verify client skill mirrors.
- [x] Run strict OpenSpec validation and the full harness gate; regenerate manifest.
- [x] Record final verification and completed session state.


Verification on 2026-10-03: focused regression suites passed, both client mirrors
validated, the Wiki index rebuilt, and the full `python3 harness.py check` gate
passed (82 tests, no skips; 7 strict OpenSpec items; 9 Wiki documents; 350 manifest
artifacts). The installed OpenSpec 1.12 executable required Node 22 on PATH.
The sandbox run initially denied Trio's local socket option; the authorized
rerun with local process permissions passed without modifying MCP source.
Native Windows execution and live Context7 requests were NOT RUN.
The verified behavior has been synchronized into current specifications; this
completed implementation change remains active as review evidence.


- [x] Correct remote CI dependency installation and demonstrated Windows path,
  encoding, launcher, permissions and optional-host-adapter assumptions.
- [ ] Pass the full remote Linux/Windows Python 3.11/3.13 matrix before merging.
