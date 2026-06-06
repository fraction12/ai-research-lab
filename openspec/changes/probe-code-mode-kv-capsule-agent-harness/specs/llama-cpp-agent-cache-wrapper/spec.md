## ADDED Requirements

### Requirement: Expose agent capsule control metadata
The wrapper and lower-level runners SHALL expose enough metadata for agent-task KV capsule experiments to distinguish live append, restored append, wrong-capsule negative, and visible-resend behavior.

#### Scenario: Agent capsule control runs
- **WHEN** an agent-task experiment uses a hidden stable prefix through llama.cpp state reuse
- **THEN** each control record includes control id, capsule route, capsule id, stable prefix hash, tail hash, prompt protocol hash, sequence id where available, prefix token count, `n_past` where available, capsule file bytes, capsule hash, save timing, restore timing, prompt evaluation timing, decode timing, and total wall time
- **AND** missing backend fields are recorded as unavailable rather than inferred

#### Scenario: Wrong capsule negative is attempted
- **WHEN** an agent-task experiment restores a mismatched capsule, catalog, or session
- **THEN** the runner records whether the request was rejected, failed semantically, or unexpectedly passed
- **AND** an unexpected pass is classified as a stop-rule event for hidden-prefix interpretation
