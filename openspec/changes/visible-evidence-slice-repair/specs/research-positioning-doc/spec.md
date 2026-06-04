## ADDED Requirements

### Requirement: Frame visible evidence repair separately from pure KV reuse
The documentation SHALL frame visible-evidence-slice repair as role-aware context compilation / selective recompute rather than pure persistent KV cache reuse.

#### Scenario: Reader checks Track 02 interpretation
- **WHEN** a Track 02 artifact summarizes the visible-evidence-slice repair experiment
- **THEN** it states that a visible extracted evidence slice is not pure KV reuse
- **AND** it describes the result as a quality-gated state reuse control with role-aware context compilation or selective recompute
- **AND** it avoids claiming general benchmark quality from the six-case GraphWalks result

#### Scenario: Reader compares cache and evidence mechanisms
- **WHEN** a Track 02 artifact discusses hidden-prefix/session-tail behavior and visible evidence repair in the same result
- **THEN** it separates cache/session semantics from model evidence retrieval, prompt protocol, scorer/parser brittleness, position/compatibility, and runtime/storage explanations
- **AND** it records which controls support or rule down each explanation
