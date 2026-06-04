# kv-capsule-scaled-amortized-benchmark-campaign Specification

## ADDED Requirements

### Requirement: Define a gated scaled KV capsule campaign
The Track 02 workflow SHALL define a gated benchmark campaign that measures restored KV/state capsule quality and repeated-query economics without making broad quality claims.

#### Scenario: Use the canonical native route
- **WHEN** the campaign is run
- **THEN** it uses the native direct C API route proven by the native/server parity bridge and Family 1/2 gates
- **AND** it uses `add_special=true` for full prompt and prefix prefill starts
- **AND** it uses `add_special=false` for appended tail tokens

#### Scenario: Preserve narrow research framing
- **WHEN** campaign results are packaged
- **THEN** they frame restored capsule reuse as a reusable-context quality and economics mechanism
- **AND** they do not claim that KV cache makes the model inherently smarter
- **AND** they do not claim GraphWalks, noiseless-evidence, or broad benchmark correctness

### Requirement: Run Phase 1 scaled structured retrieval
The campaign SHALL run deterministic scaled structured-retrieval units before any reasoning or agent-context units.

#### Scenario: Construct reusable structured prefixes
- **WHEN** Phase 1 cases are generated
- **THEN** they use reusable synthetic structured prefixes at row-count sizes 25, 100, and 250 unless runtime or context constraints stop the campaign earlier
- **AND** each size uses one reusable prefix and 10 deterministic tail queries
- **AND** each expected answer appears only in the prefix, not in the tail
- **AND** a 500-row run is not executed without later explicit approval

#### Scenario: Enforce Phase 1 ordered controls by size
- **WHEN** a Phase 1 size is run
- **THEN** `native_full_visible_prefix_plus_tail` runs for all 10 queries first
- **AND** `native_fresh_tail_only` runs only if full-visible passes 10/10 answer-contained
- **AND** `native_live_append_tail_only` runs only if fresh-tail contains 0/10 expected answers
- **AND** `native_restored_capsule_append_tail_only` runs only if live append passes 10/10 answer-contained

#### Scenario: Reuse one capsule per Phase 1 prefix
- **WHEN** restored capsule controls run for a Phase 1 size
- **THEN** the workflow builds one prefix capsule for that reusable prefix
- **AND** it restores the same capsule for each query
- **AND** it records one-time capsule build cost separately from per-query restore, tail append, and decode cost

### Requirement: Calculate amortized capsule economics
The campaign SHALL calculate amortized full-resend and capsule costs for repeated queries over the same reusable prefix.

#### Scenario: Produce break-even curves
- **WHEN** a Phase 1 size or Phase 3 agent-context unit has interpretable restored capsule results
- **THEN** the workflow calculates full resend total as `N * mean_full_visible_per_query_wall_ms`
- **AND** it calculates capsule total as `one_time_prefix_prefill_save_build_ms + N * mean_restored_query_wall_ms`
- **AND** it reports N values 1, 2, 5, 10, 20, and 50
- **AND** it reports prompt tokens avoided as `N * prefix_tokens`
- **AND** it reports capsule byte counts and measured break-even query count where available

### Requirement: Run Phase 2 calibration before reasoning capsule controls
The campaign SHALL calibrate graph/reasoning prompt formats with full-visible controls before any reasoning capsule control is interpreted.

#### Scenario: Calibrate one-hop reasoning templates
- **WHEN** Phase 2 starts
- **THEN** the workflow runs full-visible-only calibration across tiny one-hop prompt formats such as adjacency table, edge triples table, simple sentence facts, and JSON-ish object/list
- **AND** it uses at most 20 deterministic calibration cases unless explicitly narrowed by cost
- **AND** it selects a template only if full-visible reaches 100% answer-contained

#### Scenario: Stop Phase 2 if calibration fails
- **WHEN** no Phase 2 template reaches 100% full-visible answer-contained
- **THEN** the workflow stops Phase 2 as `reasoning_full_visible_calibration_failed`
- **AND** it does not run reasoning live append or restored capsule controls

#### Scenario: Run reasoning capsule controls only after calibration
- **WHEN** a Phase 2 template reaches 100% full-visible calibration
- **THEN** the workflow runs the same four ordered controls on the calibrated one-hop template
- **AND** it runs a tiny two-hop reasoning set only if the one-hop restored capsule control passes and the two-hop full-visible guard passes
- **AND** it does not import GraphWalks cases

### Requirement: Run Phase 3 agent-context benchmark only after Phase 1 capsule pass
The campaign SHALL run a small local-agent-like context benchmark only if Phase 1 has at least one interpretable restored capsule pass.

#### Scenario: Build sanitized agent-context prefix
- **WHEN** Phase 3 is eligible
- **THEN** the workflow builds a reusable prefix from repo-local context such as Track 02 README, relevant experiment summaries, AGENTS/handoff constraints, and compact synthetic policy or tool-schema blocks
- **AND** it records source file names, hashes, token counts, and prompt hashes in committed summaries
- **AND** it keeps prompt-bearing context and raw responses ignored

#### Scenario: Gate Phase 3 controls
- **WHEN** Phase 3 runs
- **THEN** it uses 8 to 10 deterministic tail questions or tasks whose answer or policy is available only from the prefix
- **AND** it runs full-visible, fresh-tail, live-append, and restored-capsule controls in order
- **AND** it interprets restored capsule only if full-visible passes, fresh-tail is clearly lower quality or misses, and live append passes

### Requirement: Enforce stop rules and failure classification
The campaign SHALL stop or quarantine each unit at the first violated gate and classify the result truthfully.

#### Scenario: Full-visible guard fails
- **WHEN** full-visible answer-contained scoring fails for a phase, size, template, or task family
- **THEN** restored capsule semantics for that unit are not interpreted
- **AND** the unit is classified with the relevant full-visible guard failure

#### Scenario: Fresh-tail leakage occurs
- **WHEN** fresh-tail contains an expected answer for a unit
- **THEN** the unit is quarantined as leakage or scorer issue
- **AND** restored capsule semantics for that unit are not interpreted

#### Scenario: Live append fails
- **WHEN** live append fails after full-visible and fresh-tail gates pass
- **THEN** restored capsule semantics for that unit are not interpreted
- **AND** the unit is classified as a live-append protocol blocker or narrower observed blocker

#### Scenario: Restored capsule fails after valid guards
- **WHEN** restored capsule fails after full-visible and live append pass
- **THEN** the unit is classified as restored capsule semantic or scale failure
- **AND** the workflow does not claim KV capsules fail in general

### Requirement: Keep campaign artifacts sanitized and auditable
The campaign SHALL commit only sanitized Track 02 summaries and keep prompt-bearing or reconstructable evidence ignored.

#### Scenario: Commit required summaries
- **WHEN** the campaign is packaged
- **THEN** committed artifacts include `README.md`, `summary.json`, `phase-results.json`, `case-metrics.json`, `amortization.json`, `failure-classifications.json`, `commands.md`, `model-info.json`, and `artifact-manifest.json`
- **AND** `capsule-contract.md` or `capsule-contracts.json` is included only for phases where restored capsule actually runs

#### Scenario: Keep raw artifacts ignored
- **WHEN** raw prompts, responses, logs, runner scripts, token arrays, or state bytes are written
- **THEN** they are written under `research/01-ssd-native-inference-current/benchmarks/kv-capsule-scaled-amortized-benchmark-campaign-2026-06-04/raw/`
- **AND** git status shows those files are ignored

#### Scenario: Exclude prompt-bearing data from commits
- **WHEN** campaign artifacts are committed
- **THEN** committed artifacts include hashes, counts, timings, booleans, classifications, and metadata only
- **AND** they omit raw prompt text, raw responses, expected answer strings, token ID arrays, generated token slices, top-k arrays, and state bytes
