## 1. Protocol Implementation

- [x] 1.1 Extend the llama.cpp client helper to pass optional JSON schema constraints to `/completion`.
- [x] 1.2 Add correctness-runner protocol helpers for raw and JSON-answer prompts.
- [x] 1.3 Extract JSON `answer` values into scorer response text while preserving raw output and parse errors.

## 2. Tests And Docs

- [x] 2.1 Add unit tests for protocol prompt construction, answer extraction, and JSON schema payloads.
- [x] 2.2 Update benchmark docs with the JSON-answer protocol and research rationale.

## 3. Validation

- [x] 3.1 Run compile checks, unit tests, OpenSpec validation, and diff hygiene.
- [x] 3.2 Rerun a local or PC smoke with JSON-answer protocol when feasible.
