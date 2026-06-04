# llama-cpp-agent-cache-wrapper Specification Delta

## ADDED Requirements

### Requirement: Separate documented full-prompt cache reuse from hidden tail-only continuation
The cache wrapper research workflow SHALL not conflate restored hidden-prefix tail-only completion with documented llama.cpp full-prompt cache reuse.

#### Scenario: Test documented route after tail-only failure
- **WHEN** tail-only restored-prefix controls fail semantic continuation
- **THEN** the workflow should test the documented route by restoring the slot and resending the full `prefix + tail` prompt with `cache_prompt: true` and explicit `id_slot`
- **AND** it must preserve both semantic answer metrics and computational cache-reuse evidence

#### Scenario: Interpret visible-prefix resend correctly
- **WHEN** the documented route works
- **THEN** the workflow frames the result as visible-prefix cache reuse that may avoid prefix recomputation
- **AND** it does not describe the result as invisible hidden context or tail-only continuation
