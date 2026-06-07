## ADDED Requirements

### Requirement: Parse Real BFCL Tool-Call Shapes
The BFCL Code-mode adapter SHALL parse benchmark tool-call intent from JSON shapes emitted by local models when the function names and arguments are present without requiring the model to use one exact wrapper.

#### Scenario: Action input JSON is parsed
- **WHEN** model text contains a JSON object with `action` and `action_input`
- **THEN** the adapter returns a BFCL call with that function name and argument object

#### Scenario: Plan JSON is parsed
- **WHEN** model text contains a `plan` list with nested function-call objects or function/arguments pairs
- **THEN** the adapter returns every complete BFCL call in order

#### Scenario: Harmless key whitespace is normalized
- **WHEN** model text contains JSON object keys with leading or trailing whitespace
- **THEN** the adapter parses those keys as their trimmed names

### Requirement: Preserve Honest BFCL Scoring Boundaries
The BFCL scorer SHALL distinguish missing required arguments from benchmark answer options that explicitly allow omission.

#### Scenario: Optional answer slot may be omitted
- **WHEN** an expected BFCL argument option list contains an empty string and the parsed call omits that argument
- **THEN** the scorer treats that omission as allowed for matching

#### Scenario: Required argument omission fails
- **WHEN** an expected BFCL argument option list does not contain an empty string and the parsed call omits that argument
- **THEN** the scorer marks the call as missing

### Requirement: Repair BFCL Rows With BFCL Schema
The model-loop runner SHALL use a BFCL-specific repair prompt for malformed BFCL tool-call output.

#### Scenario: Invalid BFCL output is repaired
- **WHEN** a BFCL row generation cannot be parsed as a host action or BFCL call and repairs remain
- **THEN** the runner appends a repair prompt that requests only `{"tool_calls":[{"function_name":"...","arguments":{...}}]}` JSON

### Requirement: Validate Against The Ten-Row Smoke Cohort
The change SHALL include tests and a Gemma4 smoke rerun before claiming BFCL Code-mode reliability.

#### Scenario: Local tests cover observed shapes
- **WHEN** the adapter tests run
- **THEN** they cover observed action/action_input, action/parameters, plan/function_call, whitespace-key, optional-argument, and required-argument failure cases

#### Scenario: Smoke result is reported with controls
- **WHEN** the 10-row BFCL smoke is rerun
- **THEN** the report states full-visible Code-mode pass count, native/restored pass count where run, negative-control behavior, parser statuses, and whether any success depended on host repair or scorer optionality
