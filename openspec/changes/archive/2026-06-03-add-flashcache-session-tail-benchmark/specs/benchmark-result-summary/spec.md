## MODIFIED Requirements

### Requirement: Summarize benchmark result JSON
The system SHALL provide command-line tooling for turning benchmark result JSON files into compact comparison reports and reproducible research figures.

#### Scenario: Summarize direct prompt-cache result
- **WHEN** the user provides a llama.cpp prompt-cache benchmark result JSON
- **THEN** the summarizer reports model, fixture, started time, reusable prefix bytes, baseline prompt milliseconds, restored prompt milliseconds, delta milliseconds, ratio, slot file bytes, and result path

#### Scenario: Summarize Flashcache wrapper result
- **WHEN** the user provides a Flashcache wrapper benchmark result JSON
- **THEN** the summarizer reports model, fixture, started time, selected server mode, selected cache mode, reusable prefix bytes, direct prompt milliseconds, wrapper prompt milliseconds, delta milliseconds, ratio, cache hit rate, cache states, boundary timing totals, server-version timing totals where available, server context timing totals where available, session setup timing totals where available, slot file bytes where available, and result path

#### Scenario: Missing optional values
- **WHEN** a supported result JSON omits an optional timing, cache, boundary, server mode, cache mode, server-version, session setup, or artifact field
- **THEN** the summarizer emits `n/a` for that field instead of failing

#### Scenario: Unsupported result JSON
- **WHEN** the user provides a JSON file that does not match a supported benchmark result schema
- **THEN** the summarizer identifies it as unsupported and continues processing other files

#### Scenario: Generate research figures
- **WHEN** the user runs the benchmark graph generator
- **THEN** it reads the current benchmark JSON files and emits SVG, PDF, and PNG chart assets with non-overlapping labels, clear measured/projection distinction, and a compact computed-data JSON artifact
