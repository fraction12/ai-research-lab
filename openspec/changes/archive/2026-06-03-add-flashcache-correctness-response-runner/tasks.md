## 1. Runner Implementation

- [x] 1.1 Add correctness-runner CLI arguments for cases, modes, llama.cpp settings, response output, and optional score output.
- [x] 1.2 Implement full-prompt response generation with response JSONL records.
- [x] 1.3 Implement session-tail response generation with prefix prime/save/restore telemetry.
- [x] 1.4 Implement optional post-run scoring using the existing scorer.

## 2. Tests And Docs

- [x] 2.1 Add focused unit tests for response record construction and runner orchestration helpers.
- [x] 2.2 Update benchmark docs with full/session-tail response-run commands.

## 3. Validation

- [x] 3.1 Run compile checks, unit tests, OpenSpec validation, and diff hygiene.
- [x] 3.2 Attempt a local smoke command path without requiring a large model run.
