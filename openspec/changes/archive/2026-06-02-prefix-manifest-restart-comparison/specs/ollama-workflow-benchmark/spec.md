## ADDED Requirements

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
