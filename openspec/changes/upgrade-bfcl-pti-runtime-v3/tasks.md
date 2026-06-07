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
- [x] Wire schema-only validator into the active BFCL model-loop repair gate.
- [x] Disable BFCL scorer-triggered model repair so repair triggers do not depend on expected calls.
- [x] Add parser-tolerant canonicalization for recoverable wrapper dialects before repair.
- [x] Add class-targeted repair profiles for missing-call, extra-call, function-selection, literal-preservation, and argument-schema errors.

## 4. Smokes

- [x] Run local unit tests.
- [x] Run OpenSpec validation.
- [x] Run DushyantPC unit smoke.
- [x] Run DushyantPC targeted model smoke for weak categories.
- [ ] Run DushyantPC micro-smokes for each repair class.
- [ ] Run DushyantPC final 15-case mixed smoke.
