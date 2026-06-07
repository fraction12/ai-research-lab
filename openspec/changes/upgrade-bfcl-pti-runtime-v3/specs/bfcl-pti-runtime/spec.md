## ADDED Requirements

### Requirement: Canonicalize PTI Calls Into Typed IR
The BFCL PTI runtime SHALL canonicalize parsed model calls into a typed intermediate representation using only the visible function catalog.

#### Scenario: Namespaced function suffix is resolved safely
- **WHEN** the visible catalog contains a single namespaced function whose suffix matches the model-emitted function name
- **THEN** the IR uses the catalog function name and records the normalization

#### Scenario: Ambiguous suffix is rejected
- **WHEN** multiple visible catalog functions share the same emitted suffix
- **THEN** validation reports an ambiguous function error instead of choosing one

### Requirement: Diagnose Call Count Without Expected Answers
The BFCL PTI runtime SHALL report likely call-count mismatches using only the user request, visible schema, and parsed model calls.

#### Scenario: Multi-operation request has too few calls
- **WHEN** the user request describes multiple independent operations and the model emits fewer calls
- **THEN** validation reports a likely call-count mismatch without using expected calls

### Requirement: Preserve Exact Identifier Literals
The BFCL PTI runtime SHALL detect paraphrased identifier-like argument values when exact tokens are present in the user request or schema.

#### Scenario: Callback literal is paraphrased
- **WHEN** a schema parameter name or description marks an argument as a callback/function/identifier and the user request contains an exact identifier token
- **THEN** validation reports a literal-preservation diagnostic if the model emits a vague paraphrase instead

### Requirement: Validate Nested Schema Shapes
The BFCL PTI runtime SHALL validate nested array and object values against visible schema definitions where provided.

#### Scenario: Array parameter receives scalar
- **WHEN** a visible schema declares an array and the model emits a scalar
- **THEN** validation reports a type mismatch

#### Scenario: Object property has wrong primitive type
- **WHEN** a visible schema declares an object property type and the model emits a conflicting nested value
- **THEN** validation reports a nested type mismatch

### Requirement: Build Schema-Only Repair Prompts
The BFCL PTI runtime SHALL build repair prompts from the user request, visible catalog, prior model output, parsed calls, and validator errors only.

#### Scenario: Repair prompt excludes answer keys
- **WHEN** a repair prompt is built
- **THEN** it does not include `possible_answer`, `expected_answer`, `expected_calls`, `ground_truth`, or official expected calls
