# llama-cpp-agent-cache-wrapper Specification Delta

## ADDED Requirements

### Requirement: Separate native capsule continuation from documented prompt-cache reuse
The cache wrapper research workflow SHALL distinguish lower-level tail-only continuation from documented llama.cpp full-prompt resend cache reuse.

#### Scenario: Treat documented full resend as a control
- **WHEN** a KV capsule semantic-continuation probe runs
- **THEN** `server_documented_full_resend_cache_prompt` may be included as a known working prompt-cache control
- **AND** it is not treated as evidence that invisible hidden-prefix tail-only continuation works

#### Scenario: Require live append before restored capsule interpretation
- **WHEN** a lower-level runner is used for capsule continuation
- **THEN** it must first show `native_live_append_tail_only` can prefill prefix state and append tail tokens without resending prefix text
- **AND** restored capsule results are interpreted only after live append semantics are valid

#### Scenario: Classify server tail-only failure narrowly
- **WHEN** server restored tail-only completion fails while documented full-prompt cache reuse succeeds
- **THEN** the workflow classifies that as a server abstraction or protocol limitation for hidden continuation
- **AND** it does not generalize the result to all native KV or capsule continuation mechanisms
