## MODIFIED Requirements

### Requirement: Summarize benchmark result JSON
The system SHALL provide a command-line summarizer for benchmark result JSON files.

#### Scenario: Summarize direct prompt-cache result
- **WHEN** the user provides a llama.cpp prompt-cache benchmark result JSON
- **THEN** the summarizer reports model, fixture, started time, reusable prefix bytes, baseline prompt milliseconds, restored prompt milliseconds, delta milliseconds, ratio, slot file bytes, and result path

#### Scenario: Summarize Flashcache wrapper result
- **WHEN** the user provides a Flashcache wrapper benchmark result JSON
- **THEN** the summarizer reports model, fixture, started time, reusable prefix bytes, direct prompt milliseconds, wrapper prompt milliseconds, delta milliseconds, ratio, cache hit rate, cache states, boundary timing totals where available, and result path

#### Scenario: Missing optional values
- **WHEN** a supported result JSON omits an optional timing, cache, boundary, or artifact field
- **THEN** the summarizer emits `n/a` for that field instead of failing

#### Scenario: Unsupported result JSON
- **WHEN** the user provides a JSON file that does not match a supported benchmark result schema
- **THEN** the summarizer identifies it as unsupported and continues processing other files
