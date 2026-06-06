# llama-cpp-agent-cache-wrapper Specification Delta

## ADDED Requirements

### Requirement: Expose paper-grade KV capsule controls
The lower-level llama.cpp route SHALL expose the controls needed to test KV capsule semantic continuation independently from documented prompt-cache resend.

#### Scenario: Run native live append
- **WHEN** the benchmark requests `native_live_append`
- **THEN** the runner prefills the stable prefix, appends only the tail in the same native sequence, and records `n_past`, prefix token count, generated token hash where available, timing, and response hashes

#### Scenario: Run native restored capsule append
- **WHEN** the benchmark requests `native_restored_capsule_append`
- **THEN** the runner prefills the stable prefix, saves a persisted sequence or capsule file, restores that state, appends only the tail, and records capsule hash, capsule bytes, save time, restore time, `n_past`, prefix token count, timing, and response hashes

#### Scenario: Run wrong capsule negative
- **WHEN** the benchmark requests `wrong_capsule_negative`
- **THEN** the runner restores a deliberately mismatched capsule or fails closed before generation
- **AND** the response record identifies whether the mismatch was rejected, generated an incorrect answer, or unexpectedly passed

### Requirement: Record capsule validity metadata
The lower-level llama.cpp route SHALL record enough metadata to judge whether a persisted capsule is compatible with a tail request.

#### Scenario: Write capsule metadata
- **WHEN** a capsule is saved or restored
- **THEN** the metadata records model hash, tokenizer or template hash where available, backend version, runner hash, context size, runtime flags, prefix token hash, sequence length, `n_past`, capsule serialization route, and unavailable fields as explicit null or unavailable values
