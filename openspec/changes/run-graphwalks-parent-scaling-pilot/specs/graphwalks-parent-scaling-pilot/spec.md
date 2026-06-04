# graphwalks-parent-scaling-pilot Specification

## Purpose
Define the controlled 50-case GraphWalks `parents` scaling pilot for Track 02, including sampling, controls, metrics, artifact layout, failure taxonomy, and conservative interpretation rules.

## ADDED Requirements

### Requirement: Build deterministic GraphWalks parents pilot cohort
The pilot SHALL build a deterministic 50-case cohort from GraphWalks `parents` rows only.

#### Scenario: Sample pilot cases
- **WHEN** the pilot case builder runs
- **THEN** it writes a 50-case GraphWalks `parents` case set under the ignored Track 01 input artifact path
- **AND** records source dataset id, source row id, task family, operation, target node, stable prefix hash, full prompt hash, prefix length, and sampling method for each case
- **AND** uses deterministic ordering or a recorded deterministic seed

#### Scenario: Annotate buckets after sampling
- **WHEN** the case set is built
- **THEN** each case records buckets for answer size, evidence edge count, evidence bytes, duplicate edges, relevant edge position where derivable, prefix length, and full-visible pass/fail once known
- **AND** empty parent-set cases, if present, are recorded as `0 parents` rather than merged into the `1 parent` bucket
- **AND** the summary records if bucket annotation was post-sampling rather than pre-stratified

### Requirement: Extract non-oracle incoming-edge evidence
The pilot SHALL extract visible evidence slices from the stable graph prefix and requested target node, without using the reference answer set.

#### Scenario: Extract parents evidence
- **WHEN** evidence is extracted for a `parents` case
- **THEN** the extractor uses the graph prefix text and requested target node to select incoming edge lines
- **AND** it does not read reference answer nodes to build the evidence slice
- **AND** it records evidence lines, evidence hash, edge count, evidence bytes, token count if available, and duplicate-edge metadata

### Requirement: Run five controls per sampled case
The pilot SHALL run the paired five-control matrix for each sampled case unless a stop rule is triggered and recorded.

#### Scenario: Run control matrix
- **WHEN** the pilot executes a sampled case
- **THEN** it attempts `full_visible_compact_prompt`, `hidden_prefix_session_tail`, `hidden_prefix_compact_tail_no_evidence`, `hidden_prefix_compact_visible_evidence_tail`, and `fresh_compact_visible_evidence_only`
- **AND** every response record identifies the control id, case id, prompt hash, raw response path, scoring result, timing metadata, and parse/truncation flags

#### Scenario: Preserve pinned lower-level path
- **WHEN** the pilot runs model responses
- **THEN** it uses the pinned GPT-OSS llama.cpp runner and model paths unless a hard blocker is recorded
- **AND** records model hash, runner hash, backend flags, command line, context size, temperature, prediction cap, cache directory, and slot/cache telemetry where applicable

### Requirement: Score and classify pilot outcomes
The pilot SHALL score each control and classify failures in a way that separates quality, protocol, scorer, cache, position, and runtime causes.

#### Scenario: Score GraphWalks parents responses
- **WHEN** a response is scored
- **THEN** the scorer records correctness pass/fail, precision, recall, F1 where available, parsed nodes, reference nodes, parse errors, and truncation status

#### Scenario: Classify failures
- **WHEN** a case-control response fails or parses ambiguously
- **THEN** the failure classification uses one of: model weakness, prompt protocol issue, scorer/parser brittleness, session/cache semantic issue, position/compatibility issue, runtime/storage issue, or ambiguity
- **AND** the classification records evidence supporting the label

### Requirement: Produce Track 02 summary artifacts
The pilot SHALL preserve prompt-bearing artifacts locally and commit Track 02 summaries.

#### Scenario: Write summary artifact set
- **WHEN** the pilot completes or stops under a recorded stop rule
- **THEN** it writes `README.md`, `summary.json`, `case-metrics.json`, `bucket-analysis.json`, `failure-classifications.json`, `evidence-slices.json`, `commands.md`, `model-info.json`, and `artifact-manifest.json` under the Track 02 experiment directory
- **AND** the artifact manifest records all raw prompt-bearing paths and hashes under ignored Track 01 benchmark directories

#### Scenario: Include required analysis views
- **WHEN** the summary is produced
- **THEN** it includes all sampled cases, full-visible-pass subset, hidden-prefix-fail subset, repairable hidden-prefix failures, cases where fresh evidence-only equals hidden-prefix plus evidence, and cases where compact no-evidence repairs hidden-prefix failure

### Requirement: Keep interpretation conservative
The pilot SHALL avoid broad benchmark or pure-KV claims.

#### Scenario: Interpret pilot result
- **WHEN** the Track 02 README or summary interprets the pilot
- **THEN** it states that the result is a controlled GraphWalks `parents` pilot only
- **AND** if compact visible evidence repairs most hidden-prefix failures, frames the finding as support for role-aware context compilation / quality-gated context scheduling
- **AND** if fresh evidence-only matches hidden-prefix plus evidence, states that hidden KV may not materially contribute for this task family
- **AND** if compact no-evidence repairs many failures, identifies prompt protocol as a major confounder

### Requirement: Enforce stop rules without silent design changes
The pilot SHALL stop rather than silently narrow the study when runtime or blocker conditions prevent the planned matrix.

#### Scenario: Runtime or repeated blocker triggers partial pilot
- **WHEN** the full 50-case five-control matrix is too slow or hits repeated runtime blockers
- **THEN** the operator may stop after a deterministic smaller slice such as 10 or 20 cases
- **AND** the summary records the blocker, completed controls, elapsed time, estimated full runtime, and exact deviation from the planned design
- **AND** it does not present the partial slice as the planned 50-case result
