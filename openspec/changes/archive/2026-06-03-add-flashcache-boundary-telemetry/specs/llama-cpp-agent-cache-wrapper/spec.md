## MODIFIED Requirements

### Requirement: Emit cache telemetry
The wrapper SHALL expose cache behavior and timing telemetry to callers.

#### Scenario: Completion returns telemetry
- **WHEN** the wrapper returns a completion response
- **THEN** the response includes cache state, cache key, prompt processing timing, save or restore timing where applicable, and fallback reason where applicable
- **AND** the response telemetry includes wrapper-visible boundary timings for request parsing or prompt assembly, cache lookup, prefix priming, slot save, slot restore, direct or tail completion, and total wrapper time where each phase is applicable

#### Scenario: Debug telemetry requested
- **WHEN** a request enables debug telemetry
- **THEN** the response body includes a machine-readable cache debug object in addition to normal response fields
- **AND** the debug object includes a `boundary_timings` object with phase durations in milliseconds where available

#### Scenario: Boundary phase is not observable
- **WHEN** a lower-level phase such as SSD read throughput, tensor serialization, or accelerator upload is not observable from the wrapper
- **THEN** the wrapper does not invent a value for that phase

### Requirement: Compare wrapper cache value
The system SHALL provide a smoke benchmark for the wrapper cache path.

#### Scenario: Run wrapper smoke benchmark
- **WHEN** the user runs the wrapper benchmark against a workflow fixture
- **THEN** the benchmark compares direct llama.cpp full-prompt calls with wrapper cache-aware calls
- **AND** writes a result JSON that reports cache hit rate, prompt timing, save/restore overhead, net delta, and boundary timing telemetry where available
