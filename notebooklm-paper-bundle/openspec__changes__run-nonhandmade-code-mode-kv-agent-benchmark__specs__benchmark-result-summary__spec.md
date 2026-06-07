## ADDED Requirements

### Requirement: Summarize non-handmade Code-mode KV benchmark results
The summarizer SHALL distinguish non-handmade Code-mode + KV capsule benchmark evidence from handmade viability results and SHALL report outcomes by benchmark source, task family, and control.

#### Scenario: Summarize external control matrix
- **WHEN** the user provides a non-handmade Code-mode KV benchmark summary JSON
- **THEN** the summarizer reports source benchmark, source revision, selected cohort size, full-visible pass count, fresh-tail leak count, wrong-capsule pass count, live/restored parity, restored-only failures, prompt-token reduction, one-shot timing, amortized timing, and artifact manifest path

#### Scenario: Summarize disallowed claims
- **WHEN** a non-handmade benchmark summary contains failed gates or diagnostic-only families
- **THEN** the summarizer reports the disallowed claims alongside allowed paper-facing claims
