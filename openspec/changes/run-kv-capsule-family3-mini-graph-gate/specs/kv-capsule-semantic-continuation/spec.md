# kv-capsule-semantic-continuation Specification Delta

## ADDED Requirements

### Requirement: Advance from Family 2 to Family 3 only by explicit reviewed mini-graph gate
The KV capsule semantic-continuation workflow SHALL treat Family 3 as a separate mini-graph mechanism gate that requires its own OpenSpec validation and stop-rule interpretation.

#### Scenario: Family 2 pass authorizes only Family 3 mini-graph gate
- **WHEN** the Family 2 structured-retrieval restored-capsule gate passes
- **THEN** the next approved expansion MAY be the 5-case Family 3 mini-graph gate
- **AND** the workflow still SHALL NOT run GraphWalks, noiseless evidence, server bridge, Family 4, or broad benchmarks without a separate reviewed change

#### Scenario: Family 3 pass remains narrow
- **WHEN** Stage A and Stage B restored capsule controls contain the expected answers after their full-visible and live-append controls pass
- **THEN** the workflow classifies `family3_restored_capsule_mini_graph_passed`
- **AND** it frames the result as a small fabricated mini-graph mechanism gate, not a general graph-reasoning or GraphWalks claim

#### Scenario: Family 3 stop rule blocks interpretation
- **WHEN** a Stage A or Stage B full-visible guard, fresh-tail control, or live append control hits a stop rule
- **THEN** restored capsule semantics for that blocked stage are not interpreted
- **AND** the packaged result records the narrower blocker and stops
