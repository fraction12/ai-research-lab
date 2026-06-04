## Context

The latest Track 02 KV capsule probe ended at commit `e5a7f3e` with:

```text
decision: native_prompt_generation_protocol_blocker
overall_result: restored_capsule_semantics_uninterpretable
```

What is known:

- Direct `libllama.dll` C API calls are reachable through Python `ctypes`.
- The pinned GPT-OSS bundle provenance was identified as llama.cpp tag `b9493`, commit `a731805cedc83c0514cbd808a2e38ec46c759cc2`.
- Token smoke passed with the pinned `llama_tokenize(const llama_vocab *, ...)` signature.
- CUDA backend loaded from `cuda_v13`, with accepted-run logs showing KV and compute buffers on `CUDA0`.
- Native state APIs are reachable.
- Native full-visible generation did not reproduce server full-visible behavior and emitted repeated newline tokens.

Pinned continuity path:

```text
server: C:\Users\Dushyant\Tools\llama-ollama-a731805ce-gptoss\llama-server.exe
bundle: C:\Users\Dushyant\Tools\llama-ollama-a731805ce-gptoss
model:  C:\Users\Dushyant\.ollama\models\blobs\sha256-e7b273f9636059a689e3ddcab3716e4f65abe0143ac978e46673ad0e52d09efb
```

## Research Question

Can the native direct C API path reproduce the known-good server full-visible codeword behavior when prompt bytes, tokenization, BOS/chat-template behavior, sampler settings, logits handling, and generation loop are matched?

## Goals / Non-Goals

**Goals:**

- Refresh a small live server full-visible baseline for 3 deterministic codeword variants.
- Compare native tokenization against server tokenization when available.
- Deliberately test special-token handling, prompt/template route, logits selection, and sampler behavior.
- Run native full-visible only after selecting the most plausible parity route.
- If native full-visible parity passes, rerun only Family 1 KV capsule gates.
- Preserve hashes, token counts, response hashes, selected non-prompt-bearing excerpts, timings, backend/model hashes, and failure classes.

**Non-Goals:**

- No broad benchmark.
- No GraphWalks run unless Family 1 capsule gates become positive and interpretable in a later approved step.
- No claim that server `cache_prompt:true` full-prompt resend is a KV capsule.
- No rewrite of the previous `probe-kv-capsule-semantic-continuation` result.

## Experimental Ladder

Run stages in order and stop when a stop rule triggers.

| Stage | Purpose | Advance condition |
| --- | --- | --- |
| `server_baseline_capture` | Refresh known-good full-visible server behavior on 3 deterministic codeword variants. | Server answer-contained passes for the small set. |
| `tokenization_parity` | Compare server/native tokenization or best available proxies for exact prompt bytes. | A native special-token route is selected or blocker recorded. |
| `prompt_template_parity` | Test raw completion prompt versus any GPT-OSS server template/BOS behavior. | Prompt route selected or blocker recorded. |
| `logits_sampler_sanity` | Rule out wrong logits index, broken token-to-piece conversion, or degenerate sampler loop. | Native first-token/generation route is plausible. |
| `native_full_visible_parity_gate` | Test native full-visible on the small codeword set. | Native answer-contained matches server baseline. |
| `family1_capsule_gate` | Only if parity passes, rerun codeword capsule controls. | Native live append must pass before restored capsule interpretation. |

## Controls

### Server Baseline Controls

| Control id | Purpose |
| --- | --- |
| `server_full_visible_no_cache` | Refreshed semantic positive control for exact prompt/model/backend family. |
| `server_tokenize_exact_prompt` | Tokenization evidence if the server exposes a tokenization endpoint. |

### Native Parity Controls

| Control id | Purpose |
| --- | --- |
| `native_tokenize_add_special_true` | Test native special-token route with BOS/template-like special handling. |
| `native_tokenize_add_special_false` | Test raw native token route. |
| `native_prompt_raw_completion` | Test native generation on raw prompt bytes. |
| `native_prompt_template_or_bos_route` | Test native generation on the selected template/BOS route when available. |
| `native_logits_sampler_probe` | Inspect first-token/top-k/sampled-token behavior before full generation. |
| `native_full_visible_prefix_plus_tail` | Main parity gate. |

### Capsule Controls, Only If Parity Passes

| Control id | Purpose |
| --- | --- |
| `full_visible_prefix_plus_tail` | Native positive control. |
| `fresh_tail_only` | Negative leakage control. |
| `native_live_append_tail_only` | Required proof of append semantics without persistence. |
| `native_restored_capsule_append_tail_only` | Main restored-state result, interpreted only after live append passes. |
| `wrong_capsule_negative` | Optional fail-closed negative control when technically safe. |
| `corrupt_or_shifted_position_negative` | Optional fail-closed negative control when technically safe. |

## Metrics

Every case/control record should include:

- exact answer match
- answer-contained / extractable-answer match
- output status: `exact_only`, `contains_with_extra_text`, `missing`, `malformed`, or `error`
- response hash and normalized response hash
- prompt hash, prefix hash, tail hash, request hash, and config hash
- prompt byte count and prompt token count
- server token count and token hash when available
- native token count, first/last token IDs or token hashes, and `add_special` route
- selected prompt/template/BOS route
- logits index used, top-k token IDs or hashed pieces when feasible
- prompt eval tokens and milliseconds
- predicted tokens, decode milliseconds, total latency
- backend/model/server/lib hashes and runner path
- failure class

Capsule controls, if run, must also include:

- prefix token count and tail token count
- `n_past_before_tail_append`
- `generation_start_pos`
- `state_bytes_requested`
- `state_bytes_restored`
- capsule bytes
- save/restore time

## Failure Classes

Use these classes in `failure-classifications.json`:

- `passed`
- `server_model_prompt_setup_issue`
- `native_tokenization_protocol_blocker`
- `native_prompt_template_protocol_blocker`
- `native_logits_sampler_blocker`
- `native_server_parity_failure`
- `native_live_append_failure`
- `capsule_persistence_state_incomplete`
- `fresh_tail_expected_miss`
- `wrong_capsule_leak_or_false_pass`
- `position_or_compatibility_issue`
- `parse_failure`
- `runtime_or_backend_failure`
- `ambiguous`

## Decision Tree

- If refreshed server full-visible fails, classify `server_model_prompt_setup_issue` and stop before native parity claims.
- If server/native tokenization cannot be made reliable or comparable enough, classify `native_tokenization_protocol_blocker` and stop.
- If tokenization is reliable but native prompt/template route cannot reproduce plausible server behavior, classify `native_prompt_template_protocol_blocker` and stop.
- If prompt route is plausible but logits/sampler behavior is degenerate, classify `native_logits_sampler_blocker` and stop.
- If native full-visible still misses after bounded attempts, classify `native_server_parity_failure` with the narrowest observed blocker and stop.
- If native full-visible passes, rerun Family 1 capsule gates.
- If native live append fails after parity passes, classify `native_live_append_failure` and do not interpret restored capsule.
- If native live append passes but restored capsule behaves like fresh tail-only, classify `capsule_persistence_state_incomplete`.

## Artifact Layout

Prompt-bearing raw artifacts stay under ignored Track 01 paths:

```text
research/01-ssd-native-inference-current/benchmarks/native-server-parity-bridge-2026-06-04/raw/
```

Committed Track 02 summaries live under:

```text
research/02-quality-gated-stateful-kv-reuse/experiments/native-server-parity-bridge-2026-06-04/
```

Required committed files:

```text
README.md
summary.json
case-metrics.json
failure-classifications.json
commands.md
model-info.json
artifact-manifest.json
```

If KV capsule gates are rerun, include `capsule-contract.md` with deltas or a link back to the existing capsule contract.

## Migration Plan

Create this OpenSpec change, validate it, add ignore coverage for the raw path if needed, build or extend only ignored local harness scripts, run the ladder until a stop rule triggers, import sanitized summaries, validate OpenSpec again, and commit locally without pushing.
