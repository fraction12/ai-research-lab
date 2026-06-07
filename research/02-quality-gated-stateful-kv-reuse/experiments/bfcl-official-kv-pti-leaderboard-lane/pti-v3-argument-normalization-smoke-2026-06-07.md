# PTI v3 Argument Normalization Smoke - 2026-06-07

## Purpose

Add a no-cheat visible-schema normalization layer for the remaining BFCL PTI failures.

The runtime still cannot use expected calls, `possible_answer`, `expected_answer`, `expected_calls`, `ground_truth`, category labels, or scorer hints in repair prompts. It may only report compiler-style diagnostics from the visible user request, visible function catalog, and visible JSON schema.

## Change Under Test

- Added visible-schema type-normalization diagnostics for quoted numeric and boolean values.
- Added enum-literal exact-copy diagnostics for schema-declared string enum values.
- Added pre-submit PTI checklist language for schema-shaped numbers, booleans, arrays, objects, and enum literals.
- Added repair-profile language requiring numbers/booleans to use schema types and enum values to be copied exactly.

Commit under test:

`69b4c2d Add BFCL PTI argument normalization diagnostics`

## Validation

Local validation:

- BFCL adapter tests: `41 passed`
- BFCL adapter + official runner tests: `48 passed`
- Compile of touched runner modules: passed
- `openspec validate upgrade-bfcl-pti-runtime-v3 --strict`: valid
- `openspec validate --all --strict`: `43 passed, 0 failed`

DushyantPC validation:

- Smoke root: `C:\ai\bfcl-pti-normalization-smoke`
- Run output: `C:\ai\bfcl-pti-normalization-runs\final-mixed-15-v1`
- Unit smoke: `48 passed`
- Sequence-state helper copied from the existing BFCL smoke checkout because the clean archive omitted the local helper artifact.

## Final Mixed 15 Smoke

The run reused the same 15-case mixed packet as the prior repair-ladder smoke:

`C:\ai\bfcl-pti-repair-ladder-runs\final-mixed-15-v1\raw\bfcl-pti-repair-ladder-final-mixed-15-v1-control-packet.jsonl`

Mode:

- control: `code_mode_restored_kv_capsule`
- model profile: `gemma4-12b`
- prediction budget: `128`
- max steps: `5`
- max schema repairs: `1`
- max empty repair retries: `1`
- state route: `seq-file`

Result:

- records: `15/15`
- total score: `11/15`
- `irrelevance`: `3/3`, repairs `0`, empty retries `0`
- `parallel`: `2/3`, repairs `1`, empty retries `0`
- `parallel_multiple`: `2/3`, repairs `1`, empty retries `0`
- `simple_java`: `2/3`, repairs `1`, empty retries `0`
- `simple_javascript`: `2/3`, repairs `1`, empty retries `1`

## Remaining Failures

- `bfcl:parallel:parallel_2`: repair kept `alumium` instead of `aluminum` and scalarized list-shaped expected values.
- `bfcl:parallel_multiple:parallel_multiple_0`: repair emitted scalar/object-like values where the adapted BFCL expectation remains list-shaped.
- `bfcl:simple_java:java_1`: repair chose plausible schema-visible fields but still used wrong object/argument names and quoted numeric value.
- `bfcl:simple_javascript:javascript_2`: empty retry fired, but the model still failed to produce a valid final call.

## Read

This change improves the compiler diagnostics and prompt discipline, but it does not improve the mixed 15 score. The final smoke remains below the run-ready gate of `13/15`.

The next clean step is not more answer-key-free repair around this same prompt. The remaining failures are now mainly BFCL adapter shape semantics and model literal-copy behavior under repair. Before a full `1390` rerun, either:

- improve BFCL adapter shape normalization in a way justified by visible schema and official language format, then re-evaluate existing records where possible, or
- run a narrower prompt experiment focused on literal copying and list/object argument-shape preservation, with the same no-cheat constraints.
