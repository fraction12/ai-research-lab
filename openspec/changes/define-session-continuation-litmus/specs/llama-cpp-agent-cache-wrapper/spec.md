## ADDED Requirements

### Requirement: Verify session continuation semantics
The system SHALL provide a focused litmus for verifying whether llama.cpp same-slot and restored-slot tail-only completions can recall primed content before interpreting session-tail benchmark failures.

#### Scenario: Run continuation litmus modes
- **WHEN** the session continuation litmus is executed
- **THEN** it runs full-prompt, live-tail, restored-tail, and fresh-tail modes for each synthetic secret-token case
- **AND** it records raw output, extracted answer, pass/fail status, timing, prompt hashes, and session setup telemetry for each case and mode

#### Scenario: Interpret continuation semantics
- **WHEN** full-prompt passes and fresh-tail fails for a case
- **THEN** live-tail pass/fail determines whether same-slot tail-only continuation is semantically usable for that case
- **AND** restored-tail pass/fail determines whether save/restore preserves that continuation behavior

#### Scenario: Preserve litmus artifacts
- **WHEN** the litmus writes raw prompt and model-output artifacts
- **THEN** those artifacts are written under ignored benchmark result paths
- **AND** committed Track 02 artifacts record exact raw paths, hashes, commands, model/backend metadata, and interpretation

#### Scenario: Avoid overinterpreting litmus success
- **WHEN** live-tail and restored-tail pass the tiny litmus
- **THEN** the system records that session continuation passed a necessary sanity check
- **AND** it does not claim GraphWalks or reasoning-over-prefix safety from the tiny litmus alone
