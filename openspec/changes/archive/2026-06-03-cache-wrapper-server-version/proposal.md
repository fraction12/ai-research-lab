## Why

The persistent-server benchmark showed that `server_enter_ms` and `server_exit_ms` are now tiny, but wrapper wall time is still dominated by repeatedly shelling out to `llama-server --version`.

We need to cache server-version identity per wrapper/config instance so repeated agent turns measure cache mechanics and model work instead of repeated binary introspection.

## What Changes

- Cache the llama.cpp server version after the first lookup on a `FlashcacheWrapper` instance.
- Preserve the server version as a cache-key compatibility input.
- Keep `server_version_ms` boundary telemetry, but make repeated requests measure the cached lookup path.
- Add summary output for total `server_version_ms` so benchmark runs expose this cost directly.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `llama-cpp-agent-cache-wrapper`: server-version identity is reused within a wrapper instance while remaining part of cache-key compatibility.
- `benchmark-result-summary`: summarize server-version boundary timing totals when available.

## Impact

- `flashcache/wrapper.py`: store first server-version result on the wrapper instance.
- `benchmarks/summarize_results.py`: include a server-version timing column.
- `tests/`: cover version lookup reuse and summary parsing.
