# kv-capsule-family1-semantic-gate Specification

## ADDED Requirements

### Requirement: Run Family 1 capsule gate only after native/server parity
The Track 02 workflow SHALL run the Family 1 capsule semantic gate only after native full-visible parity has passed on the simple codeword prompt shape.

#### Scenario: Use parity-proven prompt shape
- **WHEN** the Family 1 capsule gate is run
- **THEN** it uses the `prior_known_good_simple_codeword` prompt shape from the native/server parity bridge
- **AND** it does not use nonce prompts, GraphWalks prompts, or broad benchmark prompts

#### Scenario: Choose canonical tokenization route
- **WHEN** the Family 1 capsule gate runs native controls
- **THEN** it records which `add_special` route is selected and why
- **AND** it uses `add_special=false` for appended tail tokens

### Requirement: Enforce ordered capsule controls
The Family 1 gate SHALL enforce ordered controls and hard stop rules before interpreting restored capsule semantics.

#### Scenario: Full visible guard
- **WHEN** the gate starts
- **THEN** `native_full_visible_prefix_plus_tail` runs first on 3 deterministic simple codeword cases
- **AND** if any case fails answer-contained scoring, the workflow stops as `native_full_visible_guard_failed`

#### Scenario: Fresh tail negative control
- **WHEN** full-visible guard passes
- **THEN** `native_fresh_tail_only` runs on the same 3 tails
- **AND** if it contains the expected answer, the workflow stops or quarantines as `fresh_tail_leakage_or_scorer_issue`

#### Scenario: Live append before restored capsule
- **WHEN** fresh-tail negative control passes
- **THEN** `native_live_append_tail_only` prefills prefix state in a live native context, appends only tail tokens, and generates
- **AND** if it fails, the workflow stops as `native_live_append_protocol_blocker`

#### Scenario: Restored capsule after live append
- **WHEN** live append passes
- **THEN** `native_restored_capsule_append_tail_only` saves prefix state, restores it into the tested context, appends only tail tokens, and generates
- **AND** it records state byte counts, save/restore timings, `n_past_before_tail_append`, and `generation_start_pos`

### Requirement: Keep Family 1 artifacts sanitized
The Family 1 gate SHALL commit only sanitized Track 02 summaries and keep prompt-bearing or reconstructable evidence ignored.

#### Scenario: Commit sanitized summaries
- **WHEN** the gate is packaged
- **THEN** committed artifacts include `README.md`, `summary.json`, `case-metrics.json`, `failure-classifications.json`, `commands.md`, `model-info.json`, `artifact-manifest.json`, and `capsule-contract.md` if restored capsule ran
- **AND** committed summaries omit raw prompts, raw responses, token ID slices, generated token slices, top-k arrays, and state bytes

#### Scenario: Keep raw artifacts ignored
- **WHEN** raw prompts, responses, logs, runner scripts, or state bytes are written
- **THEN** they are written under `research/01-ssd-native-inference-current/benchmarks/kv-capsule-family1-semantic-gate-2026-06-04/raw/`
- **AND** git status shows those files are ignored
