## ADDED Requirements

### Requirement: Track real fixture provenance

The benchmark SHALL preserve provenance notes for real workflow fixtures that are distilled from repository campaigns or archived specs.

#### Scenario: Fixture includes source artifacts

- **WHEN** a workflow fixture is based on a real campaign
- **THEN** the fixture records the source repository, source artifact paths, and the campaign decisions that shaped the prompt

#### Scenario: Fixture protects raw transcript absence

- **WHEN** the original raw chat transcript is not stored
- **THEN** the fixture records that it is a sanitized distilled prompt rather than a verbatim transcript
