## ADDED Requirements

### Requirement: Preserve The Official PTI Baseline
The BFCL PTI runtime SHALL preserve the official v1 non-live score as the baseline for all PTI v2 comparisons.

#### Scenario: Baseline is recorded
- **WHEN** PTI v2 changes are evaluated
- **THEN** reports compare against `969 / 1390 = 69.88%` and include per-category deltas

### Requirement: Export Language-Aware BFCL Prompt Results
The official BFCL exporter SHALL serialize canonical PTI calls using the target BFCL category language dialect.

#### Scenario: Python categories keep Python literals
- **WHEN** exporting a Python BFCL category
- **THEN** booleans, strings, arrays, and objects are rendered in Python-compatible prompt-result syntax

#### Scenario: JavaScript categories use JavaScript literals
- **WHEN** exporting a JavaScript BFCL category
- **THEN** booleans are rendered as `true` or `false`, nulls as `null`, strings as JSON-style quoted strings, and arrays/objects as JavaScript-compatible literals

#### Scenario: Java categories avoid Python literals
- **WHEN** exporting a Java BFCL category
- **THEN** booleans are rendered as `true` or `false`, nulls as `null`, strings as Java-compatible quoted strings, and nested values avoid Python-only `True`, `False`, and `None`

### Requirement: Validate PTI Calls Against Visible Schema Only
The PTI runtime SHALL validate parsed calls against the visible BFCL function catalog without using BFCL expected answers.

#### Scenario: Unknown function fails validation
- **WHEN** a parsed call names a function absent from the visible catalog
- **THEN** validation reports an unknown-function error

#### Scenario: Required argument is missing
- **WHEN** a parsed call omits a required argument declared in the visible schema
- **THEN** validation reports a missing-required-argument error

#### Scenario: Extra argument is rejected
- **WHEN** a parsed call includes an argument not declared in the visible schema
- **THEN** validation reports an unexpected-argument error

#### Scenario: Primitive type mismatch is reported
- **WHEN** a parsed call value conflicts with a visible primitive schema type
- **THEN** validation reports a type-mismatch error without replacing the value from expected answers

### Requirement: Strengthen The PTI Prompt Contract
The BFCL stable prefix SHALL instruct the model to abstain on irrelevant requests, count requested operations, avoid helper calls, use exact schema names, and omit optional/default parameters unless the user asks for them.

#### Scenario: Stable prefix contains PTI v2 rules
- **WHEN** a BFCL PTI packet is built
- **THEN** the stable prefix contains explicit rules for abstention, call count, helper-call avoidance, exact schema names, and optional/default omission

### Requirement: Keep Repair Paper-Safe
Any PTI repair pass SHALL use only schema, parser, decoder, and validator errors.

#### Scenario: Repair does not use expected answers
- **WHEN** a malformed PTI row is repaired
- **THEN** the repair context excludes `possible_answer` and official expected calls
