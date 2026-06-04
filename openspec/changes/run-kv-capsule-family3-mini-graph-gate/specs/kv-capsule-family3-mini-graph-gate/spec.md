# kv-capsule-family3-mini-graph-gate Specification

## ADDED Requirements

### Requirement: Run Family 3 only after Family 2 capsule pass
The Track 02 workflow SHALL run the Family 3 mini-graph capsule gate only after the Family 2 structured-retrieval capsule gate has passed.

#### Scenario: Use Family 2 canonical native route
- **WHEN** the Family 3 mini-graph gate is run
- **THEN** it uses the native direct C API route proven in the Family 1 and Family 2 gates
- **AND** it uses `add_special=true` for full prompt and prefix prefill starts
- **AND** it uses `add_special=false` for appended tail tokens

#### Scenario: Keep task family narrow
- **WHEN** the Family 3 mini-graph gate is run
- **THEN** it uses 5 deterministic fabricated mini-graph cases
- **AND** it does not run GraphWalks, noiseless evidence, server bridge, Family 4, or broad benchmarks

### Requirement: Construct hidden-prefix mini-graph cases
The Family 3 gate SHALL use mini-graph prefixes where the expected answer is available only in the prefix graph and not in the tail.

#### Scenario: Stage A one-hop cases
- **WHEN** Stage A cases are generated
- **THEN** exactly 3 cases use invented node names and relation labels for one-hop relation retrieval
- **AND** each prefix includes distractor edges
- **AND** each tail asks for one exact answer by source node and relation label
- **AND** the expected answer is absent from the tail text

#### Scenario: Stage B two-hop cases
- **WHEN** Stage B cases are generated
- **THEN** exactly 2 cases use invented node names and relation labels for two-hop path retrieval
- **AND** each prefix includes distractor edges
- **AND** each tail asks for the exact answer reached by following two named relations
- **AND** the expected answer is absent from the tail text

#### Scenario: Commit only sanitized case data
- **WHEN** Family 3 case data is committed
- **THEN** committed artifacts include hashes, counts, timings, booleans, classifications, stage labels, hop counts, and metadata only
- **AND** they omit raw prompt text, raw responses, expected answer strings, token ID arrays, generated token slices, top-k arrays, and state bytes

### Requirement: Enforce Stage A controls before Stage B
The Family 3 gate SHALL complete Stage A ordered controls and hard stop rules before running Stage B.

#### Scenario: Stage A full visible guard
- **WHEN** the gate starts
- **THEN** `native_full_visible_prefix_plus_tail` runs first on the 3 Stage A one-hop mini-graph cases
- **AND** if any case fails answer-contained scoring, the workflow stops as `family3_stage_a_full_visible_guard_failed`

#### Scenario: Stage A fresh tail negative control
- **WHEN** Stage A full-visible guard passes
- **THEN** `native_fresh_tail_only` runs on the same 3 Stage A tails
- **AND** if it contains any expected answer, the workflow stops or quarantines as `family3_stage_a_fresh_tail_leakage_or_scorer_issue`

#### Scenario: Stage A live append before restored capsule
- **WHEN** Stage A fresh-tail negative control passes
- **THEN** `native_live_append_tail_only` prefills prefix state in a live native context, appends only tail tokens, and generates
- **AND** if any case fails answer-contained scoring, the workflow stops as `family3_stage_a_live_append_protocol_blocker`

#### Scenario: Stage A restored capsule
- **WHEN** Stage A live append passes on all 3 cases
- **THEN** `native_restored_capsule_append_tail_only` saves prefix state, restores it into a fresh context, appends only tail tokens, and generates
- **AND** if any case fails answer-contained scoring, the workflow classifies `family3_stage_a_restored_capsule_one_hop_failure` and stops before Stage B
- **AND** if all 3 cases pass, the workflow advances to Stage B

### Requirement: Enforce Stage B controls only after Stage A restored capsule pass
The Family 3 gate SHALL run Stage B only after Stage A restored capsule passes and SHALL classify two-hop failures separately.

#### Scenario: Stage B full visible guard
- **WHEN** Stage A restored capsule passes
- **THEN** `native_full_visible_prefix_plus_tail` runs first on the 2 Stage B two-hop mini-graph cases
- **AND** if any case fails answer-contained scoring, the workflow stops as `family3_stage_b_full_visible_guard_failed`

#### Scenario: Stage B fresh tail negative control
- **WHEN** Stage B full-visible guard passes
- **THEN** `native_fresh_tail_only` runs on the same 2 Stage B tails
- **AND** if it contains any expected answer, the workflow stops or quarantines as `family3_stage_b_fresh_tail_leakage_or_scorer_issue`

#### Scenario: Stage B live append before restored capsule
- **WHEN** Stage B fresh-tail negative control passes
- **THEN** `native_live_append_tail_only` prefills prefix state in a live native context, appends only tail tokens, and generates
- **AND** if any case fails answer-contained scoring, the workflow stops as `family3_stage_b_live_append_protocol_blocker`

#### Scenario: Stage B restored capsule
- **WHEN** Stage B live append passes on both cases
- **THEN** `native_restored_capsule_append_tail_only` saves prefix state, restores it into a fresh context, appends only tail tokens, and generates
- **AND** if any case fails answer-contained scoring, the workflow classifies `family3_stage_b_restored_capsule_two_hop_failure`
- **AND** if both cases pass, the workflow classifies `family3_restored_capsule_mini_graph_passed`

### Requirement: Keep Family 3 artifacts sanitized and auditable
The Family 3 gate SHALL commit only sanitized Track 02 summaries and keep prompt-bearing or reconstructable evidence ignored.

#### Scenario: Commit required summaries
- **WHEN** the gate is packaged
- **THEN** committed artifacts include `README.md`, `summary.json`, `case-metrics.json`, `failure-classifications.json`, `commands.md`, `model-info.json`, `artifact-manifest.json`, and `capsule-contract.md` if restored capsule ran
- **AND** `capsule-contract.md` is omitted if restored capsule did not run

#### Scenario: Keep raw artifacts ignored
- **WHEN** raw prompts, responses, logs, runner scripts, or state bytes are written
- **THEN** they are written under `research/01-ssd-native-inference-current/benchmarks/kv-capsule-family3-mini-graph-gate-2026-06-04/raw/`
- **AND** git status shows those files are ignored

#### Scenario: Interpret Family 3 outcome narrowly
- **WHEN** the Family 3 result is packaged
- **THEN** it states whether Stage A and Stage B advanced beyond each stop rule
- **AND** it frames any pass as a 5-case fabricated mini-graph mechanism gate, not a GraphWalks or broad quality claim
