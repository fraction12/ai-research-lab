## Why

The hot-cache benchmark proved that cached prefixes can reduce prompt evaluation, but it still restores the whole slot before every measured turn. Real local-agent loops are session-shaped: restore reusable state once, keep the llama.cpp slot warm, and run many changed-tail turns against that resident state.

## What Changes

- Add a Flashcache wrapper benchmark cache mode that measures session-resident prefix reuse.
- Prewarm the selected reusable prefix outside measured runs, restore it once at session start, then measure changed-tail completions while the slot remains resident.
- Record session setup telemetry separately from measured wrapper runs so restore cost is not hidden inside per-turn timing.
- Extend benchmark summaries/specs to recognize the new cache mode and session setup timing.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `llama-cpp-agent-cache-wrapper`: Add session-resident wrapper benchmark behavior.
- `benchmark-result-summary`: Summarize session setup timing for Flashcache wrapper benchmark results.

## Impact

- Affects `benchmarks/flashcache_wrapper_benchmark.py`, `benchmarks/summarize_results.py`, tests, and OpenSpec specs.
- Does not change the public wrapper HTTP API or require new dependencies.
- Does not claim lower-level partial KV restore; this remains a benchmark harness around llama.cpp slot behavior.
