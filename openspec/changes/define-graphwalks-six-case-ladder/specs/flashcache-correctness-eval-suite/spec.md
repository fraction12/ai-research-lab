## ADDED Requirements

### Requirement: Define focused GraphWalks six-case ladder
The system SHALL define a focused correctness ladder for the six selected GraphWalks cases where the 2026-06-03 full-prompt gate passed and session-tail failed.

#### Scenario: Identify fixed six-case scope
- **WHEN** the focused GraphWalks ladder is prepared
- **THEN** it uses only `graphwalks-6`, `graphwalks-9`, `graphwalks-11`, `graphwalks-13`, `graphwalks-16`, and `graphwalks-19`
- **AND** it records the source evidence path `research/01-ssd-native-inference-current/benchmarks/datasets/flashcache-correctness-parity-2026-06-03/summary.json`
- **AND** it does not include broader IFEval, MRCR, GraphWalks, or mixed benchmark cases

#### Scenario: Run controls in attribution order
- **WHEN** the focused GraphWalks ladder is executed
- **THEN** it runs controls in this order: full-prompt replay variance, visible-prefix/session-formatted control, stronger tail instructions or answer hints, reset/restore sanity checks, scorer/parser brittleness check, and stronger-model control if practical
- **AND** each control records its baseline, expected failure mode, command line, artifact paths, and pass/fail criteria before interpretation

#### Scenario: Stop before broad benchmarks
- **WHEN** the focused GraphWalks ladder is not yet classified
- **THEN** the system does not run broad benchmark suites or claim general session-tail quality from the six-case result

### Requirement: Preserve focused ladder artifacts
The system SHALL preserve exact artifact paths for focused GraphWalks ladder inputs, outputs, summaries, commands, model metadata, prompts, and failure classifications.

#### Scenario: Record prompt-bearing local inputs
- **WHEN** the focused six-case prompt bundle is materialized
- **THEN** prompt-bearing candidate and selected-case JSONL files are written under `research/01-ssd-native-inference-current/benchmarks/correctness-eval-inputs/graphwalks-six-case-ladder-2026-06-03/`
- **AND** the artifact manifest records `case_id`, `dataset_id`, `source_id`, prompt hashes, prompt byte counts, and local file paths

#### Scenario: Record raw control outputs
- **WHEN** a focused ladder control is executed
- **THEN** raw response JSONL, score JSON, ladder report JSON, and slot/cache telemetry are written under `research/01-ssd-native-inference-current/benchmarks/correctness-eval-results/graphwalks-six-case-ladder-2026-06-03/raw/` and `research/01-ssd-native-inference-current/benchmarks/correctness-eval-cache/graphwalks-six-case-ladder-2026-06-03/`
- **AND** each raw response record preserves exact model name or path, quantization when known, backend/runtime command, context size, temperature, predict count, prompt timing, raw response, extracted response, parse error, prompt hashes, and session setup telemetry where applicable

#### Scenario: Record Track 02 summaries
- **WHEN** focused ladder results are summarized
- **THEN** committed Track 02 artifacts are written under `research/02-quality-gated-stateful-kv-reuse/experiments/graphwalks-six-case-ladder-2026-06-03/`
- **AND** the directory includes `README.md`, `commands.md`, `artifact-manifest.json`, `model-info.json`, `summary.json`, `failure-taxonomy.md`, and `failure-classifications.json`

### Requirement: Classify GraphWalks failures by attribution taxonomy
The system SHALL classify each focused GraphWalks case using a failure taxonomy that separates model weakness, prompt protocol, scorer/parser brittleness, session/cache semantics, position/compatibility, and runtime/storage issues.

#### Scenario: Emit taxonomy table
- **WHEN** the focused ladder summary is produced
- **THEN** it includes a taxonomy table with these categories: `model_weakness`, `prompt_protocol_issue`, `scorer_parser_brittleness`, `session_cache_semantic_issue`, `position_compatibility_issue`, and `runtime_storage_issue`
- **AND** each category records the confirming evidence, ruling-out evidence, required controls, and fallback implication

#### Scenario: Classify each case
- **WHEN** all practical controls for a case have completed
- **THEN** `failure-classifications.json` records one classification row per case with `case_id`, `observed_failure`, `primary_class`, `secondary_classes`, `confidence`, `supporting_artifact_paths`, `fallback_recommendation`, and `open_questions`
- **AND** ambiguous cases remain marked `ambiguous` until a control distinguishes the failure source

#### Scenario: Preserve scorer brittleness evidence
- **WHEN** scorer/parser brittleness is checked
- **THEN** the summary records raw model output, extracted answer, parsed node set, reference node set, precision, recall, F1, and any parse error for each case
- **AND** it distinguishes malformed output from a well-formed but semantically wrong node set

### Requirement: Gate harness modifications behind missing controls
The system SHALL avoid modifying Track 01 harness code for the focused GraphWalks ladder unless existing commands cannot express a required control.

#### Scenario: Existing command is sufficient
- **WHEN** an existing `flashcache_correctness_eval.py` command or small local artifact composition can express a focused control
- **THEN** the implementation uses that path without changing Track 01 harness code

#### Scenario: Harness gap is found
- **WHEN** a required focused control cannot be expressed by existing commands or local artifact composition
- **THEN** the implementation records the missing control surface in the Track 02 experiment notes
- **AND** any Track 01 harness change is minimal, tested, and limited to enabling the focused control
