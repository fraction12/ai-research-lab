# native-server-parity-bridge Specification

## ADDED Requirements

### Requirement: Refresh server full-visible baseline before native parity claims
The Track 02 workflow SHALL refresh a small live server full-visible codeword baseline before interpreting native direct C API parity.

#### Scenario: Capture server baseline
- **WHEN** the native/server parity bridge starts model calls
- **THEN** it runs at least 3 deterministic codeword variants through the pinned llama.cpp server full-visible path
- **AND** it records command line, server hash, model hash, backend flags, endpoint payload shape, sampler parameters, prompt hash, response hash, answer-contained score, timing, and server token counts when available

#### Scenario: Stop on server baseline failure
- **WHEN** refreshed server full-visible does not contain the expected codeword
- **THEN** the workflow classifies the result as `server_model_prompt_setup_issue`
- **AND** it stops before native parity or KV capsule interpretation

### Requirement: Compare tokenization and prompt format before native generation
The parity bridge SHALL compare server and native prompt handling before treating native generation as meaningful.

#### Scenario: Test native special-token routes
- **WHEN** exact prompt bytes are selected for parity testing
- **THEN** native tokenization is tested with `add_special=true` and `add_special=false`
- **AND** the workflow records prompt byte hash, token counts, first and last token IDs or token hashes, BOS/EOS/template status, and which route is selected

#### Scenario: Use server tokenization when available
- **WHEN** the server exposes tokenization for the exact prompt bytes
- **THEN** the workflow compares native token IDs or token hashes against server tokenization
- **AND** if server tokenization is unavailable, it records the limitation and uses the best available proxy rather than fabricating parity

#### Scenario: Test template or BOS behavior
- **WHEN** GPT-OSS server behavior may depend on chat template, BOS, or special formatting
- **THEN** the native bridge tests raw completion prompt behavior against the selected template/BOS route
- **AND** it preserves prompt and template hashes without committing prompt-bearing text

### Requirement: Prove logits and sampler sanity before full native parity gate
The parity bridge SHALL rule out basic native generation-loop defects before running or interpreting longer native full-visible generation.

#### Scenario: Inspect first-token behavior
- **WHEN** native tokenization and prompt route are selected
- **THEN** the workflow inspects first-token logits, top-k token IDs or hashed pieces, sampled token behavior, logits index, token-to-piece conversion, and greedy or temperature-zero sampler behavior where feasible
- **AND** repeated-newline generation is classified as `native_logits_sampler_blocker`, `native_prompt_template_protocol_blocker`, or `native_server_parity_failure` according to the narrowest observed evidence

### Requirement: Gate KV capsule interpretation on native full-visible parity
The parity bridge SHALL require native full-visible parity before any native live append or restored capsule result is interpreted.

#### Scenario: Run native full-visible parity gate
- **WHEN** the selected tokenization, prompt, and sampler route is ready
- **THEN** `native_full_visible_prefix_plus_tail` runs on the refreshed codeword set
- **AND** passing requires answer-contained behavior to match the refreshed server baseline on the small codeword set

#### Scenario: Stop on native full-visible parity failure
- **WHEN** native full-visible still misses after bounded parity attempts
- **THEN** the workflow classifies the result with the narrowest blocker, including `native_tokenization_protocol_blocker`, `native_prompt_template_protocol_blocker`, `native_logits_sampler_blocker`, or `native_server_parity_failure`
- **AND** it does not run or interpret KV capsule gates

### Requirement: Preserve sanitized parity artifacts
The parity bridge SHALL separate prompt-bearing raw artifacts from committed Track 02 summaries.

#### Scenario: Write raw artifacts under ignored benchmark path
- **WHEN** prompts, raw responses, request payloads, token traces, server logs, console logs, or state bytes are written
- **THEN** they are written under `research/01-ssd-native-inference-current/benchmarks/native-server-parity-bridge-2026-06-04/raw/`
- **AND** those paths are covered by git ignore rules

#### Scenario: Commit Track 02 summaries
- **WHEN** the parity bridge is packaged
- **THEN** committed artifacts include `README.md`, `summary.json`, `case-metrics.json`, `failure-classifications.json`, `commands.md`, `model-info.json`, and `artifact-manifest.json` under `research/02-quality-gated-stateful-kv-reuse/experiments/native-server-parity-bridge-2026-06-04/`
- **AND** prompt-bearing text, raw responses, console logs, and state bytes are not committed
