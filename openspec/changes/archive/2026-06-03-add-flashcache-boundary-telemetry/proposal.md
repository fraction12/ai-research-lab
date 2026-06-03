## Why

Flashcache currently reports coarse cache state and prompt timing, but the next research step needs to show where time goes across the cache boundary before designing lower-level SSD-aware KV storage.

Without boundary telemetry, a saved second could be prefill avoidance, slot restore behavior, disk I/O, serialization overhead, runtime scheduling, or benchmark noise. We need the wrapper and result summaries to make those costs visible.

## What Changes

- Add a machine-readable `boundary_timings` object to Flashcache debug telemetry.
- Record wrapper-visible phases such as prompt assembly, cache lookup, prefix prime completion, slot save, slot restore, tail completion, direct completion, and total wrapper time.
- Preserve existing response shape and headers; no breaking API changes.
- Include boundary telemetry in Flashcache wrapper benchmark results.
- Extend benchmark summaries to surface boundary timing totals when available.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `llama-cpp-agent-cache-wrapper`: expose boundary timing telemetry for cache-aware and direct wrapper requests.
- `benchmark-result-summary`: summarize Flashcache boundary timing fields from benchmark result JSON.

## Impact

- `flashcache/wrapper.py`: capture wrapper-visible phase timings and return them in debug telemetry.
- `benchmarks/flashcache_wrapper_benchmark.py`: persist boundary timing telemetry for direct and cache-aware runs.
- `benchmarks/summarize_results.py`: include available boundary totals in summary rows.
- `tests/`: cover telemetry shape, debug output, benchmark persistence, and summary parsing.
