## ADDED Requirements

### Requirement: Generate size-targeted large-prefix fixtures
The system SHALL generate benchmark fixture variants whose reusable stable and semi-stable prefix approximates requested byte targets.

#### Scenario: Generate fixture ladder
- **WHEN** the user requests large-prefix fixtures for one or more target sizes
- **THEN** the generator writes one fixture JSON per target size
- **AND** each fixture records target prefix bytes, actual prefix bytes, source fixture, and generated expansion block names

#### Scenario: Preserve volatile turns
- **WHEN** the generator creates a large-prefix fixture from the Printy workflow fixture
- **THEN** the generated fixture preserves the original volatile changed-tail blocks and scenario ordering
- **AND** generated expansion blocks appear before volatile blocks in the reusable prefix

### Requirement: Use only sanitized benchmark context
The fixture generator SHALL avoid private or secret material in generated fixtures.

#### Scenario: Allowlisted source corpus
- **WHEN** the generator collects context for expansion blocks
- **THEN** it reads only repo-local allowlisted benchmark, docs, OpenSpec, and fixture files

#### Scenario: Secret pattern detected
- **WHEN** generated fixture text matches a configured secret, token, private key, or private chat identifier pattern
- **THEN** the generator fails before writing the fixture unless explicitly run in dry-run inspection mode

### Requirement: Record context-budget guidance
Generated fixtures SHALL include enough metadata to choose safe local-model context sizes.

#### Scenario: Context guidance is recorded
- **WHEN** a fixture is generated
- **THEN** its metadata records reusable prefix bytes, largest scenario prompt bytes, estimated token count, and recommended llama.cpp context size

#### Scenario: Prompt may exceed context budget
- **WHEN** a target prefix would likely exceed the maximum configured context size
- **THEN** the generator fails with an actionable error naming the target size and budget

### Requirement: Support local dry-run inspection
The generator SHALL support inspection without writing fixture files.

#### Scenario: Dry run
- **WHEN** the user runs the generator with dry-run enabled
- **THEN** it reports the fixture names, target sizes, actual prefix bytes, safety status, and recommended context sizes without writing output files
