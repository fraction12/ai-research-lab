# Tail-Only KV Capsule Gemma 4 12B Replication Spec Delta

## ADDED Requirements

### Requirement: Explicit Gemma Profile Selection

The harness SHALL support Gemma 4 12B replication only through an explicit model/profile/config selection that records model path, model hash, tokenizer/template assumptions, context size, decode budget, backend bundle, and route labels.

#### Scenario: Gemma profile is selected

- **WHEN** an operator prepares a Gemma 4 12B run
- **THEN** the selected profile is visible in run metadata
- **AND** GPT-OSS defaults are not silently reused
- **AND** raw/cache output paths are distinct from GPT-OSS experiment paths.

### Requirement: Configurable Llama Runtime Library

The harness SHALL support an explicit llama runtime DLL path/name for each model profile.

#### Scenario: b9512 Gemma runtime is selected

- **WHEN** the Gemma 4 12B profile uses the b9512 CUDA 13 runtime
- **THEN** the harness loads `llama.dll` from the configured runtime path
- **AND** it does not assume the library is named `libllama.dll`
- **AND** it records the resolved DLL path, version, hash, and sequence-state export availability.

#### Scenario: Profile resolver emits runner arguments

- **WHEN** the Gemma profile is resolved before DushyantPC execution
- **THEN** the emitted runner arguments include `--llama-dll` pointing at b9512's `llama.dll`
- **AND** the raw runner must use that resolved DLL for loading, hashing, and export scanning before Gemma model-bearing evidence can begin.

### Requirement: Gemma Thinking Output Calibration

The Gemma profile SHALL calibrate thinking/channel output behavior before Family 1 or Family 2 evidence is interpreted.

#### Scenario: raw completion emits thinking/channel markers

- **WHEN** a Gemma smoke produces thinking/channel markers
- **THEN** scoring and prompt protocol are treated as uncalibrated
- **AND** the Family 1/2 evidence ladder does not start until the profile either suppresses those markers through a supported route or defines a deterministic scorer that safely handles them.

#### Scenario: CLI smoke uses reasoning control

- **WHEN** orchestration runs the one-shot `llama-completion` smoke for Gemma
- **THEN** the prepared command includes `--reasoning off` when that runtime supports it
- **AND** that CLI flag is treated as a smoke/profile calibration aid, not as proof that the raw C API sequence-state runner has the same output behavior.

### Requirement: Same Sequence-State Contract

Gemma replication SHALL use the same tail-only sequence-state contract as the GPT-OSS Family 1 and Family 2 gates.

#### Scenario: Restored capsule is interpreted

- **WHEN** restored capsule evidence is reported
- **THEN** full-visible and live-append controls have passed
- **AND** fresh-tail control has not leaked
- **AND** the effective route is recorded as `seq_file` or another explicitly approved sequence-state route
- **AND** whole-context fallback is not counted as sequence-state success.

### Requirement: Narrow Smoke Ladder

The replication campaign SHALL run only the approved smoke ladder before broader expansion.

#### Scenario: Gemma smoke begins

- **WHEN** orchestration launches model-bearing work
- **THEN** it starts with dry-run/help checks, optional one-shot `llama-completion` load smoke, and Family 1 smoke
- **AND** it does not run Family 2, Family 3, GraphWalks, broad retrieval, noiseless evidence, or agent-context tasks until prior gates pass and orchestration grants clearance.
