# Tail-Only KV Capsule Gemma 4 12B Replication Spec Delta

## ADDED Requirements

### Requirement: Explicit Gemma Profile Selection

The harness SHALL support Gemma 4 12B replication only through an explicit model/profile/config selection that records model path, model hash, tokenizer/template assumptions, context size, decode budget, backend bundle, and route labels.

#### Scenario: Gemma profile is selected

- **WHEN** an operator prepares a Gemma 4 12B run
- **THEN** the selected profile is visible in run metadata
- **AND** GPT-OSS defaults are not silently reused
- **AND** raw/cache output paths are distinct from GPT-OSS experiment paths.

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
- **THEN** it starts with dry-run/help checks and Family 1 smoke
- **AND** it does not run Family 2, Family 3, GraphWalks, broad retrieval, noiseless evidence, or agent-context tasks until prior gates pass and orchestration grants clearance.
