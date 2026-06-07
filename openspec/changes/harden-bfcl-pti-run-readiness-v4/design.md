## Design

This change makes BFCL PTI repair behave like a strict compiler loop:

1. The model proposes calls.
2. The runtime parses and canonicalizes them into PTI IR.
3. The runtime validates only against the visible request/catalog/schema.
4. The runtime returns precise compiler-style errors.
5. The model repairs the plan.
6. The runtime preserves valid work, audits the repair, and exports valid calls.

The harness gets stronger, but Gemma still has to perform the semantic work.

## 1. Failure Taxonomy First

Before more prompt or repair changes, create a committed taxonomy for the current weak-category smoke:

- row id / category / source artifact
- initial model output summary
- validator errors
- repair profile
- final output summary
- official pass/fail
- failure owner: `model_semantics`, `model_literal_copy`, `model_call_count`, `model_argument_shape`, `harness_parse`, `harness_export`, `harness_repair_damage`, or `unknown`
- no-cheat note explaining what the runtime may say on retry

This taxonomy is post-hoc only. It may use official evaluator results to understand failures, but no expected calls may flow into model-facing prompts or export transformations.

## 2. Better Compiler Errors

Validation should produce small, model-actionable error records:

- `unknown_function`: emitted function is not in visible catalog
- `ambiguous_function`: suffix/fuzzy match is not unique
- `missing_required_argument`: required schema field absent
- `unexpected_argument`: field absent from schema
- `type_mismatch`: schema type and emitted value conflict
- `enum_literal_mismatch`: visible enum requires exact value
- `identifier_literal_mismatch`: identifier-like field was paraphrased when exact tokens are visible
- `call_count_too_low` / `call_count_too_high`: request-derived operation count and emitted call count differ
- `incomplete_output`: generation ended inside an incomplete call list or markdown/code wrapper

Each error must include:

- affected call index if known
- affected function if known
- affected argument path if known
- observed value summary
- visible constraint summary
- repair instruction that does not contain the expected answer

## 3. Stepwise Repair Protocol

The repair prompt should be structured as a small compiler report:

- user request
- compact visible function signatures and schemas
- previous model call list
- slot plan:
  - `preserve`: schema-valid calls to keep unchanged
  - `repair`: invalid calls with error ids
  - `reconsider`: calls with function-choice or call-count concerns
- final-output contract: return the full final call list only

The loop should support up to two repair stages:

1. **Structural repair** for parse, missing required fields, type/schema shape, enum/literal, and unknown-function errors.
2. **Plan repair** for call-count and function-choice diagnostics derived from request/catalog text.

If repair returns empty or unparsable output, one format retry is allowed. The retry may say the prior repair was empty/unparseable and ask for a complete call list. It may not add expected calls.

## 4. Pre-Submit Checklist

The stable prefix should include a generic checklist the model applies before final output:

- Every function name exists exactly in the visible catalog.
- The number of calls matches the independent operations requested by the user.
- Every required argument is present.
- Every argument value matches the declared schema type and nested shape.
- Enum and identifier-like values are copied exactly from visible enum options, the user request, or schema text.
- No helper calls, explanations, markdown, or extra text are emitted.

This checklist is generic and stable. It must not mention BFCL category labels or any row-specific answer.

## 5. Visible Schema Presentation

Improve the schema block so the model can reason without bloated raw JSON:

- one compact signature line per function
- required/optional argument list
- primitive/nested type summaries
- visible enum values
- short description copied from the official visible catalog
- language/export reminder for Python, Java, or JavaScript syntax only where the visible category/schema already implies it

Allowed examples must be schema-shape examples only, with placeholder values such as `<string>` or `<integer>`. They must not include row-specific user values or expected BFCL answers.

## 6. Gated Smoke Ladder

The change is not full-run ready until all gates pass:

1. Local TDD and compile.
2. OpenSpec change validation and full strict validation.
3. DushyantPC unit smoke.
4. DushyantPC micro-smokes for:
   - missing required argument
   - wrong type/nested shape
   - enum exact copy
   - identifier exact copy
   - unknown function
   - too few calls
   - too many calls
   - incomplete/unparseable output retry
5. DushyantPC 15-case weak-category restored-KV smoke:
   - at least `13/15`
   - `irrelevance 3/3`
   - no weak category below `2/3`
   - no repair reduces an originally schema-valid call
   - no unrecovered empty repair turns
6. DushyantPC 50-case targeted smoke:
   - official partial evaluator runs cleanly
   - score is above the current PTI v2/v3 target baseline for the sampled weak categories
   - failure taxonomy shows remaining failures are mostly model semantic failures, not harness parse/export/repair damage
7. Full `1390` non-live candidate run may start only after the 50-case gate passes.

## Stop Rules

Stop and report instead of launching full BFCL if:

- any model-facing prompt contains `possible_answer`, `expected_answer`, `expected_calls`, `ground_truth`, or official expected-call content
- repair uses scorer pass/fail as the reason to retry
- export rewrites generated calls using official expected calls
- the 15-case smoke remains below `13/15`
- any weak category falls below `2/3`
- repair damages a previously schema-valid call without a visible-schema reason
- DushyantPC unit or partial official evaluator smoke fails

## Paper-Safe Interpretation

This change can support a paper claim that a restored-KV PTI harness can provide schema-derived compiler feedback and recover some tool-call failures without answer-key leakage.

It cannot support a claim that the runtime knows the correct BFCL answer or that the official leaderboard score was improved through post-hoc answer-key repair.
