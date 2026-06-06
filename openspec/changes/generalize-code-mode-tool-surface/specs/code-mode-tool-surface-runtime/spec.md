## ADDED Requirements

### Requirement: Canonical Tool Call IR

The system SHALL represent model-authored tool calls with a benchmark-agnostic canonical call structure containing the function/tool name, arguments, source format, parse status, and raw call object.

#### Scenario: Canonical call preserves model-authored values
- **WHEN** a model emits a recognized tool-call dialect
- **THEN** the runtime returns canonical calls without filling missing benchmark-specific function names or arguments from expected answers

### Requirement: Dialect Normalization

The system SHALL normalize common local-model and provider-style tool-call dialects into canonical calls, including OpenAI-style `tool_calls`, Gemma native `call:name{...}`, `action`/`action_input`, `action`/`parameters`, `plan`, and nested `function_call` forms.

#### Scenario: Multiple dialects produce the same canonical call
- **WHEN** equivalent calls are emitted using different supported dialects
- **THEN** the runtime extracts the same canonical function name and arguments

### Requirement: Benchmark Adapter Boundary

Benchmark adapters SHALL consume canonical tool calls for scoring and execution translation instead of owning model-output dialect parsing.

#### Scenario: BFCL adapter consumes canonical calls
- **WHEN** BFCL receives model output in a supported dialect
- **THEN** BFCL scoring uses calls normalized by the common tool surface runtime

### Requirement: Auditable Normalization

The system SHALL expose normalization metadata sufficient to distinguish exact JSON, relaxed JSON, native-call syntax, wrapper-key canonicalization, whitespace normalization, and duplicate candidate merges.

#### Scenario: Parser telemetry records coercion
- **WHEN** model output requires normalization before scoring
- **THEN** the runtime exposes a parse status or metadata value identifying the normalization path

### Requirement: Duplicate Retry Merge

The system SHALL provide benchmark-agnostic duplicate merge behavior that collapses identical normalized model-authored retry candidates without dropping distinct calls.

#### Scenario: Duplicate retry is not scored as an extra call
- **WHEN** the same normalized model-authored call appears in multiple repair attempts
- **THEN** the merge utility returns one canonical call for that identity and preserves distinct calls
