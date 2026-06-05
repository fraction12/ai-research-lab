## ADDED Requirements

### Requirement: Family 2 Structured Retrieval Sequence-State Gate

Track 02 SHALL test structured retrieval using the official native sequence-state route after the Family 1 sequence-file proof.

#### Scenario: Structured retrieval sequence-file pass

- **GIVEN** 30 deterministic fabricated structured lookup cases with answers present only in the prefix
- **WHEN** the Family 2 scale gate runs on `--state-route auto`
- **THEN** the effective route SHALL be recorded
- **AND** `seq_file` SHALL be the primary passing route when the required sequence-file exports are present
- **AND** full-visible SHALL pass all cases before restored capsule results are interpreted
- **AND** fresh tail-only SHALL miss all cases before restored capsule results are interpreted
- **AND** live append SHALL pass all cases before restored capsule results are interpreted
- **AND** restored capsule append SHALL pass all cases before the family is classified as passed

### Requirement: Deterministic Parity Classification

The Family 2 gate SHALL classify deterministic output parity separately from semantic answer-contained scoring.

#### Scenario: Restored capsule semantically passes but hash parity differs

- **GIVEN** full-visible and live append pass all cases
- **AND** restored capsule answer-contained passes all cases
- **WHEN** live-vs-restored response hashes differ for any case
- **THEN** the package SHALL classify the result as a semantic pass with deterministic-parity warning
- **AND** SHALL preserve per-case hash-parity booleans and hashes in sanitized artifacts

### Requirement: Sequence-State Route Fallback Handling

Whole-context state restore SHALL NOT be classified as strong sequence-state success.

#### Scenario: Sequence-file route fails after guards pass

- **GIVEN** full-visible and live append pass all cases
- **AND** restored capsule with `seq_file` fails or is runtime-blocked
- **WHEN** sequence memory exports are available
- **THEN** the runner MAY run one controlled rerun with `--state-route seq-memory`
- **AND** the package SHALL record both route outcomes
- **AND** any whole-context run SHALL be labeled as fallback/diagnostic only

### Requirement: Sanitized Family 2 Artifact Boundary

Committed Family 2 scale artifacts SHALL preserve metrics without prompt-bearing raw evidence.

#### Scenario: Packaging Family 2 scale results

- **WHEN** Family 2 scale results are packaged
- **THEN** committed artifacts SHALL include sanitized summaries, route telemetry, case metrics, capsule contract, failure taxonomy, commands, model info, and artifact manifest
- **AND** committed artifacts SHALL NOT include raw prompts, raw responses, expected answer strings, token ID arrays/slices, generated token arrays/slices, top-k arrays, token piece previews, or state bytes
- **AND** raw prompt-bearing records, console logs, runners, and state files SHALL remain under ignored Track 01 raw/cache paths
