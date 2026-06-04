# kv-capsule-calibrated-a-to-e-campaign Specification

## ADDED Requirements

### Requirement: Define a calibrated A-to-E KV capsule campaign
The Track 02 workflow SHALL define a calibrated campaign that measures restored KV/state capsule quality and repeated-query economics only after visible baselines are made reliable.

#### Scenario: Use the canonical native route
- **WHEN** the campaign is run
- **THEN** it uses the native direct C API route proven by the native/server parity bridge and Family 1/2 gates
- **AND** it uses `add_special=true` for full prompt and prefix prefill starts
- **AND** it uses `add_special=false` for appended tail tokens
- **AND** it chunks long prefill/decode work so native batches do not exceed the pinned runner's `n_batch=512` limit

#### Scenario: Preserve narrow research framing
- **WHEN** campaign results are packaged
- **THEN** they frame restored capsule reuse as reusable-context quality and economics evidence
- **AND** they do not claim that KV cache makes the model inherently smarter
- **AND** they do not claim GraphWalks, noiseless-evidence, or broad benchmark correctness

### Requirement: Calibrate visible baselines before evidence promotion
The campaign SHALL include a visible-baseline calibration phase that can iterate benchmark variants before any capsule evidence unit is frozen.

#### Scenario: Try systematic calibration variants
- **WHEN** Phase A runs
- **THEN** it may test multiple prefix formats, query styles, decode budgets, output protocols, scoring/parsing rules, scales, and query positions
- **AND** it records sanitized summaries for both failed and promoted attempts
- **AND** it keeps raw prompts, expected answers, responses, token arrays, and logs ignored

#### Scenario: Promote only reliable full-visible units
- **WHEN** a calibration variant is considered for evidence
- **THEN** full-visible answer-contained scoring must pass 10/10
- **AND** exact or normalized-exact scoring must be high enough to support the scorer
- **AND** if exact output is low due harmless formatting, the output protocol or scorer is fixed during calibration and rerun before promotion

#### Scenario: Freeze promoted evidence units
- **WHEN** a unit is promoted from calibration to evidence
- **THEN** its prompt format, data format, query set, answer protocol, scoring/parser rule, and decode budget are frozen
- **AND** subsequent evidence controls do not mutate the unit to rescue failures

### Requirement: Run semantic capsule ladders on promoted retrieval units
The campaign SHALL run ordered native controls on promoted retrieval units and classify each gate outcome.

#### Scenario: Run controls in order
- **WHEN** Phase B evaluates a promoted retrieval unit
- **THEN** `native_full_visible_prefix_plus_tail` runs first
- **AND** `native_fresh_tail_only` runs after the full-visible guard passes
- **AND** `native_live_append_tail_only` runs after fresh-tail leakage is absent
- **AND** `native_restored_capsule_append_tail_only` runs after live append passes

#### Scenario: Continue after a failed promoted unit
- **WHEN** a promoted unit fails unexpectedly during evidence
- **THEN** the failure is retained as evidence with a failure class
- **AND** the campaign may return to calibration to promote another variant or scale
- **AND** the failed evidence unit is not silently rewritten

### Requirement: Search retrieval scale boundaries
The campaign SHALL search the reliable scale boundary for full-visible, live append, and restored capsule controls.

#### Scenario: Push required retrieval scales where feasible
- **WHEN** Phase C runs after a smaller retrieval unit works
- **THEN** it attempts scales 10, 25, 50, and 100 rows where feasible
- **AND** it may attempt 250 rows only as a stretch after lower scales produce interpretable data
- **AND** it does not run 500 rows without later explicit approval

#### Scenario: Report highest reliable control scale
- **WHEN** campaign results are packaged
- **THEN** they report the highest reliable full-visible scale
- **AND** they report the highest reliable native live-append scale
- **AND** they report the highest reliable restored-capsule scale
- **AND** they distinguish prompt/model/scorer failures from restored-capsule failures

### Requirement: Calculate amortized capsule economics
The campaign SHALL calculate amortized full-resend and capsule costs for repeated queries over passing restored-capsule units.

#### Scenario: Produce break-even curves
- **WHEN** a retrieval or agent-context unit has interpretable restored capsule results
- **THEN** the workflow calculates full resend total as `N * mean_full_visible_per_query_wall_ms`
- **AND** it calculates capsule total as `one_time_prefix_prefill_save_build_ms + N * mean_restored_query_wall_ms`
- **AND** it reports N values 1, 2, 5, 10, 20, 50, and 100
- **AND** it reports prompt tokens avoided as `N * prefix_tokens`
- **AND** it reports capsule byte counts, restore byte counts, and break-even query count where available

#### Scenario: Keep quality and economics separate
- **WHEN** restored capsule quality passes but wall-time economics are unfavorable
- **THEN** the workflow reports quality pass and latency-negative economics separately
- **AND** it does not hide restore overhead behind prompt-token savings

### Requirement: Run agent-context benchmark after retrieval capsule pass
The campaign SHALL run a small local-agent-like context benchmark only after at least one retrieval restored-capsule ladder passes.

#### Scenario: Calibrate agent-context tasks first
- **WHEN** Phase E starts
- **THEN** it builds 8 to 10 deterministic tasks whose answer or policy is available only from the prefix
- **AND** it calibrates full-visible task format, wording, answer protocol, source subset, and scoring before promotion
- **AND** it preserves failed calibration attempts as sanitized summaries

#### Scenario: Run agent-context evidence after promotion
- **WHEN** an agent-context unit is promoted
- **THEN** it runs full-visible, fresh-tail, live-append, and restored-capsule controls in order
- **AND** it records quality retained, token/time avoided, capsule size, and amortized break-even curves
- **AND** it keeps prompt-bearing context and raw outputs ignored

### Requirement: Enforce runner and artifact boundaries
The campaign SHALL keep model-bearing execution scoped to the calibrated campaign and commit only sanitized Track 02 artifacts.

#### Scenario: Restrict runner CLI surface
- **WHEN** the raw runner is prepared
- **THEN** the only model-bearing CLI mode is an explicit calibrated campaign mode
- **AND** raw-only smoke modes may remain
- **AND** the CLI exposes no server, bridge, Family 1, Family 2, Family 3, GraphWalks, noiseless-evidence, or broad-benchmark execution path

#### Scenario: Commit required summaries
- **WHEN** the campaign is packaged
- **THEN** committed artifacts include `README.md`, `summary.json`, `phase-results.json`, `calibration-results.json`, `case-metrics.json`, `amortization.json`, `failure-classifications.json`, `commands.md`, `model-info.json`, and `artifact-manifest.json`
- **AND** `capsule-contract.md` or `capsule-contracts.json` is included only for units where restored capsule actually runs

#### Scenario: Keep raw artifacts ignored
- **WHEN** raw prompts, responses, logs, runner scripts, token arrays, or state bytes are written
- **THEN** they are written under `research/01-ssd-native-inference-current/benchmarks/kv-capsule-calibrated-a-to-e-campaign-2026-06-04/raw/`
- **AND** git status shows those files are ignored

#### Scenario: Exclude prompt-bearing data from commits
- **WHEN** campaign artifacts are committed
- **THEN** committed artifacts include hashes, counts, timings, booleans, classifications, and metadata only
- **AND** they omit raw prompt text, raw responses, expected answer strings, token ID arrays, generated token slices, top-k arrays, and state bytes
