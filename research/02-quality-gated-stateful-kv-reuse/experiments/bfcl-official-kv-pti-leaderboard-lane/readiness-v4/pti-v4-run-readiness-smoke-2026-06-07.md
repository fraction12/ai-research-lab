# PTI v4 Run-Readiness Smoke - 2026-06-07

## Purpose

Implement the `harden-bfcl-pti-run-readiness-v4` OpenSpec change and test the BFCL PTI runtime with no answer-key leakage.

The runtime may show the model only compiler-style diagnostics from:

- visible user request
- visible function catalog/signatures
- visible schema constraints
- previous model output
- parser/schema errors

It must not show `possible_answer`, `expected_answer`, `expected_calls`, `ground_truth`, category hints, scorer misses, or official answer-key data in inference or repair prompts.

## Change Under Test

Commits:

- `384a9ee Add BFCL PTI run readiness OpenSpec`
- `b885237 Implement BFCL PTI run readiness v4`

Implemented:

- PTI v4 protocol and validator metadata.
- Compact function signatures with placeholder-only schema shapes.
- Generic pre-submit checklist in the stable prefix.
- Enriched compiler diagnostics with error id, argument path, visible constraint, observed value summary, and repair instruction.
- Stepwise schema-only repair stages: structural before plan-level repair.
- Preserved-call repair-damage audit.
- Post-hoc no-cheat failure taxonomy script.

## Local Validation

- Focused BFCL/PTI tests: `76 passed, 2 subtests passed`
- Python compile: passed for adapter, model loop, official runner, and taxonomy script
- OpenSpec change strict: passed
- OpenSpec all strict: `44 passed, 0 failed`

## DushyantPC Validation

Smoke checkout:

`C:\ai\bfcl-pti-v4-run-readiness-smoke-b885237`

The checkout was transferred from the committed Mac `git archive` because Windows GitHub auth was interactive. The local sequence-state helper was copied from the existing BFCL smoke checkout.

Unit smoke:

- `76 passed, 2 subtests passed`

Micro-smokes:

- missing required argument: pass
- nested type / argument shape: pass
- enum exact-copy: pass
- identifier literal-copy: pass
- function-choice schema-only diagnostic: pass
- request-derived call count: pass
- empty repair retry no-cheat prompt: pass

## DushyantPC 15-Case Restored-KV Smoke

Run:

`bfcl-pti-v4-mixed-15-v1`

Lane root:

`C:\ai\bfcl-pti-v4-run-readiness-runs\mixed-15-v1`

Mode:

- control: `code_mode_restored_kv_capsule`
- model profile: `gemma4-12b`
- state route: `seq-file`
- predict: `128`
- max steps: `5`
- max schema repairs: `1`
- max empty repair retries: `1`

Categories:

- `irrelevance`: 3
- `parallel`: 3
- `parallel_multiple`: 3
- `simple_java`: 3
- `simple_javascript`: 3

Result:

- records: `15/15`
- runner exit: `0`
- export files: written for all 5 categories
- total score: `10/15`

Breakdown:

- `irrelevance`: `3/3`
- `parallel`: `2/3`
- `parallel_multiple`: `1/3`
- `simple_java`: `2/3`
- `simple_javascript`: `2/3`

Post-hoc failure taxonomy:

- `model_argument_shape`: `2`
- `model_call_count`: `2`
- `model_format_or_empty_output`: `1`

Failure cases:

- `bfcl:parallel:parallel_2`: model call count
- `bfcl:parallel_multiple:parallel_multiple_0`: model argument shape
- `bfcl:parallel_multiple:parallel_multiple_2`: model call count
- `bfcl:simple_java:java_1`: model argument shape
- `bfcl:simple_javascript:javascript_2`: model format or empty output

## Readiness Decision

Stop.

PTI v4 is cleaner and more auditable, but the 15-case gate failed:

- required: at least `13/15`
- observed: `10/15`
- required: no category below `2/3`
- observed: `parallel_multiple` is `1/3`

Do not launch the full `1390` non-live candidate rerun from this state.

## Next Clean Target

The remaining failures are mostly schema-valid but scorer-wrong outputs. The next change should focus on generic, no-cheat model behaviour:

- stronger duplicate/extra-call suppression for multi-call requests
- better list/object shape preservation when the visible schema permits array/object values
- stronger Java camelCase/key-shape discipline
- better recovery when repair output is empty or unparsable

Any next repair prompt must still avoid expected calls, category labels, scorer hints, and answer-key-derived transformations.
