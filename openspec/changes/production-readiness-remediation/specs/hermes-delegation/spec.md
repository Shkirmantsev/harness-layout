## ADDED Requirements

### Requirement: Resolver-capable run approvals

The harness SHALL delegate guarded work only through a Hermes run transport that
explicitly proves it can resolve approvals for the active run. It SHALL NOT treat
notification-only callbacks as approval resolvers and SHALL NOT use unattended
auto-approval as a compatibility fallback.

#### Scenario: compatible worker pauses and resumes

- **GIVEN** a Hermes worker advertises resolver-backed run approvals
- **WHEN** a delegated action requires consent
- **THEN** the run exposes a pending approval associated with that run
- **AND** OpenCode shows the approval request to the user
- **AND** an explicit allow or deny resumes that exact run

#### Scenario: incompatible worker fails before delegation

- **GIVEN** a worker cannot prove resolver-backed run approvals
- **WHEN** OpenCode attempts to start a delegated run
- **THEN** the adapter rejects the request before creating the run
- **AND** the error identifies the required worker capability
- **AND** no approval policy is weakened

### Requirement: Bounded Hermes requests

Every Hermes HTTP operation SHALL have an abortable per-request deadline bounded
by the remaining operation deadline. A stalled request SHALL NOT make a wait
operation exceed its declared timeout by more than scheduler overhead.

#### Scenario: poll request stalls

- **GIVEN** a run wait has a finite timeout
- **WHEN** a status request never returns
- **THEN** the request is aborted at the remaining deadline
- **AND** the caller receives a timeout result

### Requirement: Server-enforced project boundaries

The Hermes MCP server SHALL resolve and validate every requested project root
against configured exact allowed roots before forwarding a run. Client-provided
paths alone SHALL NOT establish authorization.

#### Scenario: root outside the allowlist

- **GIVEN** the sidecar is configured with one or more allowed roots
- **WHEN** a caller supplies an absolute path outside those roots
- **THEN** the sidecar rejects the request before contacting Hermes

#### Scenario: symlink escape

- **GIVEN** a caller supplies a child path or path containing traversal beneath an
  allowed root
- **WHEN** the sidecar validates that path
- **THEN** the sidecar rejects it because only the exact configured root is authorized

### Requirement: Secret-free delegated verification

The harness SHALL expose a verification profile that exercises repository-owned
checks without reading project secrets. The restricted Hermes account SHALL use
that profile rather than receiving permission to read `.env`.

#### Scenario: restricted worker verifies a checkout

- **GIVEN** the worker can read the repository but cannot read `.env`
- **WHEN** it runs the documented delegated verification command
- **THEN** repository structure, tests, docs, specs, and integrity checks run
- **AND** no secret-bearing file is opened
