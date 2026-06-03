## Why

The first boundary telemetry run showed that named cache phases were small compared with total wrapper wall time. The likely missing cost is llama.cpp server lifecycle overhead from starting and stopping the backend around each wrapper request.

We need a persistent-server benchmark mode and explicit server context timings before designing lower-level SSD/KV storage. Otherwise we risk optimizing slot save/restore while the test harness is dominated by process lifecycle cost.

## What Changes

- Add wrapper boundary telemetry for server context enter and exit phases.
- Add a Flashcache wrapper benchmark mode that keeps a llama.cpp server alive across direct runs and wrapper cache-aware runs.
- Record `server_mode` in benchmark metadata so per-request and persistent-server results are not confused.
- Extend benchmark summaries with server context timing columns.
- Preserve the existing per-request benchmark mode as the default.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `llama-cpp-agent-cache-wrapper`: expose server lifecycle boundary timings and support a persistent-server benchmark mode.
- `benchmark-result-summary`: summarize server lifecycle boundary timing fields when available.

## Impact

- `flashcache/wrapper.py`: time managed server context enter/exit around completion, prime, save, and restore paths.
- `benchmarks/flashcache_wrapper_benchmark.py`: add `--server-mode per-request|persistent` and persistent-server execution paths.
- `benchmarks/summarize_results.py`: add server enter/exit boundary totals to summary output.
- `tests/`: cover lifecycle timing fields, persistent mode metadata, and summary parsing.
