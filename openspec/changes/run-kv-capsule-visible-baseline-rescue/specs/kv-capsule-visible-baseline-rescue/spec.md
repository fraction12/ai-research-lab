# kv-capsule-visible-baseline-rescue Specification

## ADDED Requirements

### Requirement: Define focused visible-baseline rescue campaign
The Track 02 workflow SHALL define a focused campaign that rescues and attributes full-visible retrieval baselines before any restored KV/state capsule interpretation.

#### Scenario: Start from tiny visible baselines
- **WHEN** Phase A runs
- **THEN** it tests 1, 3, 5, and 10 row retrieval units
- **AND** it queries every row for scales up to 10
- **AND** it attempts 15 or 25 rows only after a smaller scale passes

#### Scenario: Try required rescue variant families
- **WHEN** visible calibration runs
- **THEN** it tries a Family-2-positive-control style format, ultra-simple codebook lines, XML/tagged records, short TSV records, natural sentence needles, and single/three-record sanity variants
- **AND** it records sanitized pass counts and failure classes for each attempt

#### Scenario: Promote only reliable visible units
- **WHEN** a variant/scale is promoted
- **THEN** full-visible answer-contained is 100%
- **AND** exact or normalized scoring is 100%
- **AND** any answer-channel parser fix is performed during calibration and rerun before promotion
- **AND** the prompt, data, query set, scorer, and decode budget are frozen before evidence controls

### Requirement: Audit route controls before attribution
The campaign SHALL include route controls that separate prompt/model weakness from native-route/protocol weakness.

#### Scenario: Run known-positive route checks
- **WHEN** route controls run
- **THEN** they include native ctypes full-visible checks for known-positive Family 1 and Family 2 style cases when cheap
- **AND** they record whether the pinned native route still passes these simple controls

#### Scenario: Compare alternate route when available
- **WHEN** an installed llama.cpp alternate route such as llama-cli or llama-server is available without downloads
- **THEN** the campaign may run the exact same full-visible prompt through that route
- **AND** it records the route, command, prompt hash, response hash, score, and availability
- **AND** it does not install or download new models without approval

### Requirement: Run capsule evidence only on promoted units
The campaign SHALL run live/restored capsule controls only after a visible unit is promoted and fresh-tail leakage is absent.

#### Scenario: Run ordered evidence controls
- **WHEN** a unit is promoted
- **THEN** controls run in order: `native_full_visible_prefix_plus_tail`, `native_fresh_tail_only`, `native_live_append_tail_only`, and `native_restored_capsule_append_tail_only`
- **AND** restored capsule is interpreted only if full-visible and live append pass
- **AND** fresh-tail leakage quarantines the unit

#### Scenario: Push scale after smaller mechanism floor
- **WHEN** a 1-row or 3-row unit passes restored capsule
- **THEN** the campaign may push to 5, 10, 15, and 25 rows
- **AND** it records the highest reliable full-visible, live-append, and restored-capsule scale

### Requirement: Calculate minimal amortization for passing capsule units
The campaign SHALL calculate repeated-query economics only for restored-capsule-passing units.

#### Scenario: Produce break-even curves
- **WHEN** restored capsule passes for a promoted unit
- **THEN** the workflow reports one-time prefix prefill/save/build cost, per-query restore/tail/decode cost, capsule bytes, state bytes, and break-even N values 1, 2, 5, 10, 20, 50, and 100
- **AND** it reports quality and latency economics separately

### Requirement: Keep artifacts sanitized and auditable
The campaign SHALL commit only sanitized Track 02 summaries and keep prompt-bearing raw evidence ignored.

#### Scenario: Restrict runner surface
- **WHEN** the raw runner is prepared
- **THEN** it exposes only explicit rescue campaign and raw-only smoke modes
- **AND** it exposes no executable bridge, Family 1/2/3 benchmark, GraphWalks, broad-benchmark, or noiseless-evidence path

#### Scenario: Commit required summaries
- **WHEN** the campaign is packaged
- **THEN** committed artifacts include `README.md`, `summary.json`, `phase-results.json`, `calibration-results.json`, `case-metrics.json`, `route-controls.json`, `amortization.json`, `failure-classifications.json`, `commands.md`, `model-info.json`, and `artifact-manifest.json`
- **AND** capsule contract files are included only if restored capsule controls run

#### Scenario: Exclude raw evidence from commits
- **WHEN** artifacts are committed
- **THEN** raw prompts, raw responses, expected answer strings, token ID arrays, generated token arrays/slices, top-k arrays, and state bytes are omitted
- **AND** the raw Track 01 path is ignored by git
