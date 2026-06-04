## Context

Track 02 has two important prior controls:

```text
hidden-prefix semantic-continuation gate:
  full visible contained answer:        10/10
  fresh tail-only contained answer:      0/10
  restored tail-only contained answer:   0/10
  restored response equaled fresh:      10/10

documented server cache-reuse probe:
  restored full prompt + cache_prompt:  10/10
  mean prompt tokens:                   19.0 versus 31.0 full no-cache
```

Together these show that documented visible-prefix cache reuse works for the pinned GPT-OSS llama.cpp path, but current server restored tail-only usage is not a semantic continuation primitive. The next experiment must test a lower-level inference-state contract rather than repeating the server `/completion` tail-only path.

Pinned continuity path:

```text
runner: C:\Users\Dushyant\Tools\llama-ollama-a731805ce-gptoss\llama-server.exe
model:  C:\Users\Dushyant\.ollama\models\blobs\sha256-e7b273f9636059a689e3ddcab3716e4f65abe0143ac978e46673ad0e52d09efb
```

The experiment will first determine whether a feasible lower-level route exists for the same model/backend family:

1. A llama.cpp native C/C++ harness using true prefill, state save, state restore, and append semantics.
2. A Python binding only if it exposes the same true continuation primitives.
3. A server/API route only if logs and telemetry prove tail tokens append to restored `n_past` without resending the prefix text.

## Goals / Non-Goals

**Goals:**

- Test whether native/live tail-only append after prefix prefill is semantically equivalent to full visible `prefix + tail`.
- Test whether a persisted/restored KV capsule can continue semantically with tail-only append.
- Preserve the documented full-prompt resend cache route as a control.
- Preserve exact model, runner, tokenizer/template proxy, backend, command lines, prompts, raw outputs, state/capsule telemetry, timing, and failure classifications.
- Stop early when the runner surface is insufficient or the codeword gate falsifies continuation semantics.

**Non-Goals:**

- No broad benchmark run.
- No GraphWalks run unless codeword and key-value gates are positive and interpretable.
- No claim that server `cache_prompt:true` full-prompt resend is a KV capsule.
- No use of the vault mind model.

## Capsule Contract

A valid capsule is a resumable inference state with a semantic contract, not only a byte blob. The committed `capsule-contract.md` and summaries must record which fields are captured, inferred, unavailable, or missing:

- model hash
- tokenizer identity or tokenizer hash proxy
- chat template / prompt formatting hash or best available proxy
- prefix token ids or prefix token hash
- sequence length / `n_past`
- per-layer K/V tensors
- RoPE or position state
- attention mask and sequence/slot identity
- KV quantization/layout metadata
- backend version and cache serialization format
- GPT-OSS or hybrid-model state limitations, including sliding-window, recurrent, or compressed-latent state if applicable
- validity policy for tails, runtime settings, and restore verification

## Experimental Ladder

Run families in order and stop when a stop rule is triggered.

| Family | Scope | Advance condition |
| --- | --- | --- |
| `codeword_gate` | 10 deterministic codeword variants | Full visible contains answer, fresh tail-only misses, and native live append is interpretable and beats fresh tail-only. |
| `key_value_gate` | 10 deterministic variants with 20 key/value pairs | Restored capsule retrieves requested values near full-visible behavior and beats fresh tail-only. |
| `mini_graph_gate` | Tiny synthetic `parents` graphs | Restored capsule matches full-visible behavior and beats fresh tail-only. |
| `graphwalks_six_case_gate` | `graphwalks-6`, `-9`, `-11`, `-13`, `-16`, `-19` | Only run if earlier gates support semantic continuation enough to justify structured GraphWalks interpretation. |

## Controls

Each case should include these controls when technically possible:

| Control id | Purpose |
| --- | --- |
| `full_visible_prefix_plus_tail` | Semantic positive control. |
| `fresh_tail_only` | Negative leakage control. |
| `server_documented_full_resend_cache_prompt` | Known working visible-prefix prompt-cache control. |
| `server_restored_tail_only` | Known failed server hidden-tail control. |
| `native_live_append_tail_only` | Required first proof that lower-level append semantics work without persistence. |
| `native_restored_capsule_append_tail_only` | Main result: save/restore capsule, then append tail only. |
| `wrong_capsule_negative` | Restoring a mismatched capsule should fail closed or clearly miss. |
| `corrupt_or_shifted_position_negative` | Wrong `n_past`, position, or slot metadata should fail closed or clearly degrade. |

## Metrics

Every case/control record must include:

- exact answer match
- answer-contained / extractable-answer match
- response hash and normalized response hash
- output status: `exact_only`, `contains_with_extra_text`, `missing`, `malformed`, or `error`
- prompt hash, prefix hash, tail hash, request/config hash where applicable
- prompt eval tokens and prompt eval milliseconds
- predicted tokens, decode milliseconds, total latency, and wall latency
- prefix token count, tail token count, and `n_past` before tail append
- capsule bytes, capsule save milliseconds, and capsule restore milliseconds
- model hash, tokenizer/template hash proxy, backend version, and runner hash
- failure class

## Failure Classes

Use these classes in `failure-classifications.json`:

- `passed`
- `fresh_tail_expected_miss`
- `runner_surface_insufficient`
- `native_live_append_failure`
- `semantic_restore_failure`
- `capsule_state_incomplete`
- `wrong_capsule_leak_or_false_pass`
- `position_or_compatibility_issue`
- `prompt_protocol_issue_contains_answer`
- `parse_failure`
- `runtime_or_slot_failure`
- `model_weakness`
- `ambiguous`

## Decision Tree

- If `native_live_append_tail_only` passes, `native_restored_capsule_append_tail_only` passes, and `server_restored_tail_only` fails, conclude semantic continuation is possible but the current server tail-only route is the wrong abstraction.
- If native live append passes but restored capsule append fails, conclude append semantics are valid but persisted capsule state is incomplete or restore is wrong.
- If native live append cannot be implemented or fails the codeword gate, stop before persistence claims and report the runner surface as insufficient or the runner semantics as broken.
- If documented full-prompt resend works but all hidden/capsule append paths fail, conclude the current usable path is prompt-cache reuse, not KV capsule continuation.
- If GPT-OSS architecture or native support makes the result ambiguous, add a stable non-hybrid/full-attention local model control before making general claims.

## Stop Rules

- Stop after the feasibility gate if no available route can perform native live append.
- Stop after Family 1 if full visible fails or fresh tail-only unexpectedly succeeds.
- Stop after Family 1 if native live append cannot be implemented or cannot beat fresh tail-only.
- Stop after Family 1 if restored capsule append behaves exactly like fresh tail-only in 10/10 cases and logs/telemetry do not show valid `n_past` continuation.
- Do not run GraphWalks unless codeword and key-value gates produce interpretable continuation evidence.

## Artifact Layout

Prompt-bearing raw artifacts stay under ignored Track 01 paths:

```text
research/01-ssd-native-inference-current/benchmarks/kv-capsule-semantic-continuation-2026-06-04/raw/
research/01-ssd-native-inference-current/benchmarks/kv-capsule-semantic-continuation-2026-06-04/cache/
```

Committed Track 02 summaries live under:

```text
research/02-quality-gated-stateful-kv-reuse/experiments/kv-capsule-semantic-continuation-2026-06-04/
```

Required committed files:

```text
README.md
summary.json
case-metrics.json
failure-classifications.json
capsule-contract.md
commands.md
model-info.json
artifact-manifest.json
```

The design source document must remain committed at:

```text
research/02-quality-gated-stateful-kv-reuse/docs/kv-capsule-semantic-continuation-experiment-2026-06-04.md
```

## Migration Plan

No production migration is required. Add the OpenSpec change, run the feasibility gate, implement the smallest real native continuation route if available, run only the allowed ladder until a stop rule triggers, import committed Track 02 summaries, validate OpenSpec, and commit locally if coherent.
