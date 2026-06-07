## Design

PTI v2 separates four responsibilities that were previously blurred:

1. **Model intent surface**
   The model emits compact tool-call intent through the PTI contract.

2. **Typed intermediate representation**
   The host parses model intent into canonical calls: function name plus argument object.

3. **Schema-aware validation**
   The host validates calls against the visible function catalog only. It may report missing required arguments, unexpected arguments, unknown functions, and primitive type mismatches. It must not inspect BFCL `possible_answer` rows for inference repair or export decisions.

4. **Benchmark dialect export**
   The official exporter serializes canonical calls into the syntax expected by each BFCL non-live language bucket.

## No-Cheat Boundary

Allowed at inference/export:

- source user request
- visible BFCL function catalog/schema
- model output
- parser/decoder errors
- schema-validator errors

Disallowed at inference/export:

- `possible_answer`
- official expected calls
- per-row answer-derived replacements
- category-specific heuristics that identify answers rather than syntax/schema

`possible_answer` remains allowed for evaluation, failure taxonomy, and post-hoc diagnosis.

## Validation Strategy

- Unit tests cover language-aware export, schema validation, and prompt-contract text.
- Export-only smokes reuse existing model records to verify that regenerated BFCL result files are well-formed without a GPU rerun.
- Targeted model smokes cover Java, JavaScript, irrelevance, and parallel call-count rows before another full official run.
- Full BFCL non-live rerun is only justified after targeted smokes improve or preserve correctness without violating the no-cheat boundary.
