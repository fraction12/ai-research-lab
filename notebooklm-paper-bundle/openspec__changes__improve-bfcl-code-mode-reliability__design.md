## Context

The non-handmade BFCL smoke produced 70 records across seven controls. Only two rows were usable for strict KV capsule claims because several positive controls failed. Inspection of the raw responses shows that many failures contain recognizable tool-call intent in model-output shapes that the current adapter ignores, including `action` wrappers, `plan` arrays, nested `function_call` objects, and keys with leading spaces. One row also failed because BFCL answer options include `["", true]` slots that represent allowed omission, while the scorer required exact argument-key equality.

The goal is to improve the Code-mode runtime enough to test the actual research idea. The runtime must not synthesize benchmark answers from `expected_calls`, must not infer missing required arguments, and must record any optional scoring or repair behavior that affects pass/fail.

## Goals / Non-Goals

**Goals:**

- Make the BFCL adapter robust to real model-generated JSON call shapes observed in the 10-row smoke.
- Use BFCL-specific repair text when the model output is malformed for BFCL rows.
- Preserve paper-safe boundaries between parsing intent, optional scoring semantics, and answer leakage.
- Validate with local tests and a Gemma4 rerun of the 10-row smoke.

**Non-Goals:**

- Do not use `expected_calls` to fill missing calls or required arguments.
- Do not claim KV capsule value from rows that fail full-visible Code-mode.
- Do not broaden to the 50-100 row cohort until the smoke cohort has a clear result.
- Do not change the seven-control benchmark ladder.

## Decisions

### Decision 1: Normalize JSON structure before coercion

The adapter will recursively trim object keys before interpreting known wrappers. This handles observed `" function"` and `" arguments"` fields without changing user string values.

Alternative considered: regex replace raw model text. Rejected because raw text rewrites are brittle and could alter argument strings.

### Decision 2: Add wrapper support, not benchmark-answer completion

The adapter will recognize `action`, `action_input`, `parameters`, `plan`, and `function_call` wrappers when they contain function names and arguments. It will not generate calls from partial prefixes like `<|tool_call>call:math` because those lack arguments and would require hidden benchmark knowledge.

Alternative considered: resolve partial call prefixes from expected tool names. Rejected for primary scoring because it would blur parser recovery with answer inference.

### Decision 3: Treat empty-string expected options as optional omissions

The scorer will allow a missing parsed argument only when the benchmark expected options for that argument include `""`. This is a deterministic scoring normalization rather than host-filled argument generation, and must remain visible in results.

Alternative considered: fill missing optional arguments into parsed calls. Rejected because it mutates the call trace and makes hashes less faithful to model output.

### Decision 4: Add BFCL-specific repair prompt

The model-loop runner will use a BFCL repair prompt on BFCL rows when parsing fails. The prompt will request exact JSON with `tool_calls`, `function_name`, and `arguments`, and will not include expected function names or answers.

Alternative considered: reuse the generic action repair prompt. Rejected because it asks for the local harness action schema, not the BFCL scoring schema that the adapter accepts.

## Risks / Trade-offs

- Parser robustness could inflate apparent model quality if not reported. Mitigation: record parser status and include parser-driven pass counts in the summary.
- Optional-argument scoring could be mistaken for relaxed scoring. Mitigation: only allow omissions when BFCL expected options explicitly include `""`.
- Repair loops can hide first-pass weakness. Mitigation: report first-pass vs repaired pass counts and keep max repairs explicit.
- Full-visible may still fail on rows with prefix-only `<|tool_call>` outputs. Mitigation: classify those as model/protocol failures rather than synthesizing calls.

## Migration Plan

1. Add tests for observed BFCL output shapes and scorer boundary cases.
2. Implement adapter and runner changes.
3. Run Python compile, unit tests, and OpenSpec validation.
4. Sync to DushyantPC and rerun the 10-row BFCL smoke.
5. Update Track 02 summary artifacts with pass counts, parser statuses, and claim boundaries.
