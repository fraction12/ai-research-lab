## Why

The official BFCL non-live evaluation established a real baseline for restored KV capsule plus Programmatic Tool Interface (PTI): `969 / 1390 = 69.88%`. The failure audit shows that a meaningful part of the remaining loss is interface quality, not only model capability: Java/JavaScript exports are still mostly Python-shaped, irrelevance rows over-call, multi-call rows lose call-count discipline, and arguments sometimes drift from the declared schema.

We need to improve PTI as a general runtime/interface layer, not game BFCL. The implementation must stay paper-safe: no answer-key postprocessing, no category-specific cheating, and no hidden use of `possible_answer` at inference time.

## What Changes

- Freeze the official v1 BFCL baseline and compare every PTI v2 change against it by category.
- Render BFCL official exports with language-aware prompt-result dialects for Python, JavaScript, and Java.
- Add a schema-aware PTI validation layer that checks function names, required arguments, unexpected arguments, and primitive value types using only the visible function catalog.
- Tighten the PTI prompt contract around abstention, call count, exact schema names, helper-call avoidance, and optional/default argument handling.
- Define the safe repair boundary: repairs may use model output, visible schema, and validator/decoder errors, but must not use BFCL expected answers.
- Add TDD coverage and targeted smoke gates before any full BFCL rerun.

## Capabilities

### New Capabilities

- `bfcl-pti-runtime`: PTI v2 runtime/export validation for BFCL-compatible function-call generation.

### Modified Capabilities

- `bfcl-code-mode-reliability`: strengthened prompt contract and validator boundaries for BFCL PTI rows.

## Impact

- Affected code: `research/01-ssd-native-inference-current/benchmarks/bfcl_official_runner.py`, `research/01-ssd-native-inference-current/benchmarks/bfcl_code_mode_kv_adapter.py`, and related tests.
- Affected artifacts: BFCL official result exports and PTI runtime metadata.
- No new runtime dependency is required.
- Full GPU reruns are out of scope until language-aware export and targeted smokes pass.
