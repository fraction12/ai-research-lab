# PTI v3 Compiler-Style Repair Smoke - 2026-06-07

## Purpose

Harden the BFCL PTI repair loop without using answer keys. The runtime may report compiler-style errors from the visible user request and visible function catalog. It must not reveal expected calls, scorer misses, `possible_answer`, `ground_truth`, or official expected arguments.

## Change

- Added slot-preserving repair plans so schema-valid calls can be marked `preserve` while invalid calls are marked `repair`.
- Added high-confidence function-choice diagnostics using only lexical support from the user request and visible function names/descriptions.
- Added one retry for empty or unparsed BFCL repair generations.
- Added repair trace fields for validator errors, repair profile, slot repair plan, repair prompt hash, and empty retry count.
- Exposed `--max-empty-repair-retries` through the official BFCL lane wrapper.

## Validation

- Local tests: `46 passed`
- Local compile: passed for the touched BFCL runner modules
- OpenSpec strict: `upgrade-bfcl-pti-runtime-v3` valid
- DushyantPC tests: `46 passed`
- DushyantPC official-runner dry run: confirmed `--max-empty-repair-retries 1` is passed through to the model loop

## DushyantPC Step Smokes

All smokes used `code_mode_restored_kv_capsule`, `gemma4-12b`, `--max-repairs 1`, `--max-empty-repair-retries 1`, and `--state-route seq-file`.

| Lane | Result | Repairs | Empty retries | Notes |
|---|---:|---:|---:|---|
| `simple-javascript-3` | `2/3` | `0` | `0` | Baseline after compiler-repair patch; no repair fired. |
| `simple-java-3` | `2/3` | `0` | `0` | Function-choice diagnostic did not over-fire. |
| `parallel-3` | `2/3` | `0` | `0` | Stable call-count lane. |
| `parallel-multiple-3` | `2/3` | `0` | `0` | Stable multi-call lane. |
| `final-mixed-15` | `11/15` | `0` | `0` | Same category floor as the prior repair ladder. |
| `simple-javascript-3-retryfix` | `2/3` | `1` | trace gate fired | Empty/unparsed retry fired on `javascript_2`, but the model still produced an invalid repaired call. |

Final mixed breakdown:

- `irrelevance`: `3/3`
- `parallel`: `2/3`
- `parallel_multiple`: `2/3`
- `simple_java`: `2/3`
- `simple_javascript`: `2/3`

Final mixed failures:

- `bfcl:parallel:parallel_2`
- `bfcl:parallel_multiple:parallel_multiple_0`
- `bfcl:simple_java:java_1`
- `bfcl:simple_javascript:javascript_2`

## Read

The compiler-style repair loop is stricter and more auditable, but this is not full-run ready yet. The final mixed smoke remains `11/15`, below the intended `13/15` run-ready gate.

The important correction is that the empty/unparsed retry path now fires. On `javascript_2`, the runtime gave a schema-only literal-preservation error and then a format retry. The model still repaired badly, emitting an invalid function name and preserving the paraphrased callback value. That is a genuine model repair failure under the no-cheat rule.

The remaining failures are mostly schema-valid semantic/value misses:

- `parallel_2`: value typo, `alumium` instead of `aluminum`
- `parallel_multiple_0`: shape/value mismatch in nested list-style BFCL argument normalization
- `java_1`: semantic argument extraction and Java-style argument shape/type mismatch
- `javascript_2`: literal repair failed after retry

Do not launch the full `1390` run from this change alone. The next clean step is a separate schema-only validator pass for argument-shape/type normalization that can be justified from the visible schema, plus prompt work that improves the model's own literal-copy discipline.
