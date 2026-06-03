# llama-cpp-prompt-cache-benchmark Specification

## Purpose
Measure whether llama.cpp server can persist and restore reusable workflow prompt state across fresh local server processes before building a custom SSD-native cache layer.
## Requirements
### Requirement: Run llama.cpp prompt cache benchmark

The system SHALL provide a benchmark that runs selected workflow fixture prompts against llama.cpp server.

#### Scenario: Benchmark uses selected fixture

- **WHEN** the user runs the llama.cpp benchmark with a workflow fixture
- **THEN** the system builds a reusable prefix prompt and changed-tail scenario prompts from the fixture
- **AND** the system sends those prompts to llama.cpp server through `/completion`

#### Scenario: Benchmark records prompt timing

- **WHEN** llama.cpp returns completion timing data
- **THEN** the system records prompt processing time, predicted token time, prompt token count, and generated token count where available

### Requirement: Persist and restore slot prompt cache

The benchmark SHALL test llama.cpp slot save and restore behavior for reusable prefix state.

#### Scenario: Save slot cache

- **WHEN** the reusable prefix prompt has been processed in a slot
- **THEN** the benchmark saves that slot's prompt cache to a file
- **AND** records saved-token count, bytes written, and save timing

#### Scenario: Restore slot cache

- **WHEN** the benchmark starts a fresh llama.cpp server for restored-prefix runs
- **THEN** the benchmark restores the saved slot cache before sending changed-tail prompts
- **AND** records restored-token count, bytes read, and restore timing

### Requirement: Compare baseline and restored-prefix runs

The benchmark SHALL compare full-prompt baseline runs against restored-prefix changed-tail runs.

#### Scenario: Compare strategies

- **WHEN** the benchmark completes baseline and restored-prefix runs
- **THEN** the result reports baseline prompt processing cost, restored-prefix prompt processing cost, save/restore overhead, and net delta

### Requirement: Preserve generated artifacts as local outputs

The benchmark SHALL keep generated llama.cpp artifacts out of source control.

#### Scenario: Benchmark writes local artifacts

- **WHEN** the benchmark writes model files, slot cache files, prompt files, or result JSON
- **THEN** those generated paths are covered by git ignore rules

### Requirement: Emit prompt-cache benchmark progress

The llama.cpp prompt-cache benchmark SHALL emit progress output before long-running model/server phases.

#### Scenario: Progress before prefix priming

- **WHEN** the benchmark is about to create and save the reusable prefix slot cache
- **THEN** it prints a progress line identifying the prefix priming phase

#### Scenario: Progress before baseline scenario

- **WHEN** the benchmark is about to run a full-prompt baseline scenario
- **THEN** it prints a progress line identifying the baseline phase and scenario name

#### Scenario: Progress before restored scenario

- **WHEN** the benchmark is about to restore the prefix slot and run a changed-tail scenario
- **THEN** it prints a progress line identifying the restored-prefix phase and scenario name
