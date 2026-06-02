# ollama-workflow-benchmark Specification

## Purpose
Measure local Ollama prompt evaluation cost for repeated agent workflow prompts and compare full-prompt, exact-replay, and proxy prefix-reuse strategies before investing in SSD-backed KV persistence.

## Requirements
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

### Requirement: Track real fixture provenance

The benchmark SHALL preserve provenance notes for real workflow fixtures that are distilled from repository campaigns or archived specs.

#### Scenario: Fixture includes source artifacts

- **WHEN** a workflow fixture is based on a real campaign
- **THEN** the fixture records the source repository, source artifact paths, and the campaign decisions that shaped the prompt

#### Scenario: Fixture protects raw transcript absence

- **WHEN** the original raw chat transcript is not stored
- **THEN** the fixture records that it is a sanitized distilled prompt rather than a verbatim transcript

### Requirement: Compare full-prompt and prefix-context strategies

The benchmark SHALL compare a full-prompt baseline against a prefix-context strategy for the same workflow fixture.

#### Scenario: Run comparison mode

- **WHEN** the user selects comparison mode
- **THEN** the system runs each selected scenario with the full prompt baseline
- **AND** the system primes a reusable prefix context and runs each selected scenario tail with that context

#### Scenario: Report strategy deltas

- **WHEN** comparison mode completes
- **THEN** the system reports baseline prompt evaluation cost, prefix-context prime cost, prefix-context tail cost, amortized prefix-context cost, and the delta between strategies

### Requirement: Build reusable prefix from stable blocks

The prefix-context strategy SHALL build the reusable prefix from stable or semi-stable blocks common to the selected scenarios.

#### Scenario: Common reusable blocks exist

- **WHEN** selected scenarios share stable or semi-stable blocks
- **THEN** the system primes Ollama with those blocks before running volatile tails

#### Scenario: No reusable prefix exists

- **WHEN** selected scenarios do not share any stable or semi-stable blocks
- **THEN** the system exits with an actionable error explaining that prefix-context comparison requires reusable blocks

### Requirement: Mark Ollama context reuse as a proxy

The benchmark SHALL mark prefix-context results as a proxy measurement rather than proof of SSD-backed KV reuse.

#### Scenario: Prefix-context result is persisted

- **WHEN** the system writes prefix-context result metadata
- **THEN** the metadata records that Ollama `context` reuse is deprecated API behavior and not persistent SSD-backed KV cache

### Requirement: Avoid accidental exact replay in repeated samples

The benchmark SHALL support repeated samples that vary the volatile request so exact-prompt replay does not hide changed-tail prompt cost.

#### Scenario: Vary repeated runs

- **WHEN** the user enables varied repeated runs
- **THEN** the system appends a benchmark-only run marker to each full prompt or changed-tail prompt
- **AND** the system does not append that marker to the reusable prefix prime

### Requirement: Preserve reusable prefix alignment

The benchmark SHALL keep volatile benchmark metadata after reusable prompt blocks so the measured prompt layout reflects stable-prefix reuse.

#### Scenario: Assemble scenario prompt

- **WHEN** the system assembles a scenario prompt
- **THEN** stable and semi-stable blocks appear before scenario-specific benchmark metadata

### Requirement: Generate prefix manifests

The benchmark SHALL generate a machine-readable prefix manifest for selected workflow scenarios.

#### Scenario: Build manifest for selected scenarios

- **WHEN** the benchmark prepares selected workflow scenarios
- **THEN** the system records common reusable block names, block byte sizes, block hashes, prefix prompt bytes, prefix prompt hash, model name, fixture hash, and scenario tail hashes

#### Scenario: Persist manifest on request

- **WHEN** the user requests a prefix manifest file
- **THEN** the system writes the manifest to a local JSON file for later comparison

### Requirement: Compare warm and restarted prompt sequences

The benchmark SHALL compare aligned full-prompt execution while Ollama stays warm against execution with Ollama stopped before each prompt.

#### Scenario: Run restart comparison

- **WHEN** the user selects restart comparison mode
- **THEN** the system runs selected scenarios once in a warm sequence
- **AND** the system runs selected scenarios again after stopping the selected Ollama model before each scenario

#### Scenario: Report persistence gap

- **WHEN** restart comparison completes
- **THEN** the system reports warm prompt evaluation cost, restarted prompt evaluation cost, and restarted-minus-warm prompt evaluation delta

### Requirement: Restart actions are explicit in results

The benchmark SHALL record restart actions used during restart comparison.

#### Scenario: Ollama stop is invoked

- **WHEN** the benchmark stops an Ollama model for restart comparison
- **THEN** the system records the model name, command result, elapsed time, and whether the stop happened before a sequence or before a scenario
