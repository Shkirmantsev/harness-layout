# Tasks

- [x] 1. Add durable handoff persistence, generated current state, and active-task discovery.
- [x] 2. Add regression tests for synchronization, ID-free resume, active-task protection, and legacy promotion.
- [x] 3. Update agent policy, checkpoint instructions, documentation, and Wiki.
- [x] 4. Run focused tests and `python harness.py check`.
- [x] 5. Adopt the requirement and archive this change after verification.

Verification: `python3 harness.py check` passed on 2026-09-07. The OpenSpec CLI
was not installed, so its optional schema validation was not run; the repository
structural OpenSpec check passed.
