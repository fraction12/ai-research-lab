# kv-capsule-family2-structured-retrieval-gate Specification

## ADDED Requirements

### Requirement: Run Family 2 only after Family 1 capsule pass
The Track 02 workflow SHALL run the Family 2 structured-retrieval capsule gate only after the Family 1 simple codeword capsule gate has passed.

#### Scenario: Use Family 1 canonical native route
- **WHEN** the Family 2 structured-retrieval gate is run
- **THEN** it uses the native direct C API route proven in the Family 1 gate
- **AND** it uses `add_special=true` for full prompt and prefix prefill starts
- **AND** it uses `add_special=false` for appended tail tokens

#### Scenario: Keep task family narrow
- **WHEN** the Family 2 structured-retrieval gate is run
- **THEN** it uses 5 deterministic fabricated structured-retrieval cases
- **AND** it does not run mini graph, GraphWalks, noiseless evidence, server bridge, or broad benchmarks

### Requirement: Construct hidden-prefix structured retrieval cases
The Family 2 gate SHALL use structured prefixes where the expected answer is available only in the prefix text and not in the tail.

#### Scenario: Prefix contains multiple facts
- **WHEN** a Family 2 case is generated
- **THEN** its prefix contains multiple fabricated key-value facts or compact table rows
- **AND** the tail asks for one exact value by key or row
- **AND** the requested answer value is absent from the tail text

#### Scenario: Commit only sanitized case data
- **WHEN** Family 2 case data is committed
- **THEN** committed artifacts include hashes, counts, timings, booleans, classifications, and metadata only
- **AND** they omit raw prompt text, raw responses, expected answer strings, token ID arrays, generated token slices, top-k arrays, and state bytes

### Requirement: Enforce ordered structured-retrieval controls
The Family 2 gate SHALL enforce ordered controls and hard stop rules before interpreting restored capsule semantics.

#### Scenario: Full visible guard
- **WHEN** the gate starts
- **THEN** `native_full_visible_prefix_plus_tail` runs first on 5 deterministic structured-retrieval cases
- **AND** if any case fails answer-contained scoring, the workflow stops as `family2_full_visible_guard_failed`

#### Scenario: Fresh tail negative control
- **WHEN** full-visible guard passes
- **THEN** `native_fresh_tail_only` runs on the same 5 tails
- **AND** if it contains any expected answer, the workflow stops or quarantines as `family2_fresh_tail_leakage_or_scorer_issue`

#### Scenario: Live append before restored capsule
- **WHEN** fresh-tail negative control passes
- **THEN** `native_live_append_tail_only` prefills prefix state in a live native context, appends only tail tokens, and generates
- **AND** if any case fails answer-contained scoring, the workflow stops as `family2_live_append_protocol_blocker`

#### Scenario: Restored capsule after live append
- **WHEN** live append passes on all 5 cases
- **THEN** `native_restored_capsule_append_tail_only` saves prefix state, restores it into a fresh context, appends only tail tokens, and generates
- **AND** it records state byte counts, save/restore timings, `n_past_before_tail_append`, and `generation_start_pos`

### Requirement: Interpret Family 2 outcome narrowly
The Family 2 gate SHALL classify the result according to the first stop rule reached and SHALL avoid broader claims.

#### Scenario: Restored capsule passes
- **WHEN** full-visible, fresh-tail, live-append, and restored-capsule controls all satisfy their advance conditions
- **THEN** the workflow classifies `family2_restored_capsule_structured_retrieval_passed`
- **AND** it stops before Family 3, GraphWalks, noiseless evidence, or broad benchmarks

#### Scenario: Restored capsule fails after live append
- **WHEN** live append passes but restored capsule append fails
- **THEN** the workflow classifies `family2_restored_capsule_structured_retrieval_failure` or a narrower save/restore protocol blocker if telemetry supports it
- **AND** it does not claim KV capsules fail in general

### Requirement: Keep Family 2 artifacts sanitized and auditable
The Family 2 gate SHALL commit only sanitized Track 02 summaries and keep prompt-bearing or reconstructable evidence ignored.

#### Scenario: Commit required summaries
- **WHEN** the gate is packaged
- **THEN** committed artifacts include `README.md`, `summary.json`, `case-metrics.json`, `failure-classifications.json`, `commands.md`, `model-info.json`, `artifact-manifest.json`, and `capsule-contract.md` if restored capsule ran
- **AND** `capsule-contract.md` is omitted if restored capsule did not run

#### Scenario: Keep raw artifacts ignored
- **WHEN** raw prompts, responses, logs, runner scripts, or state bytes are written
- **THEN** they are written under `research/01-ssd-native-inference-current/benchmarks/kv-capsule-family2-structured-retrieval-gate-2026-06-04/raw/`
- **AND** git status shows those files are ignored
