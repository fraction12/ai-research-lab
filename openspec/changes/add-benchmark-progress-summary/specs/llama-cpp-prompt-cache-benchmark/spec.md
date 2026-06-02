## ADDED Requirements

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
