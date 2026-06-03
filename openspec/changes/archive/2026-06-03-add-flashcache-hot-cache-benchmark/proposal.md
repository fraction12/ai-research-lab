## Why

The latest persistent-server benchmark still mixes two different costs: first-turn cache fill and steady-state cache hits. For local agents, the more important product question is how fast repeated turns are after a stable prefix slot already exists on SSD.

We need a hot-cache benchmark mode that prewarms the Flashcache slot outside the measured wrapper comparison, then measures only cache-hit turns.

## What Changes

- Add a Flashcache wrapper benchmark cache mode that separates cold prewarm from measured cache-hit turns.
- Preserve the existing mixed miss-plus-hit benchmark as the default.
- Store selected cache mode in benchmark metadata.
- Store prewarm telemetry separately from measured wrapper runs.
- Extend summaries and tests so hot-cache results show measured cache states and cache mode clearly.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `llama-cpp-agent-cache-wrapper`: wrapper benchmark supports hot-cache measurement where the reusable prefix is primed before measured cache-aware turns.
- `benchmark-result-summary`: summaries report selected cache mode when available.

## Impact

- `benchmarks/flashcache_wrapper_benchmark.py`: add cache-mode option and prewarm flow.
- `benchmarks/summarize_results.py`: include cache mode in summary output.
- `tests/`: cover metadata and summary rendering for cache mode.
