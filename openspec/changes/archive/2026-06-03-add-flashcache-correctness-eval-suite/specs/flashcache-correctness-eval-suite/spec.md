## ADDED Requirements

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
