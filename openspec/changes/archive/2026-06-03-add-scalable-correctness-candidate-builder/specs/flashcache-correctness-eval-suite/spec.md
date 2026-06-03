## ADDED Requirements

### Requirement: Build reusable correctness candidate sets
The system SHALL provide a CLI workflow for building candidate case JSONL files from one or more supported correctness datasets.

#### Scenario: Build mixed candidate file
- **WHEN** the user requests a candidate set with multiple dataset counts
- **THEN** the system samples each requested dataset, converts rows into correctness cases, and writes one combined JSONL case file
- **AND** each case records candidate-builder metadata including sampling profile, dataset offset, and prompt-size filters

#### Scenario: Build easy IFEval candidates
- **WHEN** the user requests the easy IFEval sampling profile
- **THEN** the system only selects supported single-instruction IFEval rows with bounded prompt and parameter complexity
- **AND** the output records that the easy profile was used

### Requirement: Apply dataset-specific answer guidance
The system SHALL include scorer-aligned answer guidance when running the JSON answer protocol.

#### Scenario: JSON answer protocol uses dataset hint
- **WHEN** the user runs a correctness response command with the JSON answer protocol
- **THEN** the prompt includes dataset-specific guidance for the answer string shape
- **AND** the response record identifies which answer hint was used

#### Scenario: Raw answer protocol remains unchanged
- **WHEN** the user runs a correctness response command with the raw answer protocol
- **THEN** the system does not add JSON answer guidance or dataset-specific answer hints
