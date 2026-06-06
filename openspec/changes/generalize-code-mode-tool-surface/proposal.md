## Why

The BFCL 10-row smoke now passes because the harness learned several model-output dialects, but those fixes live in a BFCL adapter. Scaling to more benchmarks will keep causing hand-fixes unless Code mode has a benchmark-agnostic tool surface runtime.

## What Changes

- Add a canonical Code-mode tool-call IR and parser/normalizer shared across benchmark adapters.
- Move model-output dialect parsing out of the BFCL-specific adapter into a reusable tool surface module.
- Preserve BFCL scoring semantics while making BFCL consume canonical calls.
- Add telemetry-friendly parse status and source-format metadata for coercion, repair, casing, whitespace, and duplicate merges.
- Add regression tests proving the runtime handles multiple output dialects without filling benchmark answers.

## Capabilities

### New Capabilities

- `code-mode-tool-surface-runtime`: Benchmark-agnostic canonical tool-call parsing, normalization, deduplication, and telemetry for local Code-mode harnesses.

### Modified Capabilities

- None.

## Impact

- Affected code: `research/01-ssd-native-inference-current/benchmarks/code_mode_tool_surface.py`, `bfcl_code_mode_kv_adapter.py`, `code_mode_kv_capsule_model_loop_runner.py`, and tests.
- Affected benchmark behavior: BFCL continues to score against expected calls, but parser/coercion behavior becomes reusable for BFCL and future benchmark adapters.
- No new external runtime dependencies are required.
