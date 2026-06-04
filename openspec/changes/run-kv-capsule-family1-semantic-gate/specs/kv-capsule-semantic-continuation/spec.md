# kv-capsule-semantic-continuation Specification Delta

## ADDED Requirements

### Requirement: Interpret Family 1 capsule result narrowly
The KV capsule semantic-continuation workflow SHALL interpret the reviewed Family 1 simple codeword gate as a mechanism gate, not a broad benchmark or GraphWalks result.

#### Scenario: Passing restored capsule
- **WHEN** `native_restored_capsule_append_tail_only` contains the answer for all 3 Family 1 simple codeword cases after live append also passes
- **THEN** the workflow classifies `family1_restored_capsule_semantic_passed`
- **AND** it does not run Family 2, GraphWalks, noiseless evidence, or broad benchmarks without new orchestration approval

#### Scenario: Failing restored capsule after live append
- **WHEN** live append passes but restored capsule append fails
- **THEN** the workflow classifies `restored_capsule_semantic_failure` or a narrower save/restore protocol blocker
- **AND** it avoids claims against KV capsules in general unless the capsule contract evidence supports them
