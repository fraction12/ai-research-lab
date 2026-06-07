# KV Capsule Contract Status

This run did not reach a valid KV-capsule semantic test because the native full-visible positive control failed. The contract fields below describe what the direct API route can currently observe, not a validated capsule.

| Field | Status | Evidence |
| --- | --- | --- |
| Model hash | Captured | `E7B273F9636059A689E3DDCAB3716E4F65ABE0143AC978E46673AD0E52D09EFB` |
| Runner / server hash | Captured | `llama-server.exe` hash `765422B969681C910460FC77A49E08610E51B1730BE00A79015DA67E7C1798B6`; `libllama.dll` hash `9B707D4886051671B8C94BB5A2F3F07DD0868A5BFB34EE163C080D91555E2310` |
| Source / ABI identity | Captured with risk | Pinned provenance identified as tag `b9493`, commit `a731805cedc83c0514cbd808a2e38ec46c759cc2`; direct `ctypes` ABI remains bounded-risk. |
| Tokenizer identity | Captured proxy | `tokenizer.ggml.model = gpt2`; token smoke passed with pinned `llama_tokenize(const llama_vocab *, ...)` signature. |
| Chat template / prompt formatting | Missing for parity | Native prompt bytes were simple text and did not yet reproduce server full-visible codeword behavior. |
| Prefix token ids/hash | Captured proxy | Token counts and prompt hashes recorded in `case-metrics.json`; raw token IDs for token smoke in raw artifact. |
| Sequence length / n_past | Captured for accepted records | `n_past_before_tail_append` and `generation_start_pos` recorded separately. |
| Per-layer K/V tensors | Captured only as opaque state bytes | `llama_state_get_data` produced state bytes for restored controls; not semantically validated. |
| RoPE / position state | Inferred only | Position values supplied explicitly; internal RoPE state not separately inspected. |
| Attention mask / sequence identity | Partially captured | Sequence id 0 used in batch construction; no independent mask audit. |
| KV layout metadata | Inferred from backend logs | Console shows CUDA0 KV buffers and SWA/non-SWA cache split. |
| Hybrid / SWA state | Partially captured | Model reports `model_n_swa = 128`; logs show full-size SWA cache. Capsule semantics not validated. |
| Backend version / serialization format | Partially captured | Bundle hashes and source tag captured; opaque state format not decoded. |
| Validity policy | Not established | No tails are certified appendable until native full-visible protocol parity passes. |

## Contract Decision

No valid KV capsule contract is established by this run. The next required step is native/server full-visible parity before capsule persistence can be interpreted.
