## Why

The session-cache benchmark showed that restoring a prefix once and then replaying full prompts does not preserve the hot-cache win: the first measured full prompt still reprocesses the prefix. The next experiment must test the product-shaped path directly: restore the stable prefix once, then send only changed tails into that resident slot.

## What Changes

- Add a `session-tail` Flashcache wrapper benchmark cache mode.
- Require persistent server mode for `session` and `session-tail` cache modes.
- Reuse the existing prewarm and one-time restore setup, but measure tail-only completions after restore.
- Mark measured tail-only runs distinctly from restore-every-turn and full-prompt session runs.
- Repair and extend the benchmark summary spec so it covers server/cache modes, session setup telemetry, research figures, and tail-only session results.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `llama-cpp-agent-cache-wrapper`: Add tail-only session benchmark behavior.
- `benchmark-result-summary`: Preserve session/setup summary requirements while keeping research-figure generation requirements.

## Impact

- Affects `benchmarks/flashcache_wrapper_benchmark.py`, benchmark tests, summary tests, and OpenSpec specs.
- Does not change the public wrapper HTTP API.
- Produces a benchmark answer about llama.cpp slot semantics before we design a user-facing session API.
