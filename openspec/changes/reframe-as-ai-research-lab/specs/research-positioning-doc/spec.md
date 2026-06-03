## ADDED Requirements

### Requirement: Present repo as AI research lab
The root documentation SHALL describe the repository as an AI research lab workspace with multiple research tracks rather than a single SSD-native inference project.

#### Scenario: Reader opens the root README
- **WHEN** a reader opens the root README
- **THEN** it identifies the repository as an AI research lab
- **AND** it points to the current research tracks and negative-space ideas archive

### Requirement: Preserve current SSD-native work as a track
The repository SHALL keep the existing SSD-native inference work together in a dedicated research track folder.

#### Scenario: Reader looks for current Flashcache work
- **WHEN** a reader navigates to the current SSD-native research track
- **THEN** they can find the existing docs, benchmarks, source, tests, and evidence paths from the prior project

### Requirement: Separate next research directions
The repository SHALL provide separate folders for quality-gated stateful KV reuse, role-aware context compilation, and negative-space research ideas.

#### Scenario: Reader evaluates future research paths
- **WHEN** a reader explores the research folder
- **THEN** each major research direction has its own README with purpose, hypotheses, and next steps

## MODIFIED Requirements

### Requirement: Record prior-art positioning
The documentation SHALL record whether each active research track is known prior art, a frontier, or a project-specific wedge.

#### Scenario: Reader checks novelty
- **WHEN** a reader opens a research track's positioning or idea documentation
- **THEN** the documentation states which base ideas are already proven areas
- **AND** it identifies the remaining track-specific wedge or marks the idea as already crowded

### Requirement: Preserve source anchors
The documentation SHALL preserve source links for papers, systems, and implementation docs used to support each research track's positioning.

#### Scenario: Reader follows references
- **WHEN** a reader wants to verify the current SSD-native inference positioning
- **THEN** the documentation points to the relevant papers and systems in `research/01-ssd-native-inference-current/docs/references.md`
- **AND** lab-level idea scans preserve source links in the relevant `research/04-negative-space-ideas/` notes

### Requirement: Keep public-claim guidance conservative
The documentation SHALL include conservative phrasing guidance for public claims about novelty across lab research tracks.

#### Scenario: Reader drafts public copy
- **WHEN** a reader uses the documentation to draft public commentary
- **THEN** the documentation discourages claiming invention of established cache, memory, inference, or agent-system primitives
- **AND** it recommends positioning each track around its measured wedge, evidence, and unresolved research question
