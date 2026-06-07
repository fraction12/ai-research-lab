# KV Capsule Semantic Continuation Experiment

Date: 2026-06-04

## Decision

`native_prompt_generation_protocol_blocker`

The direct llama.cpp C API route is reachable against the pinned GPT-OSS bundle, but this run does not test KV-capsule semantics. The accepted CUDA-backed Family 1 gate stopped because `full_visible_prefix_plus_tail` failed: native full-visible generation emitted repeated newline tokens and did not contain the codeword. Since the positive semantic control failed, `native_live_append_tail_only` and `native_restored_capsule_append_tail_only` are not evidence for or against KV capsules.

## What Worked

- Direct `libllama.dll` C API calls are reachable through Python `ctypes`; this is not a server wrapper.
- Required exports exist: `llama_tokenize`, `llama_decode`, `llama_state_get_size`, `llama_state_get_data`, and `llama_state_set_data`.
- The pinned source provenance was identified as upstream tag `b9493`, commit `a731805cedc83c0514cbd808a2e38ec46c759cc2`.
- Token smoke passed: plain ASCII `hello world` tokenized to 2 tokens; first codeword prefix and tail each tokenized to 24 tokens.
- The empty-batch issue was fixed by setting `batch.n_tokens`; the earlier all-runtime-error run is invalid and excluded.
- CUDA backend diagnosis passed. `cuda_v13/ggml-cuda.dll` loaded, `nvidia-smi` saw the Python process, and accepted-run logs show KV and compute buffers on `CUDA0`.

## What Failed

The native direct-API generation protocol did not reproduce the server/full-visible behavior. In the accepted run, full-visible responses were repeated newline tokens, with `answer_contained = false`. This indicates a native prompt/generation protocol parity problem, likely in prompt formatting, BOS/chat-template handling, sampler/logits handling, or generation-loop parity.

## Scores

Accepted records: 21. Complete cases: 5. The sixth case was stopped after `full_visible_prefix_plus_tail`.

| Control | Records | Answer contained | Exact match | Interpretation |
| --- | ---: | ---: | ---: | --- |
| `full_visible_prefix_plus_tail` | 6 | 0 | 0 | positive control failed; stops experiment |
| `fresh_tail_only` | 5 | 0 | 0 | not interpreted after positive-control failure |
| `native_live_append_tail_only` | 5 | 0 | 0 | not interpreted after positive-control failure |
| `native_restored_capsule_append_tail_only` | 5 | 0 | 0 | not interpreted after positive-control failure |

Family 2, Family 3, and GraphWalks were not run by stop rule.

## Raw Evidence

Prompt-bearing raw artifacts are ignored under:

```text
research/01-ssd-native-inference-current/benchmarks/kv-capsule-semantic-continuation-2026-06-04/raw/
```

Key raw files:

- `codeword-records.jsonl`: accepted CUDA-backed Family 1 partial run.
- `codeword-console.txt`: backend/load/context/generation logs.
- `token-smoke-run-info.json`: tokenization smoke gate.
- `gpu-backend-diagnostic.json`: bounded GPU backend diagnosis.
- `smoke-run-info.json`: direct API load/context smoke test.

## Next Direction

Run a server-parity native protocol bridge before any KV-capsule interpretation: reproduce the server full-visible codeword answer with exact prompt bytes/token IDs, chat/template/BOS handling, sampler settings, logits sanity, and generation-loop parity. Only after native full-visible parity passes should Track 02 rerun live append and restored capsule gates.
