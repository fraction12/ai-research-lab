## ADDED Requirements

### Requirement: Select external benchmark sources
The experiment SHALL use external benchmark-derived tool-use tasks as primary evidence and SHALL record the source, version, license note, category, and scorer for every source used.

#### Scenario: Source audit is created
- **WHEN** the benchmark source audit runs
- **THEN** it records BFCL as the first target source
- **AND** records tau-bench/tau2-bench and ToolSandbox as staged follow-on candidates
- **AND** includes source URLs, local checkout or dataset revision, license notes, available categories, scorer availability, and integration status

#### Scenario: Unsupported benchmark source
- **WHEN** a benchmark source lacks usable row provenance or scorer semantics
- **THEN** the experiment marks that source as blocked or diagnostic
- **AND** does not use it for primary paper claims

### Requirement: Materialize benchmark-derived cases
The experiment SHALL materialize candidate cases from external benchmark rows using deterministic transforms that preserve source provenance and prompt hashes.

#### Scenario: Build candidate case
- **WHEN** the materializer converts a benchmark row
- **THEN** the emitted case includes benchmark id, source revision, source row id or deterministic offset, source row hash, task family, benchmark category, stable prefix hash, volatile tail hash, full prompt hash, transform version, scorer version, fields used/excluded, `primary_eligible`, `primary_eligibility_reason`, and `prefix_dependency_class`

#### Scenario: Handmade primary case rejected
- **WHEN** a candidate case lacks external benchmark provenance
- **THEN** the materializer excludes it from primary cohorts
- **AND** records whether it is a synthetic preflight or diagnostic-only case

### Requirement: Preserve the seven-control ladder
The experiment SHALL run the same seven controls for every selected benchmark-derived case unless a control is explicitly marked unsupported with a recorded reason.

#### Scenario: Selected case control matrix
- **WHEN** a case enters a selected external benchmark cohort
- **THEN** the runner emits records for `direct_full_visible_tools`, `code_mode_full_visible`, `code_mode_fresh_tail_only`, `code_mode_native_live_append`, `code_mode_restored_kv_capsule`, `code_mode_wrong_capsule_negative`, and `compact_visible_evidence_code_mode`

#### Scenario: Control unsupported
- **WHEN** a control cannot run for a benchmark source because the source scorer or environment does not support it
- **THEN** the runner records the unsupported reason
- **AND** the summary excludes that control from primary parity claims

### Requirement: Gate primary cohorts on full-visible Code-mode pass
The experiment SHALL compare restored capsules only on rows where `code_mode_full_visible` passes the benchmark scorer.

#### Scenario: Select primary cohort
- **WHEN** candidate calibration finishes
- **THEN** the selected cohort includes only rows whose `code_mode_full_visible` record passes
- **AND** the summary records candidate count, full-visible pass count, selected count, rejected count, and whether the cohort is paper-eligible or diagnostic-only

#### Scenario: Insufficient full-visible pass count
- **WHEN** a benchmark family cannot produce the target number of full-visible-passing rows
- **THEN** the experiment runs only a diagnostic subset
- **AND** does not claim family-level restored-capsule parity

### Requirement: Enforce negative controls
The experiment SHALL treat fresh-tail and wrong-capsule passes as leakage or protocol failures for prefix-dependent cases.

#### Scenario: Fresh tail leaks answer
- **WHEN** `code_mode_fresh_tail_only` passes a candidate row intended to be prefix-dependent
- **THEN** the row is marked non-prefix-dependent, leaked, or ambiguous
- **AND** the row is excluded from primary hidden-prefix value claims unless manually justified in the summary

#### Scenario: Wrong capsule passes
- **WHEN** `code_mode_wrong_capsule_negative` passes a selected row
- **THEN** the experiment fails the negative-control gate for that row
- **AND** classifies whether the cause is tail leakage, scorer looseness, capsule mismatch failure, or benchmark ambiguity

### Requirement: Compare restored capsule against native live append
The experiment SHALL use `code_mode_native_live_append` as the semantic ceiling for `code_mode_restored_kv_capsule`.

#### Scenario: Restored matches live append
- **WHEN** both live append and restored capsule run on a selected row
- **THEN** the result records benchmark pass/fail, parsed tool calls, normalized response hash, generated-token hash where available, prompt-token deltas, capsule metadata, and timing for both controls

#### Scenario: Restored diverges from live append
- **WHEN** restored capsule fails or diverges while native live append passes
- **THEN** the failure is classified as a persistence/capsule semantic issue unless evidence supports another category

### Requirement: Preserve benchmark scoring semantics
The experiment SHALL use benchmark-native scoring where available and SHALL document any scorer adapter limitations.

#### Scenario: Score benchmark response
- **WHEN** a model response is scored
- **THEN** the record includes raw benchmark scorer output or deterministic adapter output, pass/fail, expected function/tool calls where allowed, unsupported scorer features, parser status, and scorer version

#### Scenario: Scorer changed
- **WHEN** a scorer adapter changes between runs
- **THEN** the experiment records a new scorer version
- **AND** does not blend old and new scorer outputs without labeling them separately

#### Scenario: Partial scorer support
- **WHEN** a benchmark category lacks native or faithful category-specific scoring
- **THEN** the experiment marks that category diagnostic-only
- **AND** blocks that category from model smoke and primary parity claims until scorer support is proven

### Requirement: Report host repair and finalization boundaries
The experiment SHALL expose parser repair, template aliasing, host-filled arguments, and host finalization as top-level analysis fields so runtime-harness success is not confused with unaided model success.

#### Scenario: Host repair fields recorded
- **WHEN** a control record is emitted
- **THEN** it includes `template`, `template_alias`, `alias_registry_version`, `host_filled_args`, `final_source`, `parse_status`, expected call hash, parsed call hash, expected argument hash, and parsed argument hash

#### Scenario: Host repair dominates
- **WHEN** alias normalization, host-filled arguments, or host answer finalization account for most passing records in a cohort
- **THEN** the summary classifies the finding as runtime-harness or host-repair evidence
- **AND** does not claim unaided model Code-mode success for that cohort

### Requirement: Record paper-grade artifacts
The experiment SHALL emit committed summaries and ignored raw artifacts with enough metadata to reproduce and audit the run.

#### Scenario: Write summary artifacts
- **WHEN** a benchmark run completes or stops under a stop rule
- **THEN** it writes `README.md`, `summary.json`, `source-audit.json`, `candidate-calibration.json`, `case-metrics.json`, `control-matrix.json`, `failure-classifications.json`, `amortization.json`, `model-info.json`, `commands.md`, `artifact-manifest.json`, `paper-methods-notes.md`, and `disallowed-claims.md` under the Track 02 experiment summary path

#### Scenario: Preserve raw artifacts locally
- **WHEN** the runner writes prompt-bearing inputs, raw outputs, capsule files, or large telemetry
- **THEN** it writes them under ignored Track 01 benchmark paths
- **AND** records hashes and local paths in the artifact manifest

### Requirement: Stage execution with stop rules
The experiment SHALL run source audit, adapter dry run, smoke gates, selected cohort, harder benchmark follow-ons, and final synthesis as separate stages.

#### Scenario: Smoke gate fails
- **WHEN** the BFCL 10-case smoke fails a source, adapter, live-append, restored-capsule, or negative-control gate
- **THEN** the runner stops before the selected cohort
- **AND** writes a failure classification and next-action recommendation

#### Scenario: Smoke gate passes
- **WHEN** source audit, adapter dry run, and BFCL smoke gates pass
- **THEN** the orchestrator may run the selected BFCL cohort
- **AND** may plan tau-bench/tau2-bench or ToolSandbox follow-on smokes after the BFCL result is summarized
