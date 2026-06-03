## ADDED Requirements

### Requirement: Run alternate model and format continuation sanity check
The system SHALL provide a bounded sanity check that compares session-continuation litmus behavior across an alternate local GGUF and an explicit prompt-format variant before lower-level KV/session repair work begins.

#### Scenario: Probe alternate local model
- **WHEN** the alternate model sanity check is executed
- **THEN** it first runs a bounded full-prompt probe against `C:\Users\Dushyant\Documents\vault-mind\vault-mind-q5_k_m.gguf`
- **AND** it records whether the model loaded, whether full prompt passed, and any runtime error before running additional modes

#### Scenario: Run default and transcript-format case sets
- **WHEN** the alternate model full-prompt probe passes
- **THEN** the litmus runs default and transcript-format synthetic secret-token case sets
- **AND** each case set includes full-prompt, live-tail, restored-tail, and fresh-tail modes

#### Scenario: Preserve model sanity artifacts
- **WHEN** the sanity check writes raw prompt and model-output artifacts
- **THEN** raw JSON, logs, slot files, and cache artifacts are written under ignored benchmark result/cache paths
- **AND** committed Track 02 artifacts record exact raw paths, hashes, commands, model/backend metadata, prompts or prompt hashes, and interpretation

#### Scenario: Classify sanity outcome
- **WHEN** full-prompt passes and fresh-tail fails for a case set
- **THEN** live-tail and restored-tail results classify whether the tail-only raw completion failure generalizes across the alternate model/format control
- **AND** the interpretation explicitly distinguishes model weakness, prompt protocol issue, scorer/parser brittleness, session/cache semantic issue, position/compatibility issue, and runtime/storage issue

#### Scenario: Preserve Option 3 direction
- **WHEN** the sanity check is complete
- **THEN** the system records whether the result changes the confidence level for tail-only raw `/completion`
- **AND** it does not claim tail-only `/completion` is the intended mechanism path for Track 02 lower-level repair work
