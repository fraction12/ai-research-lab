## ADDED Requirements

### Requirement: Maintain Flashcache system report
The project SHALL maintain a decision-oriented report that summarizes the SSD-backed Flashcache system approach, benchmark evidence, quality risks, and next implementation direction.

#### Scenario: Report explains current system
- **WHEN** a reader opens the system report
- **THEN** the report explains the current Flashcache layer, the intended lower-level SSD/KV direction, and why local agent loops are the target workload

#### Scenario: Report grounds claims in evidence
- **WHEN** the report makes a claim about speed or quality
- **THEN** it references recorded benchmark artifacts or existing project docs
- **AND** it distinguishes measured results from hypotheses and projections

#### Scenario: Report preserves quality caveats
- **WHEN** the report discusses correctness results
- **THEN** it states that observed failures may be caused by model capability, prompt protocol, or cache/session semantics
- **AND** it does not claim the SSD-backed approach is quality-safe until parity gates pass
