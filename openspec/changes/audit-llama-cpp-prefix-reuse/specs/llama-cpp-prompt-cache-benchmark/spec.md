## ADDED Requirements

### Requirement: Audit llama.cpp prefix reuse mechanisms
The system SHALL provide a focused direct llama.cpp prefix-reuse audit that separates exact-repeat prompt-cache behavior from slot restore/full-resend behavior.

#### Scenario: Audit same-server exact repeat
- **WHEN** the prefix-reuse audit runs a long synthetic full prompt twice against one live llama.cpp server
- **THEN** it records raw responses, parsed answers, prompt hashes, wall timing, llama.cpp prompt timing, prompt token counts, and generated token counts for both completions
- **AND** it classifies whether the second exact-repeat call shows useful prompt-work reduction versus the first call

#### Scenario: Audit same-server slot restore
- **WHEN** the prefix-reuse audit primes and saves a synthetic prefix slot in one live llama.cpp server
- **THEN** it restores the saved slot in that same server before resending the full prompt
- **AND** it records slot save/restore telemetry and classifies whether same-server restore/full-resend reduces prompt work versus cold full-prompt execution

#### Scenario: Audit fresh-server slot restore
- **WHEN** the prefix-reuse audit primes and saves a synthetic prefix slot in one llama.cpp server and restores it in a fresh server
- **THEN** it resends the full prompt in the fresh server
- **AND** it records slot save/restore telemetry and classifies whether fresh-server restore/full-resend reduces prompt work versus cold full-prompt execution

#### Scenario: Preserve audit artifacts
- **WHEN** the prefix-reuse audit writes raw outputs, prompts, logs, slot files, summaries, and classifications
- **THEN** prompt-bearing raw artifacts are written under ignored Track 01 benchmark result/cache paths
- **AND** committed Track 02 artifacts record exact raw paths, hashes, commands, model/backend metadata, run classifications, and next-step decisions
