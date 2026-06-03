## ADDED Requirements

### Requirement: Emit wrapper benchmark progress
The Flashcache wrapper benchmark SHALL emit progress output before long-running direct and cache-aware model phases.

#### Scenario: Progress before direct scenario
- **WHEN** the wrapper benchmark is about to run a direct full-prompt scenario
- **THEN** it prints a progress line identifying the direct phase and scenario name

#### Scenario: Progress before cache-aware scenario
- **WHEN** the wrapper benchmark is about to run a cache-aware scenario through the wrapper
- **THEN** it prints a progress line identifying the cache-aware phase and scenario name
