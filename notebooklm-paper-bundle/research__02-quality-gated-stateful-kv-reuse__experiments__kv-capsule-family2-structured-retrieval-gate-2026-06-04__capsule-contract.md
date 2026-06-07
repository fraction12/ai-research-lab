# Family 2 Capsule Contract

Date: 2026-06-04

## Tested Contract

The Family 2 gate tested whether a native llama.cpp direct C API state capsule can preserve a compact structured prefix across save/restore:

```text
prefill(structured_prefix) -> llama_state_get_size/get_data -> new context -> llama_state_set_data -> append(query_tail) -> generate
```

The tail-only query did not resend the structured prefix text. The expected value was contained only in the prefix table/key-value facts.

## Runtime Route

- Full visible and prefix prefill: `add_special=true`
- Tail append: `add_special=false`
- State API: `llama_state_get_size`, `llama_state_get_data`, `llama_state_set_data`
- Runner: Python `ctypes` direct `libllama` C API against pinned b9493/GPT-OSS bundle
- Backend: `cuda_v13`

## Position Contract

For live append and restored capsule controls, the runner recorded:

- `n_past_before_tail_append = len(prefix_tokens)` before tail decode
- `generation_start_pos = len(prefix_tokens) + len(tail_tokens)` after tail decode

Mean live-append `n_past_before_tail_append`: 148.2
Mean restored-capsule `n_past_before_tail_append`: 148.2
Mean restored-capsule `generation_start_pos`: 165.4

## State Contract

Restored capsule ran on all 5 cases.

- Mean capsule bytes: 7288502.2
- Mean state bytes requested: 7288502.2
- Mean state bytes restored: 7288502.2
- Mean capsule save ms: 2.264920005109161
- Mean capsule restore ms: 149.17315999045968

## Validity Boundary

This contract is validated only for the 5-case Family 2 fabricated structured-retrieval gate. It does not establish GraphWalks, long-prefix reasoning, mini-graph, noiseless evidence, or broad benchmark correctness.
