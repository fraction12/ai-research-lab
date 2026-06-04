# llama-cpp-agent-cache-wrapper Specification Delta

## ADDED Requirements

### Requirement: Require semantic validation for hidden-prefix interpretation
The cache wrapper research workflow SHALL distinguish mechanical slot save/restore telemetry from semantic hidden-prefix continuation.

#### Scenario: Slot telemetry is not enough
- **WHEN** a hidden-prefix experiment records saved/restored token counts or slot bytes read/written
- **THEN** the workflow must not treat that telemetry alone as evidence that later tail completions semantically use the restored prefix
- **AND** it must reference a focused semantic-continuation probe or record that no such validation is available

#### Scenario: Hidden-prefix controls fail after semantic probe failure
- **WHEN** the semantic-continuation probe shows restored hidden-prefix controls fail simple codeword retrieval while full visible controls pass
- **THEN** downstream Track 02 interpretation must frame hidden-prefix failures as protocol/backend usage failures for the pinned path
- **AND** it must not generalize the result into a claim against hidden KV reuse in general
