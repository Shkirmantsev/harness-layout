# Production-readiness audit: harness-layout v4

**Audit date:** 2026-09-08

**Target:** `/home/dmytro/workspace/personal_projects/harness-layout/harness-layout`

**Provenance:** delegated Hermes audit on `hermes-tailscale-worker` using its default profile/MoA (observed model: MiniMax-M3), followed by local Codex evidence review. Live worker observations supplied by the user are labeled as such.

**Scope:** repository, documentation, OpenSpec, Wiki/state, skills, tests, optional infrastructure, remote Hermes integration, security, and release hygiene. No secret values were read or included.

## Remediation update — 2026-09-09

**Repository readiness after remediation: 9/10 — SHIP.** All 14 repository
findings have implemented fixes and regression evidence. The hardened sidecar
and exact-revision compatibility patch are deployed on the live worker.
OpenCode surfaced the guarded pause and resumed the exact run correctly for
both `deny` and `once`; unattended auto-approval remains disabled.

| ID | Resolution | Evidence |
|---|---|---|
| B-1 | Resolved | project-context uses MCP 1.30.0/AnyIO 4.10.0 with Trio stdio; 5/5 tests and full gate pass |
| B-2 | Resolved | shared POSIX/Windows lock plus guarded UID/GID and Windows CI matrix |
| H-1 | Resolved and deployed | exact-revision Hermes patch, capability gate, preserved approval metadata, and live OpenCode `deny`/`once` cycles |
| H-2 | Resolved and deployed | mandatory canonical `HERMES_ALLOWED_PROJECT_ROOTS` with escape tests and live sidecar restart/health check |
| H-3 | Resolved | `python harness.py check-delegated` skips `.env` and retains repository gates |
| H-4 | Resolved | deterministic generate/verify commands; current 331-file manifest passes |
| M-1 | Resolved | private atomic replacement for `.env`, keys, runtime, and token-bearing settings |
| M-2 | Resolved | AbortController and remaining-budget httpx timeouts |
| M-3 | Resolved | Linux/Windows GitHub Actions matrix and full Linux gate |
| M-4 | Resolved | harness invokes `openspec validate --all --strict`; 3/3 pass |
| M-5 | Resolved | staged, serialized skill publication with rollback |
| M-6 | Resolved | generator owns `.opencode/package.json` and regression test |
| L-1 | Resolved | both catalog links now resolve |
| L-2 | Resolved | QA report names current evidence and labels older totals historical |

The original audit and score below are retained as the pre-remediation baseline.

## Verdict

**Production readiness: 5/10 — DON'T SHIP as a general production release.** The local core is thoughtfully structured and most unit tests pass, but the advertised full check is red, Windows support is currently broken, and the live OpenCode→Hermes approval lifecycle can strand runs. A controlled Linux-only local pilot is reasonable after accepting those limitations.

| Area | Score | Weight | Weighted reason |
|---|---:|---:|---|
| Documentation | 7 | 15% | Broad and navigable, but Windows and current QA claims overstate verified behavior. |
| Architecture | 6 | 20% | Clear source-of-truth boundaries; remote root authorization and client lifecycle boundaries need enforcement. |
| Safety | 6 | 20% | Secret ignores and ACL denial work; secret-file creation and remote root validation need hardening. |
| Testing | 4 | 15% | 60 root tests pass, but the primary gate and MCP integration fail and no CI runs them. |
| Operability | 3 | 15% | Live approvals time out; full checks cannot run from the restricted Hermes account. |
| Consistency | 4 | 15% | The integrity manifest is stale and strict OpenSpec state is currently invalid. |

Weighted score: `0.15×7 + 0.20×6 + 0.20×6 + 0.15×4 + 0.15×3 + 0.15×4 = 5.10`, rounded to **5**.

**Findings:** 2 blocker, 4 high, 6 medium, 2 low, 0 nit.

## Executive findings

| ID | Severity | Summary |
|---|---|---|
| B-1 | Blocker | `python3 harness.py check` consistently fails in the installed project-context MCP integration. |
| B-2 | Blocker | Windows is advertised, but the mandatory session-state module imports POSIX-only `fcntl`. |
| H-1 | High | Live OpenCode→Hermes approval requests are not reaching an interactive resolver. |
| H-2 | High | The Claude Hermes sidecar accepts arbitrary absolute project roots instead of enforcing a configured allowlist. |
| H-3 | High | The restricted Hermes worker cannot run the normal full check because that check requires the deliberately denied `.env`. |
| H-4 | High | `ARTIFACT_MANIFEST.sha256` is stale: 13 mismatches and one missing file. |
| M-1 | Medium | Secret-bearing files are written before mode `0600` is applied. |
| M-2 | Medium | Hermes wait deadlines do not bound individual HTTP requests. |
| M-3 | Medium | No repository CI workflow enforces the release gate. |
| M-4 | Medium | `harness.py check` does not run strict validation of all OpenSpec specs/changes. |
| M-5 | Medium | Local skill synchronization deletes then copies without a lock or atomic swap. |
| M-6 | Medium | The OpenCode Hermes tool imports an npm package with no tracked/generated dependency contract. |
| L-1 | Low | Two shipped skill README links are broken. |
| L-2 | Low | `QA_REPORT.md` presents historical PASS results that no longer reproduce. |

## Detailed findings

### B-1 — The advertised full verification gate is red

- **Location:** `tools/mcp/project-context-mcp/pyproject.toml:10`, `tools/mcp/project-context-mcp/tests/test_server.py:25-32`, `harness.py:83-101`.
- **Problem:** the local MCP package allows any `mcp>=2.0.0,<3`; the installed environment resolved `mcp==2.1.1`. Its stdio server did not answer either the high-level v2 client negotiation or the legacy `initialize` request, so the required full gate fails.
- **Evidence:** `python3 harness.py check` failed at `test_round_trip_and_change_boundary` with `MCPError: Request 'initialize' timed out`. The focused test failed **3/3** times. A minimal `MCPServer('x').run()` under the same environment also produced no initialize response. The other 60 repository tests passed sequentially.
- **Why this is release-blocking:** README and `AGENTS.md` make `harness.py check` the completion gate, and the project-context MCP is a primary feature.
- **Smallest fix:** pin the local MCP package to a version proven by the stdio integration test (the remote components currently pin `mcp==2.1.0`), commit a reproducible lock/constraints file, rebuild the local venv, and keep the stdio test in the mandatory gate. Do not merely raise the 10-second timeout. The current SDK documentation describes v2 as stable and recommends its new high-level `Client` for stdio and tests: [Python SDK v2 notes](https://github.com/modelcontextprotocol/python-sdk/blob/main/docs/whats-new.md), [stdio client transport](https://github.com/modelcontextprotocol/python-sdk/blob/main/docs/client/transports.md).

### B-2 — Advertised Windows support cannot execute the mandatory task-state gate

- **Location:** `README.md:65-73`, `harness.py:98,132`, `scripts/session_state.py:9,125-134`, `scripts/lesson_candidate.py:9`.
- **Problem:** the README supplies a Windows PowerShell workflow and `harness.py` calls itself cross-platform, but `session_state.py` imports POSIX-only `fcntl` unconditionally. `harness.py check` always invokes `session_state.py verify`.
- **Evidence:** Python on Windows has no standard `fcntl` module. There is no platform branch or Windows locking implementation in the file and no Windows CI coverage.
- **Smallest fix:** add a cross-platform file-lock abstraction (`fcntl` on POSIX, `msvcrt` or a small pinned lock library on Windows), test it on `windows-latest`, and keep the README claim only after that gate passes.

### H-1 — Live Hermes approvals are not propagated to the parent interaction

- **Location:** `templates/opencode/hermes.js:96-109,112-140,192-208`, `scripts/configure_clients.py:227-234`, `scripts/verify.py:63-76`, `tests/test_opencode_hermes.py:16-30`.
- **Problem:** the design expects `/v1/runs/{id}` to enter `waiting_for_approval`, return control to OpenCode, ask the user, then call `hermes_approve`. In the live run, tool approvals timed out inside Hermes instead of becoming a resolvable parent prompt.
- **Evidence (user-supplied live observation):** five `terminal`/`execute_code` requests timed out in about ten minutes with `BLOCKED: Command timed out without user response`; approval calls previously returned no pending approval while run state remained inconsistent. The worker nevertheless produced the first report, showing transport works but the approval lifecycle is unhealthy. Static tests only assert that strings/endpoints exist; `scripts/verify.py` submits a run but never polls, observes an approval pause, resolves/denies it, or checks terminal completion.
- **Smallest fix:** add an opt-in live contract test that deliberately requests a harmless approval, asserts `waiting_for_approval`, resolves it with `deny` or `once`, and verifies terminal completion. If Hermes does not expose the pause before its internal 60-second timeout, fix the gateway/API event mapping; do not disable approvals globally. For unattended read-only audits, explicitly auto-deny mutation-class tools and teach the worker to continue with read-only alternatives.

### H-2 — The Claude sidecar does not enforce the authorized repository root

- **Location:** `remote/hermes-worker-mcp/src/hermes_worker_mcp/native_context.py:7-18`, `remote/hermes-worker-mcp/src/hermes_worker_mcp/server.py:37-57`, `docs/SECURITY.md:9`.
- **Problem:** `validate_project_root()` accepts any absolute path except `/` and passes it into authoritative worker instructions. Values such as `/etc` or another checkout are accepted. The dedicated OS account is not a filesystem sandbox; the security documentation explicitly notes that world-readable OS files remain visible.
- **Evidence:** unit coverage rejects only relative paths, `/`, and control characters. No configured allowlist/root is present in sidecar `Settings`.
- **Smallest fix:** configure one or more allowed canonical project roots in the sidecar and require `Path(requested).resolve()` to equal or be inside an allowed root. Treat caller-supplied instructions as context, not authorization.

### H-3 — Hermes security policy and the normal check command conflict

- **Location:** `docs/SECURITY.md:3-9`, `scripts/hermes_host_setup.py:71-77`, `scripts/check_config.py:13-17`, `harness.py:96-101`.
- **Problem:** the Hermes account is correctly denied `.env`, but the normal full check unconditionally requires and reads `.env` before running tests. A delegated reviewer therefore cannot execute the repository's required verification command without weakening secret isolation.
- **Evidence (user-supplied live observation):** the worker received `Access denied: .../.env is a secret-bearing environment file`. This is expected enforcement, not a leaked secret and not a generic CI failure.
- **Smallest fix:** split structural validation from live-secret validation. Add a secret-free mode that validates `.env.example` plus non-secret repository structure and runs all tests; reserve live `.env` checks for the owner/operator. Keep the ACL denial.

### H-4 — The committed integrity manifest does not describe the current tree

- **Location:** `ARTIFACT_MANIFEST.sha256`.
- **Problem:** the manifest is committed as integrity evidence but has no documented generator/check target and is already stale.
- **Evidence:** `sha256sum -c ARTIFACT_MANIFEST.sha256` returned exit 1 with **13 checksum mismatches** and one missing listed file, `openspec/AGENTS.md`.
- **Smallest fix:** add a deterministic generator and a CI/check target; define included/excluded paths and regenerate only from a reviewed clean tree. If it is not a supported integrity contract, remove it rather than shipping misleading evidence.

### M-1 — Secret files have a permissions race during creation/update

- **Location:** `scripts/common.py:17-23`, `scripts/bootstrap_env.py:23-44`, `scripts/configure_clients.py:21-23,132-146,260-265`.
- **Problem:** `.env`, generated API-key files, and token-bearing settings are written with the process umask and only then changed to `0600`. They are also updated non-atomically.
- **Evidence:** `write_text()`/`copy2()` precede `chmod(0o600)` in each path. The containing generated directory is not private by default.
- **Smallest fix:** create secret files atomically with mode `0600` (`os.open(..., 0o600)` into a private temporary file, fsync, then `os.replace`) and lock concurrent updates.

### M-2 — Advertised wait timeouts are not hard bounds

- **Location:** `templates/opencode/hermes.js:43-67,96-109`, `remote/hermes-worker-mcp/src/hermes_worker_mcp/server.py:18,67-79`.
- **Problem:** OpenCode's `poll()` has a deadline, but each `fetch()` has no abort timeout. The Claude sidecar uses one global 3600-second HTTP timeout, so a single status request can exceed the caller's 1–900-second wait budget.
- **Evidence:** neither request loop passes a remaining-deadline timeout to the network call.
- **Smallest fix:** apply per-request deadlines capped by the remaining wait budget (`AbortSignal.timeout` for fetch; a short request timeout for httpx) and report upstream timeout separately from run state.

### M-3 — No CI enforces supported platforms or the release gate

- **Location:** repository root; no `.github/workflows/*`, `.gitlab-ci.yml`, or equivalent tracked workflow.
- **Problem:** claims about Linux/macOS/Windows, integrity, strict OpenSpec state, and stdio MCP compatibility can drift without detection.
- **Evidence:** repository inventory found no CI definition. `QA_REPORT.md` is manually recorded evidence only.
- **Smallest fix:** add Linux and Windows jobs for focused unit tests, `harness.py check`, manifest verification, strict OpenSpec validation when the CLI is available, and a Compose configuration check. Keep optional live-service tests explicitly gated.

### M-4 — The normal gate omits full strict OpenSpec validation

- **Location:** `harness.py:54-69,96-101`, `openspec/changes/automatic-session-handoff/` (local working tree).
- **Problem:** `cmd_openspec_check()` validates only the custom schema structure and `openspec schema validate production-sdd`; it does not validate every current spec and change.
- **Evidence:** `python3 harness.py openspec-check` passed, while `openspec validate --all --strict` failed because the local `automatic-session-handoff` change directory contains no delta. Current specs `project-initialization` and `skill-integration` passed. The empty directory is local/untracked, so this is current-worktree hygiene rather than a distributed empty-directory bug.
- **Smallest fix:** when the CLI exists, run strict validation for all specs and active changes; delete the local empty change directory after confirming its archived copy is authoritative.

### M-5 — Skill synchronization is non-atomic and race-prone

- **Location:** `scripts/sync_skills.py:52-67`.
- **Problem:** `local()` removes each managed destination and then copies source trees directly. Concurrent invocations or interruption can leave missing/partial core skills.
- **Evidence:** there is no lock or temporary-directory swap; the repository already has locking/atomic-write patterns in `session_state.py` and `lesson_candidate.py`.
- **Smallest fix:** serialize sync with a project-local lock and stage each managed tree before an atomic rename/swap.

### M-6 — OpenCode tool dependency ownership is undefined

- **Location:** `templates/opencode/hermes.js:1`, `.opencode/package.json`, `.opencode/.gitignore`.
- **Problem:** the generated tool imports `@opencode-ai/plugin`, but the repository neither tracks nor generates a package declaration. The current working tree has an untracked `.opencode/package.json` pinning `1.18.28`.
- **Evidence:** `git ls-files .opencode/package.json` is empty; the client generator writes `hermes.js` but not package metadata.
- **Smallest fix:** choose one ownership model: commit the package declaration as source, or generate and ignore it together with the tool. Add a runtime smoke test that imports the generated tool. Do not simply ignore the file without preserving the dependency.

### L-1 — Shipped skill documentation contains two real broken links

- **Location:** `.agents/skills/catalog/caveman/README.md:52`, `.agents/skills/catalog/caveman-review/README.md:33`.
- **Problem:** both link to `../../README.md`, which resolves to `.agents/skills/README.md` and does not exist.
- **Evidence:** repository-wide local Markdown link scan. Other apparent failures inside fenced examples were excluded.
- **Smallest fix:** point at the intended repository/upstream README or remove the links.

### L-2 — Release QA evidence is stale

- **Location:** `QA_REPORT.md:5-25`.
- **Problem:** the report says `harness.py check` passes with MCP SDK 2.1.1 and records changing totals (56, 58, 63), but the current tree contains 60 root tests and the installed MCP integration fails consistently.
- **Evidence:** current verification results below.
- **Smallest fix:** generate a dated machine-readable verification summary from CI/`harness.py check`, and clearly label old QA reports as historical snapshots.

## Area review

### Repository shape, documentation, and architecture

The project intent is clear. `AGENTS.md` is deliberately compact, `docs/README.md` provides bounded navigation, OpenSpec owns normative behavior, `.ai/wiki` owns reviewed explanatory knowledge, and generated state is segregated under `.generated/` or `tmp/local/`. `AGENT.md` is a tracked compatibility redirect, not an orphan. The single ADR, `.ai/wiki/adr/0001-separate-core-and-integration-skill-ownership.md`, aligns with the current skill-sync implementation.

The largest architecture gap is that authorization relies partly on agent instructions: the remote sidecar does not cryptographically/policy-bind its requested root, and the approval event lifecycle has not been proven end-to-end.

### Safety and secrets

- `.env`, generated credentials/configs, local indexes, venvs, and runtime artifacts are ignored.
- `git log --all -- .env` returned no history.
- A filename-only scan of tracked non-document files found no common private-key/API-token patterns.
- The worker's `.env` denial and inability to read `.opencode/tools/hermes.js` are expected ACL outcomes; neither is evidence of a leaked secret.
- The local project-context venv path is currently mode-traversable/executable (`775` ancestors, `755` Python). The reported worker access error is therefore likely stale path/workdir state, not a present Unix-mode defect.
- Hermes hardline rejection of heredocs/malformed executable payloads is a safety control working as designed. Delegated prompts should tell the agent to use parser-compatible, non-destructive commands.

### OpenSpec, Wiki/state, and skills

- Wiki validation: 6 documents, 0 broken Wiki links, 0 duplicate IDs.
- Current state and its handoff JSON validate. Historical handoff JSON files are intentional task history unless a retention policy says otherwise.
- Current specs for project initialization and skill integration pass strict validation.
- Skill sync reports 4 core skills and 48 on-demand skills with no unintended direct exposure. `grill-me` and `grilling` are distinct names with an explicit canonical alias in the router.
- The routing eval dataset is used by `tests/test_skill_router_eval.py`; it is not dead data.

### Tests, infrastructure, and deployability

The root suite has useful coverage for routing, session state, documentation navigation, client generation, remote-sidecar shape, and security boundaries. However, many Hermes tests are string-presence/static contract tests; they do not prove a real run, approval, cancellation, model selection, or SSH file operation. The Compose file validates and generally uses loopback binds, read-only filesystems, dropped capabilities, memory limits, and log rotation. Optional service images remain tag-pinned rather than digest-pinned, so exact supply-chain reproducibility is incomplete.

## Verification evidence

| Command/check | Result |
|---|---|
| `python3 -m unittest discover -s tests -v` | **PASS** — 60 tests. |
| `python3 harness.py check` | **FAIL** — project-context MCP initialize timeout. |
| Focused MCP stdio test, three sequential runs | **FAIL 3/3** — initialize timeout each run. |
| `python3 harness.py wiki-validate` | **PASS** — 6 documents, 0 issues. |
| `python3 scripts/sync_skills.py check` | **PASS** — 4 core, 48 on demand. |
| `PYTHONPATH=remote/hermes-worker-mcp/src python3 -m unittest discover -s remote/hermes-worker-mcp/tests -v` | **PASS** — 4 tests. |
| `docker compose --env-file .env -f infra/compose.yaml --profile '*' config -q` | **PASS**. |
| `openspec validate --all --strict` | **FAIL** — 2 specs pass; local empty active change fails. |
| `sha256sum -c ARTIFACT_MANIFEST.sha256` | **FAIL** — 13 mismatches, 1 missing file. |
| Tracked secret filename/pattern checks | **PASS** — `.env` absent from history; no common token/key pattern hits in tracked non-doc files. |
| Live OpenCode→Hermes run | **DEGRADED** — real SSH-backed work and report creation succeeded; approval requests repeatedly timed out. |

## Ship plan

1. Fix B-1 and B-2; make Linux and Windows required CI jobs.
2. Add the live Hermes approval lifecycle test and repair gateway event propagation without weakening the default safety policy.
3. Enforce allowed project roots server-side and add a secret-free delegated verification mode.
4. Regenerate and continuously verify the artifact manifest and strict OpenSpec state.
5. Harden secret writes, request timeouts, skill sync, and OpenCode dependency ownership.

Re-score after all blocker/high findings are closed and the full gate passes from a clean clone.
