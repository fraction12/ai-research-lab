## ADDED Requirements

### Requirement: Maintain No-Cheat BFCL PTI Run Readiness Gates
The BFCL PTI runtime SHALL require explicit no-cheat smoke gates before launching a full official non-live candidate rerun.

#### Scenario: Full BFCL run is blocked by weak 15-case smoke
- **WHEN** the weak-category restored-KV smoke scores below `13/15`
- **THEN** the full `1390` non-live candidate run is not considered run-ready

#### Scenario: Full BFCL run requires targeted 50-case evidence
- **WHEN** the 15-case weak-category smoke passes the readiness threshold
- **THEN** the runtime workflow still requires a targeted 50-case restored-KV smoke and official partial evaluator pass before the full run

### Requirement: Produce Post-Hoc Failure Taxonomy Without Prompt Leakage
The BFCL PTI workflow SHALL maintain a failure taxonomy that separates model failures from harness failures without feeding official answers back into inference or repair.

#### Scenario: Official evaluator result is used only after generation
- **WHEN** official evaluator pass/fail is used to classify a failure
- **THEN** the classification artifact is post-hoc only and is not included in any model-facing prompt, repair prompt, or export transformation

#### Scenario: Failure owner is recorded
- **WHEN** a weak-smoke row fails
- **THEN** the taxonomy records whether the likely owner is model semantics, model literal copying, model call count, model argument shape, harness parsing, harness export, harness repair damage, or unknown

### Requirement: Emit Precise Compiler Diagnostics
The BFCL PTI validator SHALL emit precise compiler-style diagnostics from visible request/catalog/schema and model output only.

#### Scenario: Missing required field is diagnosed
- **WHEN** a model call omits a required argument declared in the visible schema
- **THEN** validation reports the missing argument path and the visible required-field constraint

#### Scenario: Nested type mismatch is diagnosed
- **WHEN** a model call contains a nested value whose type conflicts with the visible schema
- **THEN** validation reports the nested path, observed value type, and expected visible schema type

#### Scenario: Unknown function is diagnosed
- **WHEN** a model call names a function absent from the visible catalog
- **THEN** validation reports the unknown function and the visible catalog names without selecting an expected answer

#### Scenario: Exact-copy literal drift is diagnosed
- **WHEN** a model argument paraphrases an enum or identifier-like value that has exact visible options or tokens
- **THEN** validation reports an exact-copy diagnostic using only visible enum options or tokens from the request/schema

### Requirement: Use Stepwise Schema-Only Repair
The BFCL PTI repair loop SHALL repair invalid call plans through schema-only stepwise prompts that preserve valid work and require a complete final call list.

#### Scenario: Structural repair comes before plan repair
- **WHEN** a call plan has parse, missing-field, type, enum, literal, or unknown-function errors
- **THEN** the first repair stage focuses on structural errors before broader function-choice or call-count reconsideration

#### Scenario: Valid call slots are preserved
- **WHEN** validation identifies schema-valid calls in a multi-call plan
- **THEN** the repair prompt marks those slots as `preserve` and instructs the model to keep them unchanged

#### Scenario: Final repair output is complete
- **WHEN** any repair stage is invoked
- **THEN** the model-facing prompt requires the complete final call list only, not a patch fragment or explanation

#### Scenario: Empty repair gets one format retry
- **WHEN** repair output is empty or unparsable
- **THEN** the runtime may issue one format retry that asks for a complete call list without expected-call, category, or scorer data

### Requirement: Include Generic PTI Pre-Submit Checklist
The BFCL PTI stable prefix SHALL include a generic pre-submit checklist that improves model self-checking without row-specific answer hints.

#### Scenario: Checklist is generic
- **WHEN** the stable prefix is built
- **THEN** it includes checks for catalog function existence, request-derived call count, required arguments, schema types, exact enum/identifier copying, and no extra text

#### Scenario: Checklist excludes BFCL answer hints
- **WHEN** the stable prefix is built
- **THEN** it does not include BFCL expected calls, `possible_answer`, category labels used as hints, or row-specific correct values

### Requirement: Present Visible Schema Compactly
The BFCL PTI runtime SHALL render compact visible function signatures and schema summaries for model use without adding expected-answer examples.

#### Scenario: Function signature includes visible constraints
- **WHEN** a function catalog is rendered
- **THEN** each function includes its visible name, description, required arguments, optional arguments, primitive/nested type summaries, and visible enum values where declared

#### Scenario: Schema examples use placeholders only
- **WHEN** a schema-shape example is rendered
- **THEN** it uses placeholders such as `<string>` or `<integer>` and does not include user-row values or expected BFCL answer values

### Requirement: Audit Repair Damage
The BFCL PTI workflow SHALL record whether repair changed calls that the validator marked as preserved.

#### Scenario: Preserved call changes are audited
- **WHEN** a repair output modifies a call slot marked as `preserve`
- **THEN** the record includes a repair-damage audit field with the original slot, repaired slot, and visible-schema reason if any

#### Scenario: Repair damage blocks run readiness
- **WHEN** a weak-smoke repair damages a preserved schema-valid call without a visible-schema reason
- **THEN** the full `1390` non-live candidate run is not considered run-ready
