## Why

The hidden-prefix semantic-continuation gate showed that restored-slot tail-only completion behaves like fresh tail-only for the pinned GPT-OSS llama.cpp path, despite mechanical slot save/restore telemetry. The next fork is to test the documented server cache-reuse route: restore a slot, resend the full `prefix + tail` prompt with `cache_prompt: true` and explicit `id_slot`, and let llama.cpp prefix-match restored state so only the unseen suffix should be evaluated.

## What Changes

- Add a narrowly scoped documented server cache-reuse probe for 10 deterministic codeword variants.
- Compare clean full-visible, fresh tail-only, restored tail-only, restored full-prompt with `cache_prompt: true`, and optional clean full-prompt with `cache_prompt: true`.
- Preserve exact request payloads, prompt hashes, raw outputs, strict/extractable answer scores, slot save/restore telemetry, response timings, and server-log cache evidence.
- Commit Track 02 summaries and keep prompt-bearing request/response/log artifacts under ignored Track 01 benchmark paths.
- Do not run GraphWalks or noiseless-evidence controls in this change.

## Capabilities

### New Capabilities
- `documented-server-cache-reuse`: Defines the focused llama.cpp server cache-reuse probe, controls, metrics, artifact layout, log evidence, and decision tree for full-prompt resend cache matching.

### Modified Capabilities
- `llama-cpp-agent-cache-wrapper`: Add requirements for distinguishing hidden tail-only continuation from documented full-prompt cache reuse with explicit slot/prefix matching.

## Impact

- Affected experiment artifacts: Track 02 summaries under `research/02-quality-gated-stateful-kv-reuse/experiments/documented-server-cache-reuse-2026-06-04/`.
- Affected local raw artifacts: prompt-bearing requests, responses, logs, and slot cache files under `research/01-ssd-native-inference-current/benchmarks/documented-server-cache-reuse-2026-06-04/`.
- Affected repository hygiene: ignored raw benchmark paths must cover the documented server cache-reuse probe.
- No Track 01 harness changes are required unless the ignored local runner cannot faithfully express the controls.
