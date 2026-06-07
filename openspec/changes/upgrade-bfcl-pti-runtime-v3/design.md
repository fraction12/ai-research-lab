## Design

PTI v3 treats model output as a compiler input rather than a final answer string.

1. **Parse**
   Existing tolerant parsers extract model-emitted call candidates from JSON, native call fragments, `ACTION`, or `EXEC` shapes.

2. **Canonicalize Into Typed IR**
   The host converts each candidate into a `PTICallIR`:
   - `name`: the schema-selected function name
   - `arguments`: the parsed argument object
   - `source_name`: the raw model function token before canonicalization
   - `normalizations`: generic schema/name normalizations applied

3. **Validate Against Visible Schema**
   Validation uses only the visible BFCL function catalog. It reports:
   - unknown or ambiguous functions
   - missing required arguments
   - unexpected arguments
   - primitive and nested type mismatches
   - Java/camelCase parameter drift
   - identifier/callback literal paraphrases
   - likely call-count mismatches derived from the user request

4. **Repair Prompt**
   If validation fails, the runtime may ask the model to repair the call plan with a schema-only prompt. The prompt includes:
   - user request
   - visible function catalog
   - previous model output/call plan
   - validator errors

   It must exclude expected answers and `possible_answer`.

5. **Export**
   Valid canonical IR is exported through the v2 language-aware BFCL exporter.

## Scope

This change implements the generic PTI v3 compiler/validator/repair substrate plus tests and targeted smokes. A full BFCL non-live model rerun is a separate gate after v3 smokes pass.

## Anti-Cheating Constraints

- No validation function may accept BFCL expected calls.
- Repair prompt builders must not include fields named `possible_answer`, `expected_answer`, `expected_calls`, or `ground_truth`.
- Operation-count diagnostics may use only the user request and visible function count/name information.
- Literal diagnostics may only compare model values against exact tokens present in the user request or declared schema enums.
