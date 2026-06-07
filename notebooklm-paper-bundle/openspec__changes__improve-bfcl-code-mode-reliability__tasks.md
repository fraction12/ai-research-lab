## 1. Planning And Delegation

- [x] 1.1 Create the OpenSpec change for BFCL Code-mode reliability.
- [x] 1.2 Send Track 2 a skeptical read-only review request for paper-safe boundaries.
- [x] 1.3 Spawn a sidecar audit for BFCL parser/protocol risks.

## 2. Adapter And Scorer Tests

- [x] 2.1 Add tests for action/action_input and action/parameters JSON.
- [x] 2.2 Add tests for plan/function_call JSON with whitespace-padded keys.
- [x] 2.3 Add tests for multiple adjacent JSON call objects in one response.
- [x] 2.4 Add tests for optional expected argument omission and required argument omission.

## 3. Runtime Implementation

- [x] 3.1 Normalize generated JSON object keys before BFCL call coercion.
- [x] 3.2 Support observed BFCL wrapper shapes without filling missing benchmark answers.
- [x] 3.3 Allow missing parsed arguments only when expected BFCL options include an empty string.
- [x] 3.4 Add and wire a BFCL-specific repair prompt in the model loop runner.

## 4. Validation

- [x] 4.1 Run Python compile checks for changed files.
- [x] 4.2 Run BFCL adapter and model-loop unit tests.
- [x] 4.3 Run `openspec validate improve-bfcl-code-mode-reliability --strict`.
- [x] 4.4 Run `openspec validate --all --strict`.

## 5. DushyantPC Smoke

- [x] 5.1 Confirm DushyantPC is reachable, GPU-enabled, and idle.
- [x] 5.2 Sync changed files and OpenSpec artifacts to DushyantPC if needed.
- [x] 5.3 Rerun the 10-row BFCL smoke on Gemma4.
- [x] 5.4 Summarize full-visible, native/restored, negative-control, parser-status, repair-status, and scorer-optionality results.
