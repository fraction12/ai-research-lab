## 1. Planning

- [x] 1.1 Create OpenSpec change for the generic Code-mode tool surface runtime.
- [x] 1.2 Notify Track 2 for read-only skeptical review.

## 2. Runtime Implementation

- [x] 2.1 Add a benchmark-agnostic `code_mode_tool_surface.py` module.
- [x] 2.2 Implement canonical call extraction for supported dialects.
- [x] 2.3 Implement canonical call identity and duplicate retry merge.
- [x] 2.4 Expose compatibility helpers for benchmark adapters.

## 3. BFCL Migration

- [x] 3.1 Refactor BFCL parser helpers to delegate to the common tool surface.
- [x] 3.2 Refactor model-loop BFCL coercion/merge code to use common helpers.
- [x] 3.3 Preserve BFCL scoring and answer-key-free repair behavior.

## 4. Tests

- [x] 4.1 Add unit tests for the common tool-surface parser and merge behavior.
- [x] 4.2 Update BFCL tests to prove compatibility through the common runtime.
- [x] 4.3 Run local BFCL and Code-mode harness unit tests.

## 5. Validation And Summary

- [x] 5.1 Run Python compile checks for changed benchmark modules.
- [x] 5.2 Run `openspec validate generalize-code-mode-tool-surface --strict`.
- [x] 5.3 Run `openspec validate --all --strict`.
- [x] 5.4 Summarize architecture, validation, remaining risks, and next benchmark gate.
