# flashcache-correctness-eval-suite Specification Delta

## ADDED Requirements

### Requirement: Support HF KV capsule paper benchmark provenance
The correctness workflow SHALL preserve source-row and transform provenance for HF KV capsule benchmark cases.

#### Scenario: Build benchmark candidates with provenance
- **WHEN** the HF KV capsule benchmark builds IFEval or GraphWalks candidates
- **THEN** each case records source dataset repo, split, revision or snapshot timestamp, source row key or offset, source row hash, stable prefix hash, tail prompt hash, full prompt hash, transform version, prompt protocol version, and scorer version
- **AND** prompt-bearing candidate artifacts are written under ignored Track 01 benchmark paths by default

### Requirement: Support baseline-pass cohort selection by task family
The correctness workflow SHALL select paper-facing cases separately for IFEval and GraphWalks based on full-visible baseline pass.

#### Scenario: Select family cohorts
- **WHEN** full-visible calibration responses have been scored
- **THEN** the workflow writes selected case lists separately by task family
- **AND** records candidate count, selected count, full-visible pass rate, score threshold, rejected case ids, and rejection reasons where available

### Requirement: Score KV capsule control records
The correctness workflow SHALL score primary and secondary KV capsule control records without manual reshaping.

#### Scenario: Score paired control matrix
- **WHEN** response JSONL contains KV capsule control ids for supported correctness cases
- **THEN** the scorer groups records by case id and control id
- **AND** reports quality deltas for restored capsule versus full visible, restored capsule versus native live append, fresh tail versus full visible, and wrong capsule versus full visible
- **AND** records unsupported IFEval checks and GraphWalks parse failures explicitly
