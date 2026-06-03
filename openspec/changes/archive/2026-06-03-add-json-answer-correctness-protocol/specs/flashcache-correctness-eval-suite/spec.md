## MODIFIED Requirements

### Requirement: Generate correctness response JSONL
The system SHALL generate model response JSONL records for Flashcache correctness cases.

#### Scenario: Run full-prompt correctness mode
- **WHEN** the user runs the correctness eval runner in full-prompt mode
- **THEN** the system sends each case's `full_prompt` to llama.cpp
- **AND** writes one response JSONL record per case with `case_id`, `mode: "full"`, response text, latency, prompt hash, and timing metadata

#### Scenario: Run session-tail correctness mode
- **WHEN** the user runs the correctness eval runner in session-tail mode
- **THEN** the system primes a llama.cpp slot with the case's `stable_prefix`
- **AND** saves and restores that slot before sending only the case's `tail_prompt`
- **AND** writes one response JSONL record per case with `case_id`, `mode: "session-tail"`, response text, latency, prompt hash, and session setup telemetry

#### Scenario: Run both correctness modes
- **WHEN** the user runs the correctness eval runner in both modes
- **THEN** the system writes full-prompt and session-tail response records that can be consumed by the existing scorer without manual reshaping

#### Scenario: Score generated responses
- **WHEN** the user supplies a score output path while running model responses
- **THEN** the system scores the generated response JSONL against the input cases after generation
- **AND** writes the same score result shape as the standalone score command

#### Scenario: Run constrained JSON answer protocol
- **WHEN** the user runs the correctness eval runner with the JSON answer protocol
- **THEN** the system sends final-answer instructions and a llama.cpp JSON schema constraint requiring an `answer` string
- **AND** stores the extracted `answer` as the response text consumed by scorers
- **AND** preserves the raw model output in the response record for debugging
