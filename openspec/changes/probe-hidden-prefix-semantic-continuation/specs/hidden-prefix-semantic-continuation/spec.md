# hidden-prefix-semantic-continuation Specification

## ADDED Requirements

### Requirement: Run deterministic hidden-prefix semantic-continuation probes
The Track 02 workflow SHALL test whether the pinned lower-level llama.cpp + GPT-OSS restore path creates semantically usable hidden-prefix state before interpreting further GraphWalks hidden-prefix failures.

#### Scenario: Codeword sanity controls
- **WHEN** the semantic-continuation probe runs
- **THEN** it evaluates at least 10 deterministic codeword variants
- **AND** each variant compares `full_visible_prefix_plus_tail`, `fresh_tail_only`, and `restored_hidden_prefix_plus_tail`
- **AND** the workflow records both strict exact-match and answer-contained/extractable-answer metrics
- **AND** the restored hidden-prefix condition is considered semantically valid only when full visible contains or exactly returns the expected codeword, fresh tail-only misses, and restored hidden-prefix contains or exactly returns the expected codeword

#### Scenario: Stop after decisive codeword gate
- **WHEN** the 10-codeword gate shows full visible contains the expected codeword in all cases, fresh tail-only contains it in none, and restored hidden-prefix contains it in none while matching fresh tail-only responses
- **THEN** the workflow may stop before the key/value ladder
- **AND** it records that the key/value ladder was skipped because the codeword semantic-continuation gate was decisive

#### Scenario: Key/value retrieval controls
- **WHEN** the codeword ladder is run
- **THEN** the probe also evaluates at least 20 deterministic key/value retrieval variants
- **AND** each variant uses a prefix with 20 random key/value pairs generated from a recorded deterministic seed
- **AND** each variant compares the same three controls used by the codeword ladder
- **AND** the scorer records exact match and normalized response text for the requested value

#### Scenario: Tiny structured probe gate
- **WHEN** codeword and key/value restored hidden-prefix controls both pass
- **THEN** the workflow may run a tiny deterministic structured `parents` probe with 5-10 edges and the same three controls
- **AND** if either simple ladder fails, the workflow skips the structured probe and records the skip reason

### Requirement: Preserve semantic-continuation telemetry and artifacts
The semantic-continuation probe SHALL preserve raw prompt-bearing artifacts locally and commit only summary artifacts.

#### Scenario: Record per-control telemetry
- **WHEN** a probe control is executed
- **THEN** the workflow records exact response string, normalized response string, strict exact-match, answer-contained/extractable-answer, output status (`exact_only`, `contains_with_extra_text`, `missing`, or `malformed`), prompt hash, prompt token count, predicted token count, prompt processing milliseconds, decode milliseconds, total latency, slot save/restore success, `n_saved`, `n_restored`, `n_written`, `n_read`, setup wall milliseconds, save milliseconds, restore milliseconds, and prime prompt milliseconds where available
- **AND** unavailable telemetry is recorded as unavailable rather than fabricated

#### Scenario: Keep prompt-bearing artifacts ignored
- **WHEN** prompts, raw outputs, cache files, logs, or prompt-bearing response files are written
- **THEN** they are written under `research/01-ssd-native-inference-current/benchmarks/hidden-prefix-semantic-continuation-2026-06-04/`
- **AND** those paths are covered by git ignore rules

#### Scenario: Commit Track 02 summaries
- **WHEN** the probe completes or stops at a valid blocker
- **THEN** committed Track 02 artifacts are written under `research/02-quality-gated-stateful-kv-reuse/experiments/hidden-prefix-semantic-continuation-2026-06-04/`
- **AND** the artifact set includes `README.md`, `summary.json`, `case-metrics.json`, `failure-classifications.json`, `commands.md`, `model-info.json`, and `artifact-manifest.json`

### Requirement: Classify semantic-continuation outcomes
The semantic-continuation probe SHALL classify each control and the aggregate outcome using the defined failure taxonomy.

#### Scenario: Classify simple hidden-prefix failures
- **WHEN** full visible passes and restored hidden-prefix fails a codeword case
- **THEN** the outcome is classified as `semantic_restore_failure`
- **AND** the summary states that the current protocol/backend usage is not a valid semantic continuation mechanism

#### Scenario: Classify visible answers with extra text
- **WHEN** full visible contains the expected answer but does not satisfy strict exact-match
- **THEN** the workflow classifies the control as `prompt_protocol_issue_contains_answer`
- **AND** the aggregate semantic-continuation decision uses the answer-contained/extractable-answer metric rather than strict exact-match alone

#### Scenario: Classify expected fresh misses
- **WHEN** fresh tail-only cannot recover a hidden value and does not pass
- **THEN** the control is classified as `fresh_tail_expected_miss`

#### Scenario: Classify prompt and runtime blockers
- **WHEN** full visible fails on simple controls
- **THEN** the workflow classifies the issue as `prompt_protocol_issue` or `parse_failure` before interpreting hidden restore
- **AND** when server, slot, cache file, or telemetry failures prevent a valid restored-prefix result, the workflow classifies the issue as `runtime_or_slot_failure`
