# kv-capsule-semantic-continuation Specification

## ADDED Requirements

### Requirement: Define a KV capsule semantic-continuation contract
The Track 02 workflow SHALL treat a KV capsule as a resumable inference state with an explicit semantic contract, not merely as a cache byte blob.

#### Scenario: Record capsule fields
- **WHEN** a KV capsule probe is planned or summarized
- **THEN** it records whether model hash, tokenizer/template identity, prefix token hash, sequence length or `n_past`, K/V tensors, position state, attention or sequence identity, KV layout metadata, backend version, cache serialization format, and hybrid-model state are captured, inferred, unavailable, or missing
- **AND** it states which tails may be appended and which model/runtime settings invalidate the capsule

#### Scenario: Preserve design source
- **WHEN** the KV capsule probe is committed
- **THEN** `research/02-quality-gated-stateful-kv-reuse/docs/kv-capsule-semantic-continuation-experiment-2026-06-04.md` remains available as the design source
- **AND** any edits preserve the core distinction between documented full-prompt cache reuse and tail-only capsule continuation

### Requirement: Gate on a real lower-level continuation surface
The KV capsule probe SHALL start with a feasibility gate that chooses the smallest route capable of true prefix prefill, state save, state restore, and tail append without resending prefix text.

#### Scenario: Prefer native C or C++
- **WHEN** the pinned GPT-OSS llama.cpp path exposes native headers, libraries, and continuation APIs
- **THEN** the workflow uses or builds a small native harness before trying higher-level fallback surfaces

#### Scenario: Allow Python only with true continuation primitives
- **WHEN** native C/C++ support is blocked
- **THEN** a Python binding may be used only if it exposes true prefill, state save, state restore, and append semantics

#### Scenario: Reject unsupported server-only tail routes
- **WHEN** only server APIs are available
- **THEN** the route is acceptable only if telemetry proves tail tokens append to restored `n_past` without requiring a full prompt resend
- **AND** otherwise the workflow records `runner_surface_insufficient` and stops before persistence claims

### Requirement: Prove live append before persisted capsule claims
The KV capsule probe SHALL test native live append semantics before interpreting any persisted capsule result.

#### Scenario: Run native live append control first
- **WHEN** Family 1 codeword cases run through a lower-level harness
- **THEN** `native_live_append_tail_only` prefills the prefix, appends the tail in the same live context, resends no prefix text in the tail step, and records `n_past` before tail append
- **AND** if this control cannot be implemented or cannot beat `fresh_tail_only`, the workflow stops before testing GraphWalks

#### Scenario: Run restored capsule append after live append
- **WHEN** native live append is semantically valid
- **THEN** `native_restored_capsule_append_tail_only` prefills the prefix, saves capsule or state, destroys or resets context, restores the capsule or state, and appends the tail only
- **AND** it records capsule bytes, save time, restore time, `n_past`, response hashes, and answer-contained metrics

### Requirement: Run the experimental ladder in strict order
The KV capsule probe SHALL run only as far as the previous family justifies.

#### Scenario: Run codeword gate
- **WHEN** the experimental ladder begins
- **THEN** it evaluates 10 deterministic codeword variants
- **AND** it includes `full_visible_prefix_plus_tail`, `fresh_tail_only`, `server_documented_full_resend_cache_prompt`, `server_restored_tail_only`, `native_live_append_tail_only`, `native_restored_capsule_append_tail_only`, `wrong_capsule_negative`, and `corrupt_or_shifted_position_negative` when technically possible

#### Scenario: Advance beyond codeword only after positive continuation evidence
- **WHEN** the codeword gate has completed
- **THEN** the workflow advances to key-value only if full visible contains the answer, fresh tail-only misses, and native live append is positive and interpretable

#### Scenario: Restrict GraphWalks to a final small gate
- **WHEN** codeword, key-value, and mini graph gates are positive and interpretable
- **THEN** the workflow may evaluate only `graphwalks-6`, `graphwalks-9`, `graphwalks-11`, `graphwalks-13`, `graphwalks-16`, and `graphwalks-19`
- **AND** it does not run broad mixed benchmarks

### Requirement: Preserve semantic, timing, and state telemetry
The KV capsule probe SHALL preserve enough metrics to separate semantic continuation, prompt protocol, capsule-state completeness, and runtime compatibility.

#### Scenario: Score every response
- **WHEN** a control response is produced
- **THEN** the workflow records strict exact match, answer-contained or extractable-answer match, response hash, normalized response hash, output status, prompt hash, prefix hash, tail hash, and failure class
- **AND** verbose responses containing the answer are classified separately from missing-answer failures

#### Scenario: Record continuation telemetry
- **WHEN** live append or restored capsule append controls run
- **THEN** the workflow records prompt eval tokens and milliseconds, decode milliseconds, total latency, prefix token count, tail token count, `n_past` before tail append, capsule bytes, capsule save milliseconds, capsule restore milliseconds, model hash, tokenizer/template hash proxy, backend version, and runner hash where available
- **AND** unavailable telemetry is recorded as unavailable rather than fabricated

### Requirement: Keep prompt-bearing raw artifacts ignored and commit summaries
The KV capsule probe SHALL separate raw prompt-bearing artifacts from committed Track 02 summaries.

#### Scenario: Write raw artifacts under ignored Track 01 paths
- **WHEN** prompts, raw responses, runner logs, request payloads, or capsule/cache files are written
- **THEN** they are written under `research/01-ssd-native-inference-current/benchmarks/kv-capsule-semantic-continuation-2026-06-04/`
- **AND** those paths are covered by git ignore rules

#### Scenario: Commit Track 02 summaries
- **WHEN** the probe is packaged
- **THEN** committed artifacts include `README.md`, `summary.json`, `case-metrics.json`, `failure-classifications.json`, `capsule-contract.md`, `commands.md`, `model-info.json`, and `artifact-manifest.json` under `research/02-quality-gated-stateful-kv-reuse/experiments/kv-capsule-semantic-continuation-2026-06-04/`

### Requirement: Interpret prompt-cache reuse separately from KV capsule continuation
The KV capsule probe SHALL not claim that documented full-prompt resend cache reuse is the main capsule result.

#### Scenario: Best result
- **WHEN** native live append passes, restored capsule append passes, and server restored tail-only fails
- **THEN** the workflow concludes that semantic continuation is possible but the current server tail-only route is the wrong abstraction

#### Scenario: Capsule incomplete result
- **WHEN** native live append passes but restored capsule append fails
- **THEN** the workflow concludes that append semantics are valid but the persisted capsule is missing required state or restore is wrong

#### Scenario: Runner inadequate result
- **WHEN** native live append cannot be implemented or fails the codeword gate
- **THEN** the workflow stops before persistence claims and reports the runner surface as insufficient or runner semantics as broken

#### Scenario: Prompt-cache-only result
- **WHEN** documented full-prompt resend works but all hidden or capsule append paths fail
- **THEN** the workflow concludes that the current usable path is prompt-cache reuse, not KV capsule continuation
