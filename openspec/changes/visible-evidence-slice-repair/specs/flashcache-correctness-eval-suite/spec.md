## ADDED Requirements

### Requirement: Run visible-evidence-slice repair control
The system SHALL define a focused visible-evidence-slice repair control for the six selected GraphWalks cases.

#### Scenario: Use fixed six-case scope
- **WHEN** the visible-evidence-slice repair control is prepared
- **THEN** it uses only `graphwalks-6`, `graphwalks-9`, `graphwalks-11`, `graphwalks-13`, `graphwalks-16`, and `graphwalks-19`
- **AND** it records the imported positive-control path `research/02-quality-gated-stateful-kv-reuse/experiments/gptoss-edge-evidence-2026-06-04/`
- **AND** it does not include broad GraphWalks, IFEval, MRCR, or mixed benchmark cases

#### Scenario: Compare hidden session-tail against visible evidence repair
- **WHEN** the focused repair control is executed
- **THEN** it records a `hidden_prefix_session_tail` result for each case
- **AND** it records a `hidden_prefix_visible_evidence_tail` result for each case using the same hidden prefix setup plus a small visible extracted evidence slice
- **AND** it compares the two controls by correctness, prompt tokens, prompt time, and visible evidence size

#### Scenario: Extract evidence from graph prefix and requested target
- **WHEN** a visible evidence slice is built for a GraphWalks `parents` case
- **THEN** the extraction uses the stable graph prefix and requested target node
- **AND** it does not use the reference answer node set unless the output is explicitly labeled as an oracle control
- **AND** it records evidence edge lines, evidence edge count, evidence byte count, evidence token count when available, and evidence hash

#### Scenario: Preserve focused repair artifacts
- **WHEN** the visible-evidence-slice repair control is summarized
- **THEN** prompt-bearing raw inputs and outputs are written under `research/01-ssd-native-inference-current/benchmarks/correctness-eval-inputs/visible-evidence-slice-repair-2026-06-04/`, `research/01-ssd-native-inference-current/benchmarks/correctness-eval-results/visible-evidence-slice-repair-2026-06-04/raw/`, and `research/01-ssd-native-inference-current/benchmarks/correctness-eval-cache/visible-evidence-slice-repair-2026-06-04/`
- **AND** committed summaries are written under `research/02-quality-gated-stateful-kv-reuse/experiments/visible-evidence-slice-repair-2026-06-04/`
- **AND** the committed summary directory includes `README.md`, `summary.json`, `artifact-manifest.json`, `model-info.json`, `commands.md`, `failure-classifications.json`, and `evidence-slices.json`

#### Scenario: Record model and runtime metadata
- **WHEN** the visible-evidence-slice repair control runs on DushyantPC
- **THEN** each summary records exact model path, model hash, model family, quantization or file type, runner path, runner hash, runner version, command line, backend flags, context size, predict count, temperature, prompt hash, tail hash, and slot/cache telemetry where applicable

#### Scenario: Classify repair outcomes
- **WHEN** focused repair results are interpreted
- **THEN** each case is classified as `model_weakness`, `prompt_protocol_issue`, `scorer_parser_brittleness`, `session_cache_semantic_issue`, `position_compatibility_issue`, `runtime_storage_issue`, `no_failure_observed`, or `ambiguous`
- **AND** the classification records supporting artifact paths, ruled-down classes, confidence, fallback recommendation, and open questions

#### Scenario: Avoid broad benchmark claims
- **WHEN** the visible-evidence-slice repair control passes all six cases
- **THEN** the system reports it as a focused repair result only
- **AND** it does not claim general GraphWalks quality, general local-agent quality, or pure KV cache reuse from the six-case result

### Requirement: Gate visible-evidence harness changes
The system SHALL avoid modifying Track 01 harness code for the visible-evidence-slice repair control unless existing commands and local case composition cannot express the required control.

#### Scenario: Existing composition is sufficient
- **WHEN** a derived case JSONL can express the hidden-prefix plus visible-evidence tail control
- **THEN** the implementation uses local case composition without changing Track 01 harness code

#### Scenario: Harness support is required
- **WHEN** the hidden-prefix plus visible-evidence tail control cannot be expressed by local case composition or existing commands
- **THEN** the implementation records the missing control surface in the Track 02 experiment notes
- **AND** any Track 01 harness change is minimal, tested, and limited to the focused repair control

### Requirement: Run compact-answer visible evidence follow-up
The system SHALL run a focused compact-answer visible evidence follow-up for the two remaining visible-evidence failures.

#### Scenario: Use fixed two-case scope
- **WHEN** the compact-answer visible evidence follow-up is prepared
- **THEN** it uses only `graphwalks-16` and `graphwalks-19`
- **AND** it uses the same extracted evidence lines recorded for those cases in `research/02-quality-gated-stateful-kv-reuse/experiments/visible-evidence-slice-repair-2026-06-04/evidence-slices.json`
- **AND** it does not run broad GraphWalks, IFEval, MRCR, or mixed benchmark cases

#### Scenario: Change prompt protocol only
- **WHEN** the compact-answer visible evidence follow-up is executed
- **THEN** it keeps the same hidden prefix mechanics, model, runner, context size, temperature, predict count, and GPT-OSS llama.cpp flags as the visible-evidence-slice repair control
- **AND** it changes only the tail instructions to require a compact final node list or compact JSON answer with no explanation
- **AND** it records any deviation from those settings as a separate diagnostic condition rather than the main repair result

#### Scenario: Preserve compact repair artifacts
- **WHEN** the compact-answer visible evidence follow-up is summarized
- **THEN** prompt-bearing raw inputs and outputs are written under `research/01-ssd-native-inference-current/benchmarks/correctness-eval-inputs/compact-visible-evidence-repair-2026-06-04/`, `research/01-ssd-native-inference-current/benchmarks/correctness-eval-results/compact-visible-evidence-repair-2026-06-04/raw/`, and `research/01-ssd-native-inference-current/benchmarks/correctness-eval-cache/compact-visible-evidence-repair-2026-06-04/`
- **AND** committed summaries are written under `research/02-quality-gated-stateful-kv-reuse/experiments/compact-visible-evidence-repair-2026-06-04/`
- **AND** the committed summary directory includes `README.md`, `summary.json`, `artifact-manifest.json`, `model-info.json`, `commands.md`, and `failure-classifications.json`

#### Scenario: Interpret compact repair chain
- **WHEN** the compact-answer visible evidence follow-up repairs both remaining cases
- **THEN** the system reports the focused chain as `hidden-prefix 0/6 -> visible evidence 4/6 -> compact visible evidence 6/6`
- **AND** it frames the result as role-aware context compilation / quality-gated context scheduling rather than pure KV reuse or a broad benchmark

#### Scenario: Classify remaining compact failures
- **WHEN** the compact-answer visible evidence follow-up does not repair both remaining cases
- **THEN** the system classifies each remaining failure as `model_weakness`, `prompt_protocol_issue`, `scorer_parser_brittleness`, `session_cache_semantic_issue`, `position_compatibility_issue`, `runtime_storage_issue`, or `ambiguous`
- **AND** it records supporting raw artifact paths, model/runtime metadata, and ruled-down explanations
