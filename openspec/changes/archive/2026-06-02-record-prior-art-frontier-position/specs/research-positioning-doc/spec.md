## ADDED Requirements

### Requirement: Record prior-art positioning
The documentation SHALL record whether SSD-native local-agent inference research is known prior art, a frontier, or a project-specific wedge.

#### Scenario: Reader checks novelty
- **WHEN** a reader opens the research-positioning documentation
- **THEN** the documentation states that KV/prefix caching and SSD-backed KV storage are already proven areas
- **AND** it identifies the remaining project wedge around local agent workloads, changed-tail prompts, and cold/restarted-session persistence

### Requirement: Preserve source anchors
The documentation SHALL preserve source links for papers, systems, and implementation docs used to support the positioning.

#### Scenario: Reader follows references
- **WHEN** a reader wants to verify the positioning
- **THEN** the documentation points to the relevant papers and systems in `docs/references.md`

### Requirement: Keep public-claim guidance conservative
The documentation SHALL include conservative phrasing guidance for public claims about novelty.

#### Scenario: Reader drafts public copy
- **WHEN** a reader uses the documentation to draft public commentary
- **THEN** the documentation discourages claiming invention of KV caching or SSD-backed inference
- **AND** it recommends positioning the work as a fast-moving edge for persistent KV/prefix reuse in local agent workflows
