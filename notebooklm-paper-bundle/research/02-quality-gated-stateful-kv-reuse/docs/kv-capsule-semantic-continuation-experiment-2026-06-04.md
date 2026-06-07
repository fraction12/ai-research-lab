# KV Capsule Semantic Continuation Experiment

Date: 2026-06-04

## Purpose

This experiment tests whether Track 02 can move beyond documented prompt-cache reuse into a true resumable inference-state mechanism.

The target object is a **KV capsule**:

> A persisted inference state that can be restored and continued with new tail tokens, without resending the original prefix text, while preserving the semantic behavior of `full visible prefix + tail`.

This is intentionally stricter than llama.cpp server prompt caching. In the documented server cache route, the caller resends the full visible prompt so the server can prefix-match and avoid recomputing some tokens. A KV capsule should instead restore the already-computed prefix state and append only the tail.

## Prior Evidence

### Hidden Tail-Only Restore Failed

`hidden-prefix-semantic-continuation-2026-06-04` showed:

| Control | Answer contained |
| --- | ---: |
| `full_visible_prefix_plus_tail` | 10/10 |
| `fresh_tail_only` | 0/10 |
| `restored_hidden_prefix_plus_tail` | 0/10 |

The restored hidden-prefix responses exactly matched fresh tail-only responses in 10/10 cases, even though slot save/restore telemetry reported `n_saved`/`n_restored`.

Interpretation: mechanical slot restore happened, but the prefix was not semantically available to the tail in that protocol.

### Documented Full-Prompt Cache Reuse Worked

`documented-server-cache-reuse-2026-06-04` showed:

| Control | Answer contained | Mean prompt tokens | Mean prompt ms |
| --- | ---: | ---: | ---: |
| `full_visible_no_cache` | 10/10 | 31.0 | 625.4 |
| `fresh_tail_only` | 0/10 | 14.0 | 410.1 |
| `restored_tail_only` | 0/10 | 14.0 | 410.4 |
| `restored_full_prompt_cache_prompt` | 10/10 | 19.0 | 477.8 |
| `full_prompt_cache_prompt_without_restore` | 10/10 | 31.0 | 623.4 |

Decision: `documented_cache_reuse_semantic_and_computational_reuse_observed`.

Interpretation: the pinned GPT-OSS llama.cpp route can reuse cached prefix computation when the full visible prompt is resent with `cache_prompt: true`, but this is not invisible semantic continuation.

## Research Question

Can a lower-level runner create, persist, restore, and continue from a KV capsule such that:

```text
restore(capsule(prefix)) + append(tail)
```

is semantically equivalent to:

```text
full_prompt = prefix + tail
```

without resending the prefix text in the tail request?

## Capsule Contract

A valid capsule is not just a KV tensor dump. It must identify enough state to resume a sequence safely:

- model hash
- tokenizer hash or tokenizer identity
- chat template / prompt formatting hash
- prefix token ids or prefix token hash
- sequence length / `n_past`
- per-layer K/V tensors
- RoPE or position state
- attention mask and sequence/slot identity
- KV quantization/layout metadata
- backend version and cache serialization format
- hybrid-model state if applicable:
  - sliding-window ring-buffer state
  - recurrent/SSM state
  - MLA or compressed latent state
- validity policy:
  - which tails may be appended
  - which model/runtime settings invalidate the capsule
  - how restore success is verified

The first experiment may not implement all of these fields explicitly, but its artifacts must state which fields were captured, inferred, unavailable, or missing.

## Experimental Ladder

Run the ladder in order. Do not advance to the next family unless the previous family gives interpretable results.

### Family 1: Codeword Gate

10 deterministic variants.

Prefix:

```text
The secret codeword for nonce <N> is <CODEWORD>. Remember it.
```

Tail:

```text
For nonce <N>, what is the secret codeword? Answer with one word.
```

Pass condition: restored capsule append contains the correct codeword in 10/10 cases, or failures are clearly attributable to output formatting rather than missing prefix state.

### Family 2: Key-Value Gate

10 deterministic variants.

Prefix contains 20 key-value pairs. Tail asks for one exact value.

Pass condition: restored capsule append retrieves the requested value at or near full-visible performance and clearly beats fresh tail-only.

### Family 3: Mini Graph Gate

Use small synthetic directed graphs where the full prompt is short enough that the model reliably passes.

Tail asks for parent/source nodes of one target node.

Pass condition: restored capsule append matches full-visible behavior and beats fresh tail-only.

### Family 4: GraphWalks Six-Case Gate

Only run this if Families 1-3 are interpretable and at least the simple gates pass.

Use the six historical GraphWalks cases already used by Track 02:

- `graphwalks-6`
- `graphwalks-9`
- `graphwalks-11`
- `graphwalks-13`
- `graphwalks-16`
- `graphwalks-19`

Pass condition: restored capsule append meaningfully closes the gap against full visible prompt. If it fails, classify whether the failure is capsule semantics, model retrieval weakness, prompt protocol, or scorer/parser behavior.

## Required Controls

Each case in each family should include these controls when technically possible:

| Control | Purpose |
| --- | --- |
| `full_visible_prefix_plus_tail` | Positive semantic control. |
| `fresh_tail_only` | Negative leakage control. |
| `server_documented_full_resend_cache_prompt` | Known working prompt-cache control from the latest Track 02 result. |
| `server_restored_tail_only` | Known failed server hidden-tail control. |
| `native_live_append_tail_only` | Proves lower-level append semantics without persistence. |
| `native_restored_capsule_append_tail_only` | Main result: persisted capsule restore plus tail-only append. |
| `wrong_capsule_negative` | Restoring a mismatched capsule should fail closed or clearly miss. |
| `corrupt_or_shifted_position_negative` | Wrong position/`n_past`/slot metadata should fail closed or clearly degrade. |

## Runner Requirement

The experiment should not rely only on llama.cpp server `/completion`, because that route has already shown that tail-only restore behaves like fresh tail-only while full-prompt resend works through prefix matching.

Track 02 should first determine the smallest feasible lower-level route:

1. llama.cpp native command or small C/C++ harness using the llama.cpp API.
2. A Python binding only if it exposes true prefill, state save, state restore, and append semantics.
3. Server API only if it exposes an operation that demonstrably appends tail tokens to restored `n_past` without requiring full prompt resend.

If no available route can perform native live append, stop and report that the runtime surface is insufficient for a KV capsule test.

## Metrics

For every control:

- exact answer match
- answer-contained/extractable match
- response hash
- output status: exact, contains extra text, missing, malformed, error
- prompt eval tokens
- prompt eval time
- decode time
- total latency
- prefix token count
- tail token count
- `n_past` before tail append
- capsule bytes
- capsule save time
- capsule restore time
- model hash
- tokenizer/template hash or best available proxy
- backend version and runner hash
- failure class

## Decision Tree

### Best Result

```text
native_live_append_tail_only passes
native_restored_capsule_append_tail_only passes
server_restored_tail_only fails
```

Interpretation: semantic continuation is possible, but the current server tail-only route is the wrong abstraction. Track 02 should pursue a capsule-aware runtime path.

### Capsule-Incomplete Result

```text
native_live_append_tail_only passes
native_restored_capsule_append_tail_only fails
```

Interpretation: append semantics are valid, but the persisted capsule is missing required state or restoring it incorrectly.

### Runner-Inadequate Result

```text
native_live_append_tail_only fails
```

Interpretation: stop before persistence claims. The runner does not yet prove correct low-level continuation semantics.

### Prompt-Cache-Only Result

```text
server_documented_full_resend_cache_prompt passes
all hidden/capsule append paths fail
```

Interpretation: current usable path is prompt-cache reuse, not KV capsule continuation. This is still paper-useful as evidence that cache telemetry and documented prefix reuse are not semantic continuation contracts.

## Stop Rules

- Stop after Family 1 if full visible fails or fresh tail-only unexpectedly succeeds.
- Stop after Family 1 if native live append cannot be implemented or cannot beat fresh tail-only.
- Stop after Family 1 if restored capsule append behaves exactly like fresh tail-only in 10/10 cases and logs do not show valid `n_past` continuation.
- Do not run GraphWalks unless the codeword and key-value gates produce interpretable continuation evidence.

## Artifact Layout

Committed Track 02 summaries should go under:

```text
research/02-quality-gated-stateful-kv-reuse/experiments/kv-capsule-semantic-continuation-2026-06-04/
```

Prompt-bearing raw artifacts should stay under ignored Track 01 benchmark paths, for example:

```text
research/01-ssd-native-inference-current/benchmarks/kv-capsule-semantic-continuation-2026-06-04/raw/
research/01-ssd-native-inference-current/benchmarks/kv-capsule-semantic-continuation-2026-06-04/cache/
```

Minimum committed artifacts:

- `README.md`
- `summary.json`
- `case-metrics.json`
- `failure-classifications.json`
- `capsule-contract.md`
- `commands.md`
- `model-info.json`
- `artifact-manifest.json`

## Paper Framing If This Works

If capsule continuation passes the simple gates, Track 02 can frame the result as:

> A KV capsule is not a cache blob. It is a resumable inference state with a semantic contract.

The novelty wedge becomes semantic contracts for local-agent state reuse: when hidden state, visible prompt replay, prefix-cache reuse, evidence slices, recompute, or fallback are valid representations of task context.

## Paper Framing If This Fails

If capsule continuation fails while documented prompt-cache reuse works, Track 02 still has a useful negative result:

> Prefix cache reuse is not semantic continuation. Mechanical KV save/restore and cache telemetry are insufficient evidence that hidden prefix state participates in later attention.

This supports a conformance/fallback paper rather than a speedup-only paper.

