## Why

The previous KV capsule semantic-continuation probe reached the direct llama.cpp C API, loaded CUDA on DushyantPC, passed token smoke, and exposed `llama_state_get_size`, `llama_state_get_data`, and `llama_state_set_data`. It still stopped before any KV-capsule interpretation because native `full_visible_prefix_plus_tail` emitted repeated newline tokens and failed the codeword positive control.

Prior server controls on the same pinned GPT-OSS model family showed full-visible/documented-cache codeword behavior can work. Therefore Track 02 needs a native/server parity bridge before it can interpret native live append or restored capsule results. The bridge asks whether the native direct C API harness can reproduce the known-good server full-visible behavior when prompt bytes, tokenization, BOS/chat-template behavior, sampler settings, logits handling, and generation loop are matched.

## What Changes

- Add a narrowly scoped native/server parity bridge experiment before rerunning KV capsule semantic-continuation gates.
- Refresh a small live server full-visible codeword baseline instead of relying only on prior 10/10 results.
- Compare server and native tokenization where possible, deliberately testing `add_special=true` and `add_special=false`.
- Test prompt formatting/template/BOS routes and sampler/logits handling before long native generation.
- Gate all KV capsule interpretation on native full-visible parity.
- If native full-visible parity passes, rerun only the Family 1 codeword KV capsule gates before any larger ladder.
- Preserve prompt-bearing requests, responses, logs, and state bytes only under ignored Track 01 benchmark paths, while committing Track 02 summaries.

## Capabilities

### New Capabilities
- `native-server-parity-bridge`: Defines the server-baseline capture, tokenization parity, prompt/template parity, logits/sampler sanity, native full-visible parity gate, stop rules, artifacts, and interpretation for making the native direct API runner trustworthy.

### Modified Capabilities
- `kv-capsule-semantic-continuation`: Adds an explicit prerequisite that native full-visible parity must pass before `native_live_append_tail_only` or `native_restored_capsule_append_tail_only` results can be interpreted.
- `llama-cpp-agent-cache-wrapper`: Adds requirements for preserving server request/tokenization/cache evidence used to compare server and native completion paths.

## Impact

- Affected experiment artifacts: new Track 02 summaries under `research/02-quality-gated-stateful-kv-reuse/experiments/native-server-parity-bridge-2026-06-04/`.
- Affected raw artifacts: prompt-bearing requests, responses, console logs, tokenization traces, and optional capsule/state files under `research/01-ssd-native-inference-current/benchmarks/native-server-parity-bridge-2026-06-04/raw/`.
- Prior evidence preserved: `research/02-quality-gated-stateful-kv-reuse/experiments/kv-capsule-semantic-continuation-2026-06-04/` remains the packaged `native_prompt_generation_protocol_blocker` result and is not rewritten.
- No Track 01 harness changes are expected unless the bridge proves the ignored runner cannot express the needed parity controls.
