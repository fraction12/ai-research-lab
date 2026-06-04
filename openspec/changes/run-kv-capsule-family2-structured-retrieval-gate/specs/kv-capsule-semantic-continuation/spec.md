# kv-capsule-semantic-continuation Specification Delta

## ADDED Requirements

### Requirement: Advance from Family 1 to Family 2 only by explicit reviewed gate
The KV capsule semantic-continuation workflow SHALL treat Family 2 as a separate structured-retrieval mechanism gate that requires its own OpenSpec validation and stop-rule interpretation.

#### Scenario: Family 1 pass authorizes only Family 2 gate
- **WHEN** the Family 1 simple codeword restored-capsule gate passes
- **THEN** the next approved expansion MAY be the 5-case Family 2 structured-retrieval gate
- **AND** the workflow still SHALL NOT run Family 3, GraphWalks, noiseless evidence, or broad benchmarks without a separate reviewed change

#### Scenario: Family 2 pass remains narrow
- **WHEN** `native_restored_capsule_append_tail_only` contains the expected value for all 5 Family 2 cases after live append also passes
- **THEN** the workflow classifies `family2_restored_capsule_structured_retrieval_passed`
- **AND** it frames the result as a small structured-retrieval mechanism gate, not a general correctness or GraphWalks claim

#### Scenario: Family 2 stop rule blocks interpretation
- **WHEN** full-visible guard, fresh-tail control, or live append hits a Family 2 stop rule
- **THEN** restored capsule semantics are not interpreted
- **AND** the packaged result records the narrower blocker and stops
