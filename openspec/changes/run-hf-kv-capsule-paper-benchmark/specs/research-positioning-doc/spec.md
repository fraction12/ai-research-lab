# research-positioning-doc Specification Delta

## ADDED Requirements

### Requirement: Distinguish KV capsule evidence levels
Track 02 documentation SHALL distinguish synthetic route validation, HF benchmark quality evidence, pure KV capsule effects, and context-compilation effects.

#### Scenario: Reader checks paper benchmark interpretation
- **WHEN** a reader opens the HF KV capsule benchmark summary
- **THEN** it states which results are synthetic preflight only and which results use HF source rows
- **AND** it reports IFEval and GraphWalks separately
- **AND** it states whether restored capsule behavior matched native live append and full-visible quality
- **AND** it does not present evidence-slice repairs as pure KV capsule wins when fresh evidence-only matched capsule plus evidence

### Requirement: Preserve conservative paper claim guidance
Track 02 documentation SHALL state what the paper may and may not claim after the HF KV capsule benchmark.

#### Scenario: Reader drafts paper claims
- **WHEN** benchmark results are summarized for paper framing
- **THEN** the documentation maps each result pattern to allowed claims, disallowed claims, and required follow-up tests
- **AND** it preserves negative results and failure taxonomy instead of hiding them behind aggregate speed numbers
