## ADDED Requirements

### Requirement: Define a paper-grade evaluation campaign
The lab SHALL maintain an OpenSpec-defined campaign for turning the Gemma 4 Code-mode + KV capsule pilot result into paper-grade evidence.

#### Scenario: Campaign is planned before execution
- **WHEN** model-bearing paper runs are requested
- **THEN** the orchestrator uses this campaign's stage order, controls, metrics, stop rules, and artifact schema
- **AND** does not start broad model execution from an ad hoc chat plan

#### Scenario: Pilot evidence is referenced
- **WHEN** the campaign interprets prior Gemma 4 and BFCL results
- **THEN** it labels those results as mechanism, handmade viability, or pilot external benchmark evidence
- **AND** does not blend pilot rows into the final primary paper cohort unless the cohort is explicitly rerun under this campaign

### Requirement: Run staged paper execution
The campaign SHALL execute in explicit stages: readiness, BFCL expansion, stateful-agent follow-on, model matrix, amortization, and paper package.

#### Scenario: Stage 0 readiness runs
- **WHEN** execution begins
- **THEN** the orchestrator records repo revision, dirty state, raw-path ignore status, DushyantPC reachability, GPU status, duplicate process state, model profile resolution, llama.cpp route identity, and validation status
- **AND** writes `execution-readiness.json`

#### Scenario: Stage cannot pass readiness
- **WHEN** DushyantPC, model profile, raw artifact boundary, validation, or duplicate process checks fail
- **THEN** the campaign stops before broad model execution
- **AND** writes a failure classification and next action

### Requirement: Expand BFCL into a paper-grade primary cohort
The campaign SHALL treat BFCL primary-50 as pilot evidence and SHALL run a larger deterministic BFCL cohort for paper-grade claims.

#### Scenario: BFCL candidate calibration runs
- **WHEN** BFCL expansion begins
- **THEN** it materializes a deterministic candidate pool of at least 500 supported rows where available
- **AND** records source revision, row hashes, categories, scorer version, transform version, and prefix-dependency class
- **AND** treats smaller runs such as 50-row pilots, smoke tests, or partial category probes as diagnostic only, not paper calibration

#### Scenario: BFCL primary cohort is selected
- **WHEN** candidate calibration finishes
- **THEN** the target primary cohort is 200 `code_mode_full_visible` passing rows
- **AND** the minimum paper-eligible cohort is 100 `code_mode_full_visible` passing rows
- **AND** selected/rejected/leaked/diagnostic counts are recorded by category
- **AND** the campaign stops short of full paper claims if fewer than 100 clean full-visible-passing rows remain after scorer-support and negative-control filters

#### Scenario: Calibration captures paper metrics
- **WHEN** BFCL candidate calibration runs
- **THEN** each record includes enough data to support paper tables and failure analysis: category, selected/diagnostic status, scorer support, full-visible pass state, live-vs-restored parity fields, restored-only failure flags, fresh-tail leak flags, wrong-capsule leak flags, direct-tool gap fields, compact-evidence effect fields, prompt/token counts, timing, model profile, llama.cpp route identity, capsule metadata, and provenance hashes
- **AND** the calibration summary reports those metrics by category and control before any full paper run begins

### Requirement: Preserve the seven-control ladder
The campaign SHALL run the seven-control ladder for every selected row where the benchmark supports it.

#### Scenario: Selected row is executed
- **WHEN** a selected row runs
- **THEN** records are emitted for `direct_full_visible_tools`, `code_mode_full_visible`, `code_mode_fresh_tail_only`, `code_mode_native_live_append`, `code_mode_restored_kv_capsule`, `code_mode_wrong_capsule_negative`, and `compact_visible_evidence_code_mode`

#### Scenario: Control is unsupported
- **WHEN** a benchmark cannot honestly support a control
- **THEN** the record marks the control unsupported with a reason
- **AND** excludes it from primary parity claims

### Requirement: Gate hidden-state claims on negative controls
The campaign SHALL enforce fresh-tail and wrong-capsule negatives before hidden-state value is claimed.

#### Scenario: Negative control leaks
- **WHEN** fresh-tail or wrong-capsule passes on a prefix-dependent row
- **THEN** the row is excluded from hidden-prefix value claims
- **AND** the failure is classified as tail leakage, scorer looseness, wrong-capsule identity failure, benchmark ambiguity, or protocol bug

#### Scenario: Negative controls remain closed
- **WHEN** negative controls remain closed for a selected cohort
- **THEN** the summary may state that the cohort required hidden stable context
- **AND** reports the closure rate and every exception

### Requirement: Compare restored capsule to native live append
The campaign SHALL use native live append as the semantic ceiling for restored KV capsule claims.

#### Scenario: Restored and native agree
- **WHEN** `code_mode_restored_kv_capsule` and `code_mode_native_live_append` have the same benchmark pass/fail result on a selected row
- **THEN** the record stores scorer result, parsed call hashes, normalized response hash, generated-token hash where available, prompt-token deltas, capsule metadata, and timing for both controls

#### Scenario: Restored-only failure occurs
- **WHEN** native live append passes but restored capsule fails
- **THEN** the row is classified as a restored-only failure unless evidence supports parser, scorer, model, or runtime instability
- **AND** the non-inferiority margin is recalculated for the cohort

### Requirement: Add a stateful-agent follow-on benchmark
The campaign SHALL include at least one stateful-agent follow-on benchmark after BFCL unless source/scorer integration is blocked.

#### Scenario: ToolSandbox smoke runs
- **WHEN** BFCL expansion is summarized and ToolSandbox source/scorer readiness passes
- **THEN** a 10-20 task ToolSandbox smoke runs through all supported controls
- **AND** the summary records whether ToolSandbox is eligible for a 50-100 task primary follow-on

#### Scenario: Follow-on blocked
- **WHEN** ToolSandbox and tau-bench/tau2 cannot be integrated without changing benchmark semantics
- **THEN** the campaign records the blocker
- **AND** limits the paper to BFCL plus controlled mechanism evidence unless Sir approves a narrower technical report

### Requirement: Run a model matrix
The campaign SHALL define which models support which controls before model comparison.

#### Scenario: Primary local model runs
- **WHEN** primary paper runs execute
- **THEN** Gemma 4 12B uses the pinned local profile and the working llama.cpp sequence-file route

#### Scenario: Non-KV model baseline runs
- **WHEN** a stronger model or API baseline lacks the same KV state route
- **THEN** it may run full-visible or direct-tool quality controls only
- **AND** the summary does not compare its missing restored-capsule controls as failures

### Requirement: Separate semantic and efficiency claims
The campaign SHALL report semantic quality separately from speed, token, and amortization results.

#### Scenario: Efficiency is measured
- **WHEN** efficiency results are reported
- **THEN** they include stable prefix tokens, volatile tail tokens, full visible prompt tokens, restored visible prompt tokens, prompt eval time, decode time, capsule save time, capsule restore time, capsule bytes, total wall time, and repeated-tail amortization

#### Scenario: Speedup is unsupported
- **WHEN** restored execution does not beat full-visible resend after overhead under realistic repeated-tail workloads
- **THEN** the campaign marks speedup claims disallowed
- **AND** may still claim semantic viability if quality gates passed

### Requirement: Support periodic checkups during long runs
The campaign SHALL make long model runs inspectable without changing their state.

#### Scenario: Checkup requested
- **WHEN** Sir asks for a run checkup
- **THEN** the orchestrator reports process health, GPU status, current row/control counts, failure counts, last JSONL timestamp, artifact sizes, and active stop-rule triggers
- **AND** appends the checkup to `periodic-checkups.jsonl`

#### Scenario: Checkup finds a stop-rule trigger
- **WHEN** a checkup finds duplicate processes, stalled output, GPU failure, repeated parser/scorer bugs, or negative-control leakage over threshold
- **THEN** the orchestrator stops or pauses according to the campaign stop rules
- **AND** records the action in the checkup log and summary artifacts
