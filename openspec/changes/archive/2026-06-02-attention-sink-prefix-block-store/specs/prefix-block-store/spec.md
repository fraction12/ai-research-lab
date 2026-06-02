## ADDED Requirements

### Requirement: Build content-addressed prompt block metadata

The system SHALL build a local metadata store for prompt blocks using deterministic content hashes.

#### Scenario: Store selected fixture blocks

- **WHEN** the user runs the prefix block store builder for a workflow fixture
- **THEN** the system writes one metadata record per referenced prompt block keyed by SHA-256 hash
- **AND** the system writes a manifest that references those block hashes in prompt order

#### Scenario: Reuse existing block records

- **WHEN** a block hash already exists in the store
- **THEN** the system preserves content-addressed identity and records the block as a cache hit in the manifest summary

### Requirement: Classify cache roles

The system SHALL classify blocks by cache role for future memory-tier decisions.

#### Scenario: Common reusable prefix exists

- **WHEN** selected scenarios share stable or semi-stable blocks
- **THEN** the system marks the earliest configured reusable blocks as `attention-sink-candidate`
- **AND** the system marks the remaining common reusable blocks as `stable-prefix`

#### Scenario: Scenario tail blocks exist

- **WHEN** a selected scenario includes blocks outside the common reusable prefix
- **THEN** the system marks semi-stable blocks as `rolling-tail-candidate`
- **AND** the system marks volatile blocks as `volatile-tail`

### Requirement: Recommend storage tiers

The system SHALL recommend a storage tier for each block role.

#### Scenario: Block role is assigned

- **WHEN** the system writes block metadata
- **THEN** the block metadata includes a storage recommendation for RAM-hot, SSD-persistent, or no-persist treatment

### Requirement: Emit cache-key material

The system SHALL emit cache-key material for future prefix or KV cache experiments.

#### Scenario: Store manifest is written

- **WHEN** the prefix block store builder completes
- **THEN** the manifest records model name, fixture hash, selected scenarios, common prefix block hashes, sink block hashes, tail block hashes, and a manifest cache-key hash
