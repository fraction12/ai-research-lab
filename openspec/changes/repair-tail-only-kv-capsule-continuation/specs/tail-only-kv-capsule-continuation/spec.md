## ADDED Requirements

### Requirement: Tail-Only KV Capsule Semantic Contract

Track 02 SHALL define the strong capsule contract as restored prefix state plus tail-only append, without resending prefix text in the tail request.

#### Scenario: Family 1 restored capsule pass

- **WHEN** the campaign runs the Family 1 simple codeword gate
- **THEN** full-visible `prefix + tail` SHALL pass all cases under answer-contained scoring
- **AND** fresh tail-only SHALL miss all cases unless quarantined as leakage
- **AND** native live append SHALL pass all cases before restored capsule is interpreted
- **AND** restored capsule tail-only append SHALL pass all cases before the family is classified as passed

### Requirement: Official Route Diagnostics Are Separated From Strong Contract Evidence

Server `cache_prompt` and slot save/restore diagnostics SHALL be reported as prompt-cache diagnostics unless they prove tail-only append into restored state without resending the prefix text.

#### Scenario: Server full-prompt resend cache works

- **WHEN** server slot/cache diagnostics show semantic correctness or prompt-token reuse while resending `prefix + tail`
- **THEN** the result SHALL be classified as documented prompt-cache reuse
- **AND** SHALL NOT be classified as strong tail-only capsule continuation

### Requirement: Sequence-State and Bridge Escalation

The campaign SHALL try or prove unavailable practical native sequence-state routes before emitting a no-go report.

#### Scenario: Python direct API cannot safely call sequence-state APIs

- **WHEN** Python `ctypes` cannot reliably access the required sequence-state APIs
- **THEN** the campaign SHALL inspect tiny C/C++ bridge feasibility against exact llama.cpp headers/libs
- **AND** SHALL document exact export/header/build blockers if bridge execution is not practical

### Requirement: Sanitized Artifact Boundary

Committed artifacts SHALL contain sanitized metrics, classifications, hashes, and commands only.

#### Scenario: Packaging results

- **WHEN** experiment results are committed
- **THEN** prompt-bearing raw prompts, raw responses, expected answer strings, token ID arrays/slices, generated token arrays, top-k arrays, and state bytes SHALL remain only under ignored Track 01 raw/cache paths
- **AND** committed Track 02 artifacts SHALL include artifact-manifest boundaries and leak-scan validation.
