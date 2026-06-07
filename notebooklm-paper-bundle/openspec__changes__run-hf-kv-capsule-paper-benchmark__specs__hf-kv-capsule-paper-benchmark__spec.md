# hf-kv-capsule-paper-benchmark Specification

## Purpose

Define the paper-facing Hugging Face benchmark for Track 02 KV capsule semantic continuation, including source datasets, hypotheses, cohorts, controls, metrics, stop rules, artifact boundaries, and conservative interpretation.

## ADDED Requirements

### Requirement: Use Hugging Face benchmark rows for paper claims
The benchmark SHALL use real source rows from `google/IFEval` and `openai/graphwalks` for paper-facing results.

#### Scenario: Materialize HF benchmark candidates
- **WHEN** the benchmark candidate builder runs
- **THEN** it materializes deterministic candidates from `google/IFEval` and `openai/graphwalks`
- **AND** each case records HF repo, split, revision or snapshot timestamp, source row key or offset, row hash, license, task family, and transform version
- **AND** no handmade benchmark cases are included outside the synthetic preflight phase

### Requirement: Keep synthetic gates separate from benchmark evidence
The benchmark SHALL label synthetic codeword and key-value cases as runner preflight only.

#### Scenario: Report synthetic preflight results
- **WHEN** synthetic preflight results are summarized
- **THEN** the summary identifies them as lower-level route validation
- **AND** it does not count them toward HF benchmark pass rates, paper benchmark tables, or task-family quality claims

### Requirement: Gate selected cohorts on full-visible baseline pass
The benchmark SHALL compare KV capsule quality only on cases that pass the full-visible baseline.

#### Scenario: Select paper-facing cases
- **WHEN** full-visible calibration has run for a candidate family
- **THEN** the selected cohort includes only cases that pass the family scorer under `full_visible`
- **AND** the summary records candidate count, selected count, rejected count, full-visible pass rate, and selection criteria
- **AND** if the selected cohort is below the planned count, the summary marks the result as diagnostic rather than family-level parity evidence

### Requirement: Run paired KV capsule controls
The benchmark SHALL run a paired control matrix for every selected case unless a stop rule is triggered.

#### Scenario: Execute primary controls
- **WHEN** a selected case is evaluated
- **THEN** the runner attempts `full_visible`, `fresh_tail_only`, `native_live_append`, `native_restored_capsule_append`, `wrong_capsule_negative`, and `documented_full_prompt_cache_resend`
- **AND** every response record identifies case id, control id, prompt hash, capsule hash where applicable, raw response hash, normalized response hash, scoring result, timing metadata, and failure class

### Requirement: Separate GraphWalks context-compilation controls
The benchmark SHALL keep GraphWalks evidence-slice controls separate from pure KV capsule controls.

#### Scenario: Run GraphWalks secondary controls
- **WHEN** GraphWalks selected cases are evaluated with compact evidence controls
- **THEN** the benchmark records `fresh_compact_evidence_only`, `capsule_plus_compact_evidence_tail`, and `compact_tail_no_evidence` separately from primary KV capsule controls
- **AND** the summary states whether any repair is attributable to evidence scheduling, prompt protocol, hidden KV state, or ambiguity

### Requirement: Measure semantic quality and efficiency
The benchmark SHALL record quality and performance metrics needed to test KV capsule parity and amortization.

#### Scenario: Record per-control metrics
- **WHEN** a control completes
- **THEN** the benchmark records pass/fail, exact match or constraint result, GraphWalks precision/recall/F1 where applicable, IFEval supported checks where applicable, prompt eval tokens and milliseconds, decode tokens and milliseconds, wall time, capsule save and restore time, capsule bytes, prompt-token reduction, and speedup versus full-visible

### Requirement: Enforce predeclared stop rules
The benchmark SHALL stop or downgrade claims when required gates fail.

#### Scenario: Stop after route or semantic gate failure
- **WHEN** synthetic preflight fails, native live append fails on full-visible-passing HF cases, restored capsule diverges from native live append beyond the declared margin, or runtime instability repeats
- **THEN** the run stops before the full matrix or marks the affected family as diagnostic
- **AND** the summary records the failed gate, completed cases, completed controls, raw artifact paths, and next recommended fix

### Requirement: Produce paper-ready summary artifacts
The benchmark SHALL write committed summary artifacts and keep prompt-bearing raw artifacts local.

#### Scenario: Write experiment summary
- **WHEN** the benchmark completes or stops under a recorded stop rule
- **THEN** it writes `README.md`, `summary.json`, `case-metrics.json`, `control-matrix.json`, `candidate-calibration.json`, `amortization.json`, `failure-classifications.json`, `model-info.json`, `commands.md`, `artifact-manifest.json`, and `paper-methods-notes.md` under the Track 02 experiment directory
- **AND** the artifact manifest records prompt-bearing raw paths, hashes, and whether each path is committed or ignored
