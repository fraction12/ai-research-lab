## ADDED Requirements

### Requirement: Passive manager turn ledger
The lab SHALL maintain a local JSON ledger for Workspace Manager turns using a Codex `Stop` hook.

#### Scenario: Workspace Manager turn ends
- **WHEN** a Workspace Manager turn stops in the lab repo
- **THEN** the hook records the thread id, role, repo, last update, inferred status, next action hint, and update timestamp in the local ledger

#### Scenario: Non-manager turn ends
- **WHEN** a non-manager Codex turn stops in the lab repo
- **THEN** the hook exits successfully without modifying the manager ledger

### Requirement: Passive hook behavior
The ledger hook SHALL NOT block, continue, or otherwise steer Codex turns.

#### Scenario: Hook completes normally
- **WHEN** the hook handles a matching or non-matching stop event
- **THEN** it exits with success and emits valid JSON that does not request continuation

### Requirement: Local generated state
The generated manager ledger state SHALL remain local machine state and SHALL NOT be committed by default.

#### Scenario: Ledger file is generated
- **WHEN** the hook writes the manager ledger JSON file
- **THEN** Git ignores that generated ledger file and its temporary write file

### Requirement: Recoverable updates
The hook SHALL preserve existing ledger content when a new turn update is written.

#### Scenario: Existing ledger contains entries
- **WHEN** the hook writes a Workspace Manager update to an existing ledger
- **THEN** existing thread entries and event history are preserved while the manager entry is updated
