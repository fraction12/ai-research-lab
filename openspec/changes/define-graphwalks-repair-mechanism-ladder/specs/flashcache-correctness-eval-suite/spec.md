## ADDED Requirements

### Requirement: Define GraphWalks repair mechanism ladder
The system SHALL define a focused repair-and-mechanism correctness ladder for the six selected GraphWalks cases from the first Track 02 ladder.

#### Scenario: Prepare fixed repair cohort
- **WHEN** the GraphWalks repair mechanism ladder is prepared
- **THEN** the case set includes exactly `graphwalks-6`, `graphwalks-9`, `graphwalks-11`, `graphwalks-13`, `graphwalks-16`, and `graphwalks-19`
- **AND** it uses the prior `graphwalks-six-case-ladder-2026-06-03` result as the source evidence
- **AND** it does not include broader IFEval, MRCR, GraphWalks, coding, RAG, or mixed benchmark cases

#### Scenario: Preserve mechanism scope
- **WHEN** the repair mechanism ladder is interpreted
- **THEN** the system treats the six cases as a mechanism probe rather than a prevalence benchmark
- **AND** it does not claim general GraphWalks, reasoning-task, or local-agent quality from the six-case cohort

### Requirement: Separate live session continuation from restored session-tail execution
The system SHALL test whether tail-only continuation fails before or after disk save/restore by separating live session continuation from restored session-tail execution.

#### Scenario: Run live no-restore control
- **WHEN** the live no-restore control is executed
- **THEN** the system primes the model with each case's stable prefix
- **AND** continues with the tail prompt in the same live session without saving or restoring the slot between prefix and tail
- **AND** writes response records with mode `live-tail`, prompt hashes, timing metadata, and session setup telemetry

#### Scenario: Compare live no-restore against restored session-tail
- **WHEN** live no-restore and restored session-tail scores are both available for a case
- **THEN** the summary records whether the failure appears before restore, only after restore, or remains ambiguous
- **AND** the classification can distinguish `live_session_semantic_issue` from `restore_or_position_issue`

### Requirement: Test anchor-span recompute repair controls
The system SHALL test bounded visible anchor-span recompute controls for restored-prefix/session-tail GraphWalks failures.

#### Scenario: Build anchor-span repair cases
- **WHEN** anchor-span repair cases are materialized
- **THEN** the system creates derived local case JSONL files for bounded anchor spans such as 64, 128, and 256 tokens from the stable-prefix suffix
- **AND** each derived case records the source case id, anchor policy, anchor token count, prompt hashes, and source input path
- **AND** prompt-bearing derived cases remain under ignored benchmark input paths

#### Scenario: Run anchor-span repair controls
- **WHEN** an anchor-span repair control is executed
- **THEN** the system runs the restored session-tail path with the chosen visible anchor span included in the tail-side prompt construction
- **AND** writes raw responses, scores, timing, prompt hashes, cache telemetry, and model metadata
- **AND** records whether the control repaired, partially repaired, degraded, or did not change each case

#### Scenario: Interpret anchor repair outcomes
- **WHEN** full prompt passes, restored session-tail fails, and an anchor-span repair control passes
- **THEN** the summary classifies the case as repairable by visible anchor recompute
- **AND** the fallback recommendation can be `allow_restore_with_anchor_recompute`

### Requirement: Decompose prompt visibility for GraphWalks failures
The system SHALL include prompt visibility controls that identify whether graph evidence, operation text, answer protocol, or full visible context is required for correctness.

#### Scenario: Build visibility control cases
- **WHEN** visibility controls are prepared
- **THEN** the system materializes derived local case files for query-visible graph-hidden, graph-visible query-tail, and graph-and-query-visible session-format controls where feasible
- **AND** each derived case records a deterministic construction rule and source case id

#### Scenario: Classify visibility sensitivity
- **WHEN** visibility control scores are available
- **THEN** the summary records whether each case depends on visible graph evidence, visible operation text, both, or neither
- **AND** prompt protocol sensitivity remains separate from cache/session semantic failure

### Requirement: Probe position and compatibility assumptions
The system SHALL record enough position and compatibility metadata to decide whether a GraphWalks repair result may be explained by tokenizer, prompt boundary, context-size, chat-format, or restore-position mismatch.

#### Scenario: Record position compatibility metadata
- **WHEN** any repair mechanism control runs
- **THEN** the response or summary artifacts record model path or repo, model file size where local, backend name and version, quantization, context size, server command line, answer protocol, stable-prefix hash, tail hash, full-prompt hash, restored token count where applicable, and derived prompt construction policy

#### Scenario: Classify compatibility issue
- **WHEN** compatibility metadata shows a token count, prompt hash, context-size, answer-protocol, or restore-position mismatch that explains the observed failure
- **THEN** the failure classification records `position_compatibility_issue` or `restore_or_position_issue`
- **AND** it does not classify the case as a model weakness or prompt protocol issue without supporting controls

### Requirement: Produce fallback policy from repair outcomes
The system SHALL produce a conservative fallback policy artifact for the fixed six GraphWalks cases after repair controls are scored.

#### Scenario: Write fallback policy
- **WHEN** repair controls have been summarized
- **THEN** the system writes `fallback-policy.md` under the Track 02 experiment directory
- **AND** each case receives one of `allow_session_tail`, `allow_live_tail_only`, `allow_restore_with_anchor_recompute`, `require_full_prompt`, or `ambiguous_needs_lower_level_probe`
- **AND** each policy decision records the supporting control ids and artifact paths

#### Scenario: Prefer full prompt when repair is not proven
- **WHEN** a case remains failed or ambiguous after repair controls
- **THEN** the fallback policy recommends `require_full_prompt` or `ambiguous_needs_lower_level_probe`
- **AND** it does not recommend restored session-tail reuse for that case

### Requirement: Preserve repair ladder artifacts
The system SHALL preserve exact artifact paths for GraphWalks repair mechanism ladder inputs, outputs, summaries, commands, model metadata, prompts, prior-art mapping, repair outcomes, and fallback policy.

#### Scenario: Write committed Track 02 repair artifacts
- **WHEN** the repair mechanism ladder is executed or summarized
- **THEN** committed Track 02 artifacts are written under `research/02-quality-gated-stateful-kv-reuse/experiments/graphwalks-repair-mechanism-ladder-2026-06-03/`
- **AND** the committed artifact set includes `README.md`, `commands.md`, `artifact-manifest.json`, `model-info.json`, `prior-art-mechanism-map.md`, `summary.json`, `repair-outcomes.json`, `failure-classifications.json`, `fallback-policy.md`, and `control-feasibility.md`

#### Scenario: Keep prompt and model run artifacts local
- **WHEN** prompt-bearing inputs, raw model outputs, score JSON, logs, or cache files are produced
- **THEN** they are written under ignored Track 01 benchmark paths for `graphwalks-repair-mechanism-ladder-2026-06-03`
- **AND** committed Track 02 artifacts record paths, hashes, and metadata needed to locate and verify those local raw artifacts

### Requirement: Map prior art before interpreting repair results
The system SHALL map relevant repo-local paper harvest evidence to the GraphWalks repair mechanism ladder before making paper-facing interpretation claims.

#### Scenario: Write prior-art mechanism map
- **WHEN** the repair mechanism ladder is summarized
- **THEN** the system writes `prior-art-mechanism-map.md`
- **AND** it maps CacheBlend, EPIC, CachedAttention, DroidSpeak, SCBench, Resident KV Claims, Stateful Inference, KVFlow, Tutti, KVDrive, DUAL-BLADE, and Swarm to the mechanisms or novelty boundaries they affect
- **AND** it states whether the current repo evidence is metadata/abstract-only or full-text-backed

#### Scenario: Avoid overclaiming novelty
- **WHEN** the summary interprets repaired or unrepaired GraphWalks failures
- **THEN** it does not claim novelty for generic KV reuse, prefix caching, SSD-backed KV storage, or agent workflow cache policy
- **AND** it frames the contribution as correctness contracts, repair/fallback policy, local non-frontier agent-loop evidence, and failure attribution unless stronger evidence is added

### Requirement: Minimize Track 01 harness changes for repair controls
The system SHALL avoid modifying Track 01 harness code for the GraphWalks repair mechanism ladder unless existing commands and deterministic local case composition cannot express a required control.

#### Scenario: Document control feasibility before harness edits
- **WHEN** implementation begins
- **THEN** the system writes or updates `control-feasibility.md` with each required control, whether it is covered by existing commands, whether local case composition is sufficient, and whether Track 01 code changes are required

#### Scenario: Add only minimal missing control surface
- **WHEN** a required control cannot be expressed without code changes
- **THEN** the implementation adds only the smallest mode or helper needed for that control
- **AND** it adds focused tests for the changed behavior
- **AND** it runs relevant Track 01 tests before recording the experiment as complete
