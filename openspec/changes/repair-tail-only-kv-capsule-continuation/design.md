# Tail-Only KV Capsule Continuation Repair Design

## Prior Evidence Inventory

Current HEAD begins after `9a4ca0a Record KV capsule visible baseline rescue`. The relevant committed Track 02 artifacts are:

| Artifact | Decision | Meaning for this change |
| --- | --- | --- |
| `native-server-parity-bridge-2026-06-04` | `native_full_visible_parity_passed_family1_capsule_gate_not_run_in_this_script` | The accepted simple codeword prompt route can make native full-visible match server full-visible semantics on `3/3`. |
| `kv-capsule-family1-semantic-gate-2026-06-04` | `family1_restored_capsule_semantic_passed` | Strong tail-only restored capsule append passed `3/3` simple codeword cases. |
| `kv-capsule-family2-structured-retrieval-gate-2026-06-04` | `family2_restored_capsule_structured_retrieval_passed` | Strong tail-only restored capsule append passed `5/5` small structured retrieval cases. |
| `kv-capsule-family3-mini-graph-gate-2026-06-04` | `family3_stage_a_full_visible_guard_failed` | First boundary family: full-visible one-hop mini-graph passed only `2/3`, so capsule semantics were not tested. |
| `kv-capsule-visible-baseline-rescue-2026-06-04` | `visible_baseline_rescue_completed_without_interpretable_capsule_evidence` | Later rescue exposed route/protocol instability; useful as caution, not as a capsule negative. |

Interpretation: Family 1 `3/3` and Family 2 `5/5` are prior narrow positives, not final proof. Basic feasibility is not unknown, but the frontier is scaled reproduction, official-route triangulation, and boundary isolation.

## Source Refresh

Official llama.cpp server docs document fixed-slot prompt cache persistence through `--slot-save-path` plus `POST /slots/{id_slot}?action=save|restore`, with responses that include `n_saved`, `n_written`, `n_restored`, and `n_read`.

Official llama.cpp C API docs expose:

- Whole-context state: `llama_state_get_size`, `llama_state_get_data`, `llama_state_set_data`, `llama_state_save_file`, `llama_state_load_file`.
- Sequence state: `llama_state_seq_get_size`, `llama_state_seq_get_data`, `llama_state_seq_set_data`, `llama_state_seq_save_file`, `llama_state_seq_load_file`.
- Extended sequence state flags including partial/SWA-only and on-device variants.

Design consequence: server `cache_prompt`/slot restore is useful as telemetry, but it generally remains a visible full-prompt-resend cache mechanism. The strongest tail-only contract should use native append semantics and, where possible, official sequence-state APIs or a tiny bridge compiled against exact headers/libs.

Sources:

- <https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md>
- <https://github.com/ggml-org/llama.cpp/blob/master/include/llama.h>

## Research Question

Can the pinned GPT-OSS llama.cpp stack reproducibly preserve reusable prefix state as a persisted capsule such that:

```text
restore(capsule(prefix)) + append(tail)
```

is semantically equivalent to evaluating:

```text
prefix + tail
```

without resending prefix text in the tail request?

## Semantic Contract

For each deterministic Family 1 case:

- Prefix `P`: simple codeword memory sentence using the prior parity-proven shape.
- Tail `T`: asks for the hidden codeword.
- Full-visible baseline: evaluate `P + T`, then greedily decode.
- Live append: evaluate `P`, then append/evaluate only `T` at the next position in the same context/sequence, then decode.
- Restored capsule: evaluate `P`, save prefix state, restore into a clean context/session/sequence, append/evaluate only `T`, then decode.

Pass criteria:

- Full-visible answer-contained: `30/30`.
- Fresh tail-only answer-contained: `0/30`, unless explicitly quarantined as leakage.
- Live append answer-contained: `30/30`.
- Restored capsule answer-contained: `30/30`.
- Restored output need not exact-match if answer-contained scoring is already accepted for GPT-OSS verbosity, but exact/normalized status must be recorded separately.

## Route Ladder

### A. Environment and Inventory

- Verify HEAD, OpenSpec status, raw ignored paths, DushyantPC checkout, model path, runner path, backend, GPU visibility, process state, and previous artifacts.
- Preserve model hash, runner/lib hashes, command lines, prompt hashes, raw response hashes, and raw artifact locations.

### B. Official Server Diagnostics

Purpose: refresh the known-good server route and record why it is not the final strong contract.

Controls:

- Server full-visible `P + T`, 3-smoke then optionally 30 if cheap.
- Server full-prompt resend with `cache_prompt: true` and explicit `id_slot`.
- Server slot save/restore with `--slot-save-path`, then full-prompt resend with `cache_prompt: true`.

Record:

- `id_slot`, save/restore telemetry, prompt/evaluated token counts if exposed, timing fields, server logs for cache/restore/full-reprocessing warnings.
- Any SWA/hybrid warnings such as full prompt re-processing due to lack of cache data.

Interpretation:

- This route cannot satisfy the strong contract unless it can append tail-only into restored slot state without resending prefix text.

### C. Native Live Append Gate

Use native direct C API with the prior parity-proven prompt/token route:

- Full/prefix start tokenization: `add_special=true`.
- Appended tail tokenization: `add_special=false`.
- Decode `P` with positions starting at `0`, then `T` at `len(prefix_tokens)`.
- Set logits on the final tail token before generation.

If live append fails:

- Fix tokenization, BOS/template route, positions, sequence id, logits flags, greedy sampler, generation loop, or batch chunking.
- Do not interpret restored capsule until live append reaches `30/30` or a concrete blocker is proven.

### D. Native Restored Capsule Gate

Preferred order:

1. Official sequence file route: `llama_state_seq_save_file` / `llama_state_seq_load_file`.
2. Official sequence memory route: `llama_state_seq_get_size` / `get_data` / `set_data`.
3. Whole-context state route only as a compatibility fallback, clearly labeled.

Record:

- API route used.
- `seq_id`.
- Prefix token count.
- `n_past_before_tail_append`.
- `generation_start_pos`.
- State/capsule bytes and hash.
- Save/restore ms.
- Whether sampler state was reset/recreated.
- Whether restored token count was returned by file APIs.

### E. Tiny C/C++ Bridge if Needed

If Python `ctypes` is too fragile or lacks the exact sequence-state ABI:

- Locate exact llama.cpp headers/source on DushyantPC, or clone/build a compatible source checkout if already approved and bounded.
- Build a minimal C/C++ bridge/tool against the exact installed headers/libs.
- Keep the tool experiment-local and raw/ignored.
- Emit sanitized JSON plus raw ignored records.

### F. Expansion Only After Family 1 `30/30`

After Family 1 restored capsule passes:

1. Scale Family 2 structured retrieval beyond 5 cases.
2. Redesign Family 3 full-visible mini-graph guard.
3. Stop and ask orchestration before any GraphWalks/noiseless/broad benchmark.

## Stop Rules

- Stop before model-bearing work if OpenSpec validation fails or raw paths are not ignored.
- Do not stop at first protocol error; repair/escalate through the route ladder.
- Do not interpret restored capsule if full-visible or live append fails.
- Do not accept a no-go report until official server diagnostics, native live append, native sequence-state save/load, and C/C++ bridge feasibility have been tried or proven unavailable.
- Do not claim universal impossibility; classify blockers as model-specific, backend-specific, API-specific, or route-specific.

## Artifact Boundary

Committed Track 02 summaries:

```text
research/02-quality-gated-stateful-kv-reuse/experiments/tail-only-kv-capsule-continuation-repair-2026-06-04/
```

Ignored prompt-bearing raw artifacts:

```text
research/01-ssd-native-inference-current/benchmarks/tail-only-kv-capsule-continuation-repair-2026-06-04/raw/
research/01-ssd-native-inference-current/benchmarks/tail-only-kv-capsule-continuation-repair-2026-06-04/cache/
```

Committed artifacts must not contain raw prompts, raw responses, expected strings, token ID arrays/slices, generated token arrays, top-k arrays, or state bytes.
