## 1. OpenSpec

- [x] Document PTI v3 no-cheat plan and design.
- [x] Add requirements for typed IR, schema-only repair, call-count diagnostics, and literal preservation.
- [x] Validate OpenSpec change and strict suite.

## 2. Typed IR And Validator

- [x] Add failing tests for schema-referenced function canonicalization.
- [x] Add failing tests for call-count diagnostics without expected answers.
- [x] Add failing tests for exact identifier/callback literal diagnostics.
- [x] Add failing tests for nested array/object validation.
- [x] Implement PTI v3 typed IR and validator improvements.

## 3. Schema-Only Repair

- [x] Add failing tests that repair prompts exclude `possible_answer`, `expected_answer`, `expected_calls`, and `ground_truth`.
- [x] Implement schema-only repair prompt builder.
- [x] Add PTI v3 metadata to control packets.

## 4. Smokes

- [x] Run local unit tests.
- [x] Run OpenSpec validation.
- [x] Run DushyantPC unit smoke.
- [x] Run DushyantPC targeted model smoke for weak categories.
