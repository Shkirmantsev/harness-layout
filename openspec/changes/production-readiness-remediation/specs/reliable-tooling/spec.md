## ADDED Requirements

### Requirement: Private atomic secret writes

Harness code that creates or replaces secret-bearing files SHALL create private
temporary files with mode `0600`, flush them, and atomically replace the target.
No permissive intermediate target file SHALL be observable.

#### Scenario: new secret file is written

- **WHEN** harness tooling creates `.env` or a client secrets file
- **THEN** the first filesystem-visible inode containing secret material has mode
  `0600`
- **AND** readers observe either the complete old content or complete new content

### Requirement: Portable inter-process locking

State-mutating scripts SHALL use a lock implementation available on every
advertised supported platform, while retaining mutual exclusion between
processes.

#### Scenario: module loads on Windows

- **GIVEN** the Python runtime does not provide `fcntl`
- **WHEN** session-state or lesson-candidate tooling is imported and used
- **THEN** it selects a supported Windows locking implementation
- **AND** concurrent writers remain serialized

### Requirement: Race-safe skill synchronization

Local skill synchronization SHALL serialize writers and publish complete trees
atomically. Readers SHALL NOT observe a destination removed between deletion and
copy.

#### Scenario: two synchronizers target one client

- **WHEN** two local sync operations run concurrently
- **THEN** one writer waits for the other
- **AND** the final destination is one complete generated tree

### Requirement: Reproducible client dependencies

Every generated client adapter import SHALL have a harness-owned dependency
declaration generated or installed by the same workflow.

#### Scenario: OpenCode configuration is generated

- **WHEN** `configure-clients` installs the Hermes tool
- **THEN** it also produces the required OpenCode package declaration
- **AND** verification detects a missing or incompatible declaration
