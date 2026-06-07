## Why

PTI v2 raised the official BFCL non-live score from `69.88%` to `71.54%` by fixing export/runtime format issues, but targeted smokes still show weak spots that are real interface problems: multi-call completeness, exact literal preservation, function/schema fidelity, and nested/typed argument shapes.

We need PTI v3 to improve the runtime as a general Programmatic Tool Interface, not as BFCL score surgery. The implementation must remain paper-safe: no `possible_answer`, no expected-call repair, no answer-key postprocessing, and no hidden category-specific shortcuts.

## What Changes

- Introduce a typed PTI call IR that canonicalizes model-emitted calls into schema-referenced function calls.
- Validate function names as schema enum selections, including safe suffix matching for BFCL namespaced functions.
- Add generic call-count planning telemetry using only the user request and visible schema.
- Add exact-literal diagnostics for identifier-like arguments, callback/function names, and enum-like parameters.
- Deepen schema validation for arrays, objects, nested primitive values, and suspicious Java/camelCase drift.
- Generate schema-only repair prompts from model output, visible schema, user request, and validator errors only.
- Add TDD coverage and DushyantPC smoke gates before any full PTI v3 BFCL rerun.

## No-Cheat Boundary

Allowed at inference/repair/export:

- source user request
- visible BFCL function catalog/schema
- model output
- parser/decoder errors
- schema-validator errors
- generic operation-count/literal diagnostics derived from the user request

Disallowed at inference/repair/export:

- `possible_answer`
- official expected calls
- per-row answer-derived replacements
- result-specific answer-key repair
- category labels used as answer hints

`possible_answer` remains allowed only for evaluation, failure taxonomy, and post-hoc diagnosis.

## Impact

- Affected code: `research/01-ssd-native-inference-current/benchmarks/bfcl_code_mode_kv_adapter.py`, `research/01-ssd-native-inference-current/benchmarks/code_mode_kv_capsule_model_loop_runner.py` if repair loop plumbing is added, and related tests.
- Affected artifacts: PTI runtime metadata, schema validation telemetry, targeted smoke summaries.
- No new runtime dependency is required.
