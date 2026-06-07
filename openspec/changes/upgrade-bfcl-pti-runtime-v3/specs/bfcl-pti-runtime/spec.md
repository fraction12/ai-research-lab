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

#### Scenario: Repair prompt targets a failure class
- **WHEN** visible-schema validation reports a repairable missing-call, extra-call, function-selection, literal-preservation, or argument-schema error
- **THEN** the repair prompt includes a failure-class-specific repair profile that tells the model what to preserve and what to change without answer-key data

#### Scenario: Repair prompt preserves valid call slots
- **WHEN** visible-schema validation can identify calls with no validator errors
- **THEN** the repair prompt includes a slot-level plan that tells the model which calls to preserve and which calls to repair without exposing expected calls

#### Scenario: Repair trace records compiler-style diagnostics
- **WHEN** a schema repair prompt is appended
- **THEN** the record includes the validator errors, repair profile, prompt hash, and slot-level repair plan for auditability

### Requirement: Canonicalize Recoverable Wrapper Dialects Before Repair
The BFCL PTI runtime SHALL canonicalize recoverable model output wrapper dialects before asking the model to repair.

#### Scenario: Java-style call wrapper is parseable
- **WHEN** model output uses a wrapper such as `{"call":{"function":"name","parameters":{...}}}`
- **THEN** the runtime extracts the inner function and parameters into PTI IR without triggering model repair for the wrapper alone

#### Scenario: Close schema function typo is uniquely recoverable
- **WHEN** the model emits a misspelled function name that has exactly one close match in the visible function catalog
- **THEN** validation canonicalizes the call to the visible catalog function and records the fuzzy schema normalization

### Requirement: Repair Literal And Count Errors Step By Step
The BFCL PTI runtime SHALL repair count and literal errors with targeted instructions.

#### Scenario: Exact identifier was paraphrased
- **WHEN** validation reports a literal-preservation diagnostic for a callback/function/identifier argument
- **THEN** repair is allowed and the prompt instructs the model to copy the exact token from the user request

#### Scenario: High-confidence extra call is detected
- **WHEN** the user request provides a high-confidence maximum call count and the model emits more calls than that count
- **THEN** validation reports a repairable extra-call diagnostic and the prompt instructs the model to remove only unsupported helper, duplicate, or unrequested calls

### Requirement: Gate BFCL Model-Loop Repair On Schema Validation
The BFCL PTI model loop SHALL trigger repair from schema-validator errors rather than BFCL scorer failures.

#### Scenario: Invalid call plan is repaired with schema-only context
- **WHEN** a BFCL model output parses into calls that fail visible-schema validation
- **THEN** the loop appends a schema-only repair prompt containing validator errors and no answer-key fields

#### Scenario: BFCL scorer failure does not trigger model repair
- **WHEN** a BFCL call plan is schema-valid but does not match official expected calls
- **THEN** the loop does not append a scorer-derived repair prompt to the model

#### Scenario: Empty BFCL repair receives one format retry
- **WHEN** a BFCL schema repair generation is empty or unparsable
- **THEN** the loop may append one retry prompt that asks for a complete call list without adding expected-call or scorer data

### Requirement: Diagnose Function Choice From Schema Text Only
The BFCL PTI runtime SHALL flag high-confidence function-choice concerns using only the user request and visible catalog names/descriptions.

#### Scenario: Selected function has no request support while another visible function does
- **WHEN** the selected catalog function has no lexical support in the user request and another catalog function has substantially stronger lexical support
- **THEN** validation reports a repairable function-choice diagnostic without naming any expected call

### Requirement: Preserve Complete BFCL Generations Before Parsing
The BFCL PTI model loop SHALL avoid stopping generation on structurally incomplete BFCL tool-call fragments.

#### Scenario: Incomplete JSON fragment continues generation
- **WHEN** a BFCL generation has an unclosed markdown fence, trailing comma, or unbalanced JSON list/object delimiters
- **THEN** the loop does not stop solely because a partial tool call can be salvaged from the fragment

#### Scenario: Complete JSON call list can stop generation
- **WHEN** a BFCL generation contains a complete parseable tool-call list
- **THEN** the loop may stop generation and score the parsed calls

### Requirement: Isolate Host Repair Prompts From Model Markup
The BFCL PTI model loop SHALL separate host-authored repair prompts from unfinished model-authored markdown or code blocks.

#### Scenario: Repair follows unfinished code fence
- **WHEN** the previous model output has an unclosed markdown code fence
- **THEN** the loop closes the fence before appending the host-authored schema repair prompt
