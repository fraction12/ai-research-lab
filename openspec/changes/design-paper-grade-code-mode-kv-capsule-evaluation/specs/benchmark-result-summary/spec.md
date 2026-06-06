## MODIFIED Requirements

### Requirement: Summarize benchmark results with claim boundaries
Paper-facing benchmark summaries SHALL distinguish pilot, primary, replication, diagnostic, and ablation evidence.

#### Scenario: Paper campaign summary is written
- **WHEN** a paper-grade Code-mode + KV capsule campaign summary is written
- **THEN** it labels each result as mechanism evidence, handmade viability evidence, external benchmark pilot evidence, primary paper evidence, model-matrix evidence, efficiency evidence, or diagnostic evidence
- **AND** reports allowed and disallowed claims separately

#### Scenario: Pilot and primary rows differ
- **WHEN** a pilot result and a primary paper cohort both exist
- **THEN** the summary reports them separately
- **AND** does not blend their pass rates into one aggregate
