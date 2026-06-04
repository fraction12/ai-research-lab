# documented-server-cache-reuse Specification

## ADDED Requirements

### Requirement: Probe documented llama.cpp full-prompt cache reuse
The Track 02 workflow SHALL test documented server-side prompt-cache reuse by restoring a slot and resending the full `prefix + tail` prompt with `cache_prompt: true` and an explicit slot id.

#### Scenario: Run codeword controls
- **WHEN** the documented server cache-reuse probe runs
- **THEN** it evaluates 10 deterministic codeword variants
- **AND** each variant includes `full_visible_no_cache`, `fresh_tail_only`, `restored_tail_only`, `restored_full_prompt_cache_prompt`, and `full_prompt_cache_prompt_without_restore`
- **AND** every `/completion` request uses explicit `id_slot: 0`

#### Scenario: Score semantic and exact-output behavior
- **WHEN** a control response is produced
- **THEN** the workflow records strict exact-match, answer-contained/extractable-answer, output status, response hash, normalized response hash, prompt hash, and request payload hash
- **AND** verbose responses containing the correct codeword are classified separately from missing-answer failures

#### Scenario: Preserve slot and timing telemetry
- **WHEN** a restored-slot control is executed
- **THEN** the workflow records slot save/restore telemetry including `n_saved`, `n_restored`, `n_written`, `n_read`, save milliseconds, restore milliseconds, setup wall milliseconds, and prime prompt milliseconds where available
- **AND** unavailable telemetry is recorded as unavailable rather than fabricated

### Requirement: Preserve auditable server-cache evidence
The documented server cache-reuse probe SHALL preserve enough server evidence to audit whether semantic correctness also corresponds to computational prefix reuse.

#### Scenario: Keep raw logs ignored
- **WHEN** server logs, request payloads, raw responses, prompts, or slot cache files are written
- **THEN** they are written under `research/01-ssd-native-inference-current/benchmarks/documented-server-cache-reuse-2026-06-04/`
- **AND** those paths are covered by git ignore rules

#### Scenario: Commit sanitized log index
- **WHEN** Track 02 summaries are written
- **THEN** committed artifacts include a server-log index with log hashes, selected non-prompt-bearing cache evidence, cache-related pattern counts, and a cache-evidence classification
- **AND** prompt-bearing raw logs remain uncommitted

### Requirement: Interpret documented cache reuse separately from hidden tail-only continuation
The workflow SHALL distinguish documented full-prompt cache reuse from invisible hidden-prefix tail-only continuation.

#### Scenario: Documented route works semantically and computationally
- **WHEN** `restored_full_prompt_cache_prompt` contains the codeword and log/timing evidence shows only the suffix was evaluated
- **THEN** the result is interpreted as documented visible-prefix cache reuse working for the pinned path
- **AND** the summary states that the prefix must be resent for matching

#### Scenario: Documented route works semantically but not computationally
- **WHEN** `restored_full_prompt_cache_prompt` contains the codeword but evidence shows the whole prefix was recomputed
- **THEN** the result is interpreted as semantically correct but not an effective prefix-cache speedup

#### Scenario: Documented route fails semantically
- **WHEN** `restored_full_prompt_cache_prompt` fails like `fresh_tail_only`
- **THEN** the workflow concludes that the pinned GPT-OSS/server path is broken or incompatible for this documented route
- **AND** it recommends a stable non-SWA/non-hybrid model control before making general claims
