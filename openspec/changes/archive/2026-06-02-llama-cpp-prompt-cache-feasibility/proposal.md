## Why

The positioning docs raised the bar: llama.cpp prompt/cache reuse is now a close baseline that this project must understand before building custom SSD-backed KV persistence. The next step is a feasibility benchmark that tests whether llama.cpp can persist and restore reusable workflow prompt state across server restarts.

## What Changes

- Add a llama.cpp prompt-cache feasibility benchmark for the LightningITB workflow fixture.
- Exercise llama.cpp server `/completion` with `cache_prompt` and slot save/restore endpoints.
- Record prompt timing, slot save/restore timing, cache file bytes, and baseline versus restored-prefix deltas.
- Document whether llama.cpp already closes the Ollama warm-vs-restarted persistence gap.

## Capabilities

### New Capabilities

- `llama-cpp-prompt-cache-benchmark`: Measure llama.cpp prompt cache reuse and slot save/restore behavior for local-agent workflow fixtures.

### Modified Capabilities

None.

## Impact

- Adds a benchmark script under `benchmarks/`.
- Adds ignored generated artifacts for llama.cpp models, slot caches, and results.
- May install llama.cpp via Homebrew and download a small GGUF model locally for benchmarking.
- Does not implement custom KV storage yet.
