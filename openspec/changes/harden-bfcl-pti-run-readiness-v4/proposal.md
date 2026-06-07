## Why

PTI v3/v3.1 made the BFCL Programmatic Tool Interface more honest: export formatting is language-aware, repair is schema-triggered instead of scorer-triggered, valid slots can be preserved, empty repairs get one retry, and visible-schema diagnostics are now auditable. The weak-category restored-KV smoke still plateaus at `11/15`, with each weak category at `2/3`.

That plateau is useful evidence: the remaining misses are not mostly parser/export fragility. They are places where Gemma fails to choose the right function, copy exact literals, produce schema-shaped arguments, or complete multi-call plans under the restored per-case PTI contract.

We need one more no-cheat hardening pass before a full BFCL non-live rerun: make the harness a stricter compiler and a better teacher, without turning it into a scorer or answer-key postprocessor.

## What Changes

- Add a failure-taxonomy artifact for the current 15-case weak-category smoke that separates model failures from harness failures.
- Improve compiler-style validation errors so the model receives precise, schema-derived feedback for missing fields, unknown functions, enum/literal drift, call-count mismatches, and nested type mismatches.
- Upgrade the repair protocol to perform targeted, stepwise repair while preserving valid slots and requiring a complete final call list.
- Add a generic PTI pre-submit checklist to the stable prefix so the model self-checks function existence, call count, required arguments, schema types, literal copying, and output cleanliness before finalizing.
- Improve visible schema presentation with compact, generic function signatures and schema examples that do not leak BFCL expected answers, categories, or row-specific hints.
- Run a gated smoke ladder: local TDD, DushyantPC unit smoke, micro-smokes by repair class, 15-case mixed smoke, 50-case targeted smoke, then full `1390` only if gates pass.

## No-Cheat Boundary

Allowed in inference, validation, repair, export, and smoke gating:

- source user request
- visible BFCL function catalog, descriptions, declared schema, enums, required fields, and language family
- model output and parse errors
- schema-validator errors
- generic operation-count diagnostics derived from the request text
- exact tokens present in the user request or visible schema
- post-hoc official evaluator scores for reporting and failure taxonomy only

Disallowed in inference, validation, repair, export, and model-facing prompts:

- `possible_answer`
- official expected calls
- scorer-derived repair prompts
- per-row answer-derived replacements
- hidden category labels as hints
- post-hoc answer-key transformations of generated calls

The runtime may tell the model why its output is invalid. It must not tell the model what the official answer is.

## Impact

- Affected code: `research/01-ssd-native-inference-current/benchmarks/bfcl_code_mode_kv_adapter.py`, `research/01-ssd-native-inference-current/benchmarks/code_mode_kv_capsule_model_loop_runner.py`, official BFCL runner/export plumbing, and related tests.
- Affected artifacts: weak-smoke failure taxonomy, repair trace metadata, DushyantPC smoke summaries, official-lane readiness docs.
- No full official leaderboard submission is performed by this change.
