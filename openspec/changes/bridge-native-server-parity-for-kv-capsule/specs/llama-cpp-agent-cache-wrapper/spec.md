# llama-cpp-agent-cache-wrapper Specification Delta

## ADDED Requirements

### Requirement: Preserve server evidence for native parity comparison
The llama.cpp cache-wrapper research workflow SHALL preserve enough server-side evidence to compare documented server behavior against native direct C API behavior.

#### Scenario: Capture server request and cache context
- **WHEN** server baseline controls are refreshed for native parity
- **THEN** the workflow records endpoint path, payload shape, `id_slot` and `cache_prompt` usage when applicable, sampler parameters, server flags, model path/hash, server executable hash, response hash, timing, and token counts returned by the server
- **AND** prompt-bearing payloads and raw responses remain under ignored benchmark paths

#### Scenario: Keep documented prompt-cache result separate
- **WHEN** server full-visible or documented full-prompt resend controls pass
- **THEN** the workflow treats them as server parity controls
- **AND** it does not claim that they prove invisible hidden-prefix continuation or restored KV capsule semantics
