## MODIFIED Requirements

### Requirement: Summarize benchmark result JSON
The system SHALL provide a command-line summarizer for benchmark result JSON files.

#### Scenario: Summarize Flashcache wrapper result
- **WHEN** the user provides a Flashcache wrapper benchmark result JSON
- **THEN** the summarizer reports model, fixture, started time, selected server mode, selected cache mode, reusable prefix bytes, direct prompt milliseconds, wrapper prompt milliseconds, delta milliseconds, ratio, cache hit rate, cache states, boundary timing totals, server-version timing totals where available, server context timing totals where available, and result path

#### Scenario: Missing optional values
- **WHEN** a supported result JSON omits an optional timing, cache, boundary, server mode, cache mode, server-version, or artifact field
- **THEN** the summarizer emits `n/a` for that field instead of failing
