## MODIFIED Requirements

### Requirement: Compare wrapper cache value
The system SHALL provide a smoke benchmark for the wrapper cache path.

#### Scenario: Run wrapper smoke benchmark
- **WHEN** the user runs the wrapper benchmark against a workflow fixture
- **THEN** the benchmark compares direct llama.cpp full-prompt calls with wrapper cache-aware calls
- **AND** writes a result JSON that reports cache hit rate, prompt timing, save/restore overhead, net delta, boundary timing telemetry where available, selected server mode, and selected cache mode

#### Scenario: Run wrapper benchmark with hot cache mode
- **WHEN** the user runs the wrapper benchmark with hot cache mode
- **THEN** the benchmark prewarms the reusable prefix slot before measured wrapper runs
- **AND** stores prewarm telemetry separately from measured wrapper runs
- **AND** reports measured wrapper cache states from cache-hit runs
