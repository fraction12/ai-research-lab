## ADDED Requirements

### Requirement: Define a combined Code mode and KV capsule viability probe
The experiment SHALL define a controlled local-agent runtime harness probe that tests Code mode tool-surface compression and KV capsule state reuse as separable mechanisms.

#### Scenario: Reader reviews the experiment purpose
- **WHEN** a reader opens the experiment design
- **THEN** it states the research question for combining Code mode and KV capsules
- **AND** it identifies the local model, runtime route, task families, controls, success gates, and stop rules
- **AND** it avoids claiming general model intelligence improvements from the prototype alone

### Requirement: Use prefix-dependent agent task cases
The harness SHALL use deterministic task cases where the stable prefix contains information or rules needed to solve the volatile tail request.

#### Scenario: Task case is materialized
- **WHEN** the runner prepares a task case
- **THEN** it records the stable prefix, volatile tail, expected answer, required tool path, source fixture hash, and task bucket
- **AND** fresh tail-only controls are expected to underperform unless the case is marked invalid or diagnostic

#### Scenario: Task suite covers agent behaviors
- **WHEN** the viability suite is assembled
- **THEN** it includes cases for single-tool selection, dependent multi-tool calls, parallel aggregation, bounded retry, long-horizon trace continuation, and denied or invalid tool access

### Requirement: Provide a Code mode hidden catalog contract
The harness SHALL expose a Code mode control surface that keeps the broad tool catalog out of the model-visible prompt while preserving deterministic tool discovery and policy enforcement.

#### Scenario: Code mode prompt is assembled
- **WHEN** a Code mode control is run
- **THEN** the model-visible tool contract is limited to the Code mode execution interface
- **AND** the broad tool catalog is represented through a run-scoped hidden catalog with a catalog id, catalog hash, and policy-filtered tool ids
- **AND** denied tools are absent from the callable catalog or rejected by the host bridge

#### Scenario: Guest tool calls are executed
- **WHEN** generated code or a structured call plan requests a catalog tool
- **THEN** the harness validates the tool id, arguments, policy, session identity, and case identity before returning a tool result
- **AND** it records search, describe, call, denial, timeout, and error telemetry

#### Scenario: Model-bearing Code mode loop runs
- **WHEN** a Gemma 4 model-bearing Code mode control is run
- **THEN** the runner treats model output as one bounded `EXEC {"code":"..."}` or `FINAL` step rather than a one-shot final answer
- **AND** it statically extracts only supported `tools.search`, `tools.describe`, and `tools.call` operations from the exec code cell before executing hidden catalog calls
- **AND** it appends validated `EXEC_RESULT` observations to the same active sequence before asking for the next step when a host answer is not yet terminal
- **AND** it rejects model-authored `TOOL_RESULT` or `EXEC_RESULT` text as spoofed host output
- **AND** it records exec parse status, tool execution status, host-filled arguments, final source, repair prompts, and whether channel/thought text was ignored for scoring

### Requirement: Run paired controls for each selected case
The harness SHALL run a paired control matrix that isolates direct tool exposure, Code mode, hidden live append state, restored KV capsule state, wrong capsule state, and compact visible evidence.

#### Scenario: Control matrix is run
- **WHEN** a selected case is evaluated
- **THEN** the runner attempts `direct_full_visible_tools`, `code_mode_full_visible`, `code_mode_fresh_tail_only`, `code_mode_native_live_append`, `code_mode_restored_kv_capsule`, `code_mode_wrong_capsule_negative`, and `compact_visible_evidence_code_mode`
- **AND** it records any skipped control with a reason and stop-rule classification

#### Scenario: Main restored capsule result is interpreted
- **WHEN** the restored KV capsule condition is summarized
- **THEN** it is compared against full-visible and native live-append controls
- **AND** it is not counted as valid hidden-prefix evidence unless fresh tail-only underperforms and wrong-capsule negative fails or is rejected

### Requirement: Record mechanism-level metrics
The harness SHALL record quality, tool-use, code-validity, safety, capsule, prompt-size, timing, and failure-classification metrics per case and per control.

#### Scenario: Case metrics are written
- **WHEN** a case-control record is completed
- **THEN** it includes task success, tool selection correctness, argument correctness, generated-code validation status, denied-tool behavior, response hashes, prompt byte and token counts, capsule metadata, runtime timings, and failure class

#### Scenario: Summary metrics are written
- **WHEN** a suite summary is produced
- **THEN** it reports results by task bucket, control id, full-visible-pass subset, fresh-tail-fail subset, live-append-pass subset, restored-vs-live mismatch subset, wrong-capsule outcome, and compact-evidence ablation

### Requirement: Preserve prompt-bearing artifacts outside committed summaries
The harness SHALL keep prompt-bearing raw records, generated code, tool outputs, capsule files, and trace payloads under ignored benchmark paths while committing only distilled summaries and manifests.

#### Scenario: Artifact manifest is written
- **WHEN** the experiment completes or stops
- **THEN** the committed artifact manifest points to ignored raw artifact directories, records hashes and counts, and identifies which raw data is not committed
- **AND** Track 02 committed summaries avoid raw volatile prompt text unless an explicit debug policy allows it

### Requirement: Apply staged go and stop rules
The harness SHALL use staged gates before any large run.

#### Scenario: Smoke gate fails
- **WHEN** harness-only dry run, two-case smoke, or twelve-case viability fails a required control
- **THEN** the runner stops or quarantines the failing phase
- **AND** it records whether the failure is task invalidity, model weakness, prompt protocol, Code mode contract, capsule semantics, scorer brittleness, runtime/storage, transport, or ambiguity

#### Scenario: Viability gate passes
- **WHEN** the thirty-case viability suite passes full-visible, fresh-tail, live-append, restored-capsule, wrong-capsule, and artifact gates
- **THEN** the summary may recommend a separate larger benchmark design
- **AND** it must still distinguish Code mode, compact evidence, and hidden KV contributions
