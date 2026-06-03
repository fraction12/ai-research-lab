## ADDED Requirements

### Requirement: Run baseline-pass correctness ladder
The system SHALL provide a correctness ladder that only compares session-tail against full-prompt cases that pass the baseline scorer.

#### Scenario: Select full-prompt passing cases
- **WHEN** the user runs the baseline-pass ladder on a candidate case JSONL file
- **THEN** the system runs full-prompt responses, scores them, and writes a selected case JSONL containing only cases whose full-prompt score passes the configured threshold
- **AND** records the candidate count, selected count, full response path, full score path, and selected case path

#### Scenario: Compare session-tail on selected cases
- **WHEN** at least one full-prompt case passes selection
- **THEN** the system runs session-tail responses only for the selected cases
- **AND** writes a combined parity response JSONL containing selected full responses and selected session-tail responses
- **AND** writes a parity score JSON comparing the two modes

#### Scenario: No baseline cases pass
- **WHEN** no full-prompt case passes selection
- **THEN** the system writes a ladder report showing zero selected cases
- **AND** does not claim session-tail quality parity
