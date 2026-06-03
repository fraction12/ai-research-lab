# flashcache-correctness-eval-suite Specification

## Purpose
Define how Flashcache correctness experiments sample Hugging Face tasks, generate full-prompt and session-tail model responses, score parity, and record enough evidence to judge whether SSD-backed session reuse preserves answer quality.
## Requirements
### Requirement: Declare scoreable Hugging Face datasets
The system SHALL maintain a dataset registry for the first correctness suite.

#### Scenario: List supported correctness datasets
- **WHEN** the user lists correctness-eval datasets
- **THEN** the system reports `google/IFEval`, `openai/mrcr`, and `openai/graphwalks`
- **AND** reports each dataset's license, split, task family, scoring method, and source URL

### Requirement: Materialize correctness eval cases
The system SHALL turn supported dataset rows into Flashcache correctness cases with stable-prefix and changed-tail prompt parts.

#### Scenario: Build eval case
- **WHEN** the user samples a supported dataset
- **THEN** each emitted case includes a stable prefix, tail prompt, full prompt, source dataset id, source row id, scoring metadata, and reference answer metadata
- **AND** the full prompt is reproducibly derived from the stable prefix and tail prompt

#### Scenario: Hugging Face dependency is unavailable
- **WHEN** the user asks to sample remote Hugging Face rows and the optional dataset loader is unavailable
- **THEN** the system fails with a clear dependency error instead of silently producing partial data

### Requirement: Score full-prompt and session-tail responses
The system SHALL score full-prompt and session-tail responses for supported correctness cases.

#### Scenario: Score response pair
- **WHEN** the user provides model responses for the same case in full-prompt and session-tail modes
- **THEN** the system scores each response with the dataset-specific scorer
- **AND** records per-mode score, pass status, score delta, unsupported checks where applicable, and optional latency metadata

#### Scenario: Score MRCR response
- **WHEN** the system scores an MRCR response
- **THEN** it applies the documented reference-string similarity scoring and records the numeric similarity

#### Scenario: Score GraphWalks response
- **WHEN** the system scores a GraphWalks response
- **THEN** it parses the returned node set and records precision, recall, and F1 against the reference nodes

#### Scenario: Score IFEval response
- **WHEN** the system scores an IFEval response
- **THEN** it evaluates supported deterministic instruction checks
- **AND** records unsupported instruction ids rather than pretending the score is complete

### Requirement: Keep generated correctness artifacts local
The system SHALL keep downloaded dataset rows and generated correctness outputs out of source control.

#### Scenario: Write local eval artifacts
- **WHEN** the user materializes correctness cases or writes score results
- **THEN** those artifacts are written under ignored benchmark directories by default

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

### Requirement: Run baseline-pass correctness ladder
The system SHALL provide a correctness ladder that only compares session-tail against full-prompt cases that pass the baseline scorer.

#### Scenario: Select full-prompt passing cases
- **WHEN** the user runs the baseline-pass ladder on a candidate case JSONL file
- **THEN** the system runs full-prompt responses, scores them, and writes a selected case JSONL containing only cases whose full-prompt score passes the configured threshold
- **AND** records the candidate count, selected count, full response path, full score path, and selected case path

#### Scenario: Compare session-tail on selected cases
- **WHEN** at least one full-prompt case passes selection
- **THEN** the system runs session-tail responses only for the selected cases
- **AND** writes a combined parity response JSONL containing selected full responses and selected session-tail responses
- **AND** writes a parity score JSON comparing the two modes

#### Scenario: No baseline cases pass
- **WHEN** no full-prompt case passes selection
- **THEN** the system writes a ladder report showing zero selected cases
- **AND** does not claim session-tail quality parity

### Requirement: Build reusable correctness candidate sets
The system SHALL provide a CLI workflow for building candidate case JSONL files from one or more supported correctness datasets.

#### Scenario: Build mixed candidate file
- **WHEN** the user requests a candidate set with multiple dataset counts
- **THEN** the system samples each requested dataset, converts rows into correctness cases, and writes one combined JSONL case file
- **AND** each case records candidate-builder metadata including sampling profile, dataset offset, and prompt-size filters

#### Scenario: Build easy IFEval candidates
- **WHEN** the user requests the easy IFEval sampling profile
- **THEN** the system only selects supported single-instruction IFEval rows with bounded prompt and parameter complexity
- **AND** the output records that the easy profile was used

### Requirement: Apply dataset-specific answer guidance
The system SHALL include scorer-aligned answer guidance when running the JSON answer protocol.

#### Scenario: JSON answer protocol uses dataset hint
- **WHEN** the user runs a correctness response command with the JSON answer protocol
- **THEN** the prompt includes dataset-specific guidance for the answer string shape
- **AND** the response record identifies which answer hint was used

#### Scenario: Raw answer protocol remains unchanged
- **WHEN** the user runs a correctness response command with the raw answer protocol
- **THEN** the system does not add JSON answer guidance or dataset-specific answer hints
