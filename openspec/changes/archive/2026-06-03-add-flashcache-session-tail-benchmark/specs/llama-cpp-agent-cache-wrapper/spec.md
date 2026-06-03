## MODIFIED Requirements

### Requirement: Compare wrapper cache value
The system SHALL provide a smoke benchmark for the wrapper cache path.

#### Scenario: Run wrapper smoke benchmark
- **WHEN** the user runs the wrapper benchmark against a workflow fixture
- **THEN** the benchmark compares direct llama.cpp full-prompt calls with wrapper cache-aware calls
- **AND** writes a result JSON that reports cache hit rate, prompt timing, save/restore overhead, net delta, boundary timing telemetry where available, selected server mode, and selected cache mode

#### Scenario: Run wrapper benchmark with persistent server mode
- **WHEN** the user runs the wrapper benchmark with persistent server mode
- **THEN** the benchmark keeps a llama.cpp server alive across direct full-prompt scenarios
- **AND** keeps a separate llama.cpp server alive across wrapper cache-aware scenarios
- **AND** records the selected server mode in result metadata

#### Scenario: Run wrapper benchmark with hot cache mode
- **WHEN** the user runs the wrapper benchmark with hot cache mode
- **THEN** the benchmark prewarms the reusable prefix slot before measured wrapper runs
- **AND** stores prewarm telemetry separately from measured wrapper runs
- **AND** reports measured wrapper cache states from cache-hit runs

#### Scenario: Run wrapper benchmark with session cache mode
- **WHEN** the user runs the wrapper benchmark with session cache mode
- **THEN** the benchmark prewarms the reusable prefix slot before measured wrapper runs
- **AND** restores the slot once into a persistent wrapper server session before measured wrapper runs
- **AND** sends full changed-tail prompts without restoring the slot before each measured turn
- **AND** records session setup telemetry separately from measured wrapper runs
- **AND** records the selected cache mode in result metadata

#### Scenario: Run wrapper benchmark with session-tail cache mode
- **WHEN** the user runs the wrapper benchmark with session-tail cache mode
- **THEN** the benchmark prewarms the reusable prefix slot before measured wrapper runs
- **AND** restores the slot once into a persistent wrapper server session before measured wrapper runs
- **AND** sends only changed-tail prompt text without restoring the slot before each measured turn
- **AND** marks measured runs as tail-only session cache hits
- **AND** records session setup telemetry separately from measured wrapper runs
- **AND** records the selected cache mode in result metadata
