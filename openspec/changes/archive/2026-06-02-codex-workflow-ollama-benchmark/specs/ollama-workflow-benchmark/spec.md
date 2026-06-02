## ADDED Requirements

### Requirement: Benchmark repeated workflow prompts

The system SHALL provide a CLI benchmark that runs repeated agent workflow prompts against a local Ollama model.

#### Scenario: Run benchmark with default fixture

- **WHEN** the user runs the benchmark without selecting a custom fixture
- **THEN** the system sends a Codex-style DeepClean workflow prompt fixture to Ollama for each configured scenario

#### Scenario: Run benchmark with selected model

- **WHEN** the user provides a model name
- **THEN** the system sends all benchmark requests to that Ollama model

### Requirement: Separate stable and volatile prompt blocks

The benchmark fixture SHALL represent the workflow as named stable, semi-stable, and volatile prompt blocks.

#### Scenario: Build scenario prompt

- **WHEN** a benchmark scenario is prepared
- **THEN** the system assembles the prompt from the fixture blocks selected by that scenario

#### Scenario: Estimate reusable prefix size

- **WHEN** a scenario includes stable or semi-stable blocks
- **THEN** the system reports their byte sizes and hashes so future cache manifests can reuse the same structure

### Requirement: Record Ollama timing metrics

The benchmark SHALL record Ollama usage metrics for each run.

#### Scenario: Ollama returns timing metrics

- **WHEN** Ollama returns a non-streaming generate response
- **THEN** the system records total duration, load duration, prompt eval count, prompt eval duration, eval count, and eval duration

#### Scenario: Derive readable timing values

- **WHEN** a run completes
- **THEN** the system reports durations in milliseconds and prompt/eval throughput in tokens per second where counts are available

### Requirement: Persist machine-readable results

The benchmark SHALL write machine-readable result artifacts for later comparison.

#### Scenario: Complete benchmark run

- **WHEN** all configured scenarios complete
- **THEN** the system writes a JSON result file that includes input metadata, per-run timing metrics, prompt block hashes, and summary statistics

### Requirement: Fail clearly when Ollama is unavailable

The benchmark SHALL fail with an actionable message when the local Ollama API cannot be reached.

#### Scenario: Ollama API is unreachable

- **WHEN** the benchmark cannot connect to the configured Ollama host
- **THEN** the system exits non-zero and explains how to start or configure Ollama
