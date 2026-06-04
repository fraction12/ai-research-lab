# flashcache-correctness-eval-suite Specification Delta

## ADDED Requirements

### Requirement: Support GraphWalks parents pilot controls
The correctness workflow SHALL support or faithfully record the controlled GraphWalks `parents` scaling pilot without committing prompt-bearing artifacts.

#### Scenario: Compose compact visible-evidence controls
- **WHEN** a Track 02 GraphWalks `parents` pilot needs compact visible-evidence controls
- **THEN** the workflow can compose prompt-bearing local cases for full visible compact prompt, hidden-prefix session tail, hidden-prefix compact no-evidence tail, hidden-prefix compact visible-evidence tail, and fresh compact visible-evidence-only
- **AND** the prompt-bearing local cases are written under ignored Track 01 benchmark paths
- **AND** the workflow records prompt hashes so committed Track 02 summaries can reference them without committing prompt text

#### Scenario: Record lower-level session telemetry
- **WHEN** the pilot uses hidden prefix mechanics
- **THEN** the workflow records session setup, cache directory, slot save/restore or prompt-cache telemetry, prompt token counts, prompt processing milliseconds, predicted token counts, decode milliseconds, and total latency where available
- **AND** it records when any telemetry is unavailable instead of filling false defaults
