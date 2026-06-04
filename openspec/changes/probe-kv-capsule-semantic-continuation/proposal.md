## Why

The documented llama.cpp server cache-reuse probe showed that the pinned GPT-OSS path works when the caller resends the full visible `prefix + tail` prompt with `cache_prompt: true` and an explicit slot. That is useful prompt-cache reuse, but it is not invisible semantic continuation. The earlier hidden-prefix semantic-continuation gate showed that restored-slot tail-only completion behaved exactly like fresh tail-only in 10/10 codeword cases despite slot save/restore telemetry.

Track 02 now needs the sharper fork: can a lower-level runner create a persisted KV capsule for a prefix, restore it, and append only new tail tokens while preserving the semantic behavior of the full visible prompt?

## What Changes

- Add a narrowly scoped KV capsule semantic-continuation probe, starting with a lower-level runner feasibility gate.
- Treat `native_live_append_tail_only` as the first required proof of append semantics before making any persistence claim.
- Treat `native_restored_capsule_append_tail_only` as the main result only after live append is semantically valid.
- Preserve the documented server full-prompt resend route as a known working control, not as the target result.
- Run the experimental ladder in order: codeword gate, key-value gate, mini graph gate, and the six historical GraphWalks cases only if earlier gates are interpretable and positive enough.
- Preserve exact runner/model/backend hashes, prompt hashes, state/capsule telemetry, response hashes, timing, failure classifications, and raw prompt-bearing artifacts.

## Capabilities

### New Capabilities
- `kv-capsule-semantic-continuation`: Defines the capsule contract, lower-level runner feasibility gate, controls, metrics, stop rules, artifact layout, and decision tree for tail-only semantic continuation after live or restored prefix state.

### Modified Capabilities
- `llama-cpp-agent-cache-wrapper`: Add requirements for distinguishing documented full-prompt cache reuse from lower-level native append and restored-capsule continuation.

## Impact

- Affected experiment artifacts: Track 02 summaries under `research/02-quality-gated-stateful-kv-reuse/experiments/kv-capsule-semantic-continuation-2026-06-04/`.
- Affected raw artifacts: prompt-bearing prompts, responses, runner outputs, cache/capsule files, and logs under `research/01-ssd-native-inference-current/benchmarks/kv-capsule-semantic-continuation-2026-06-04/`.
- Affected research docs: preserve `research/02-quality-gated-stateful-kv-reuse/docs/kv-capsule-semantic-continuation-experiment-2026-06-04.md` as the design source for this probe.
- No Track 01 harness changes are required unless the feasibility gate proves the ignored runner cannot express the required low-level continuation controls.
