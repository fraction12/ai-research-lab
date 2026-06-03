## 1. Server Lifecycle Telemetry

- [x] 1.1 Add wrapper instrumentation for `server_enter_ms` and `server_exit_ms`.
- [x] 1.2 Preserve existing boundary telemetry fields and response headers.

## 2. Persistent Benchmark Mode

- [x] 2.1 Add `--server-mode per-request|persistent` to the Flashcache wrapper benchmark.
- [x] 2.2 Run direct full-prompt scenarios through one persistent server when persistent mode is selected.
- [x] 2.3 Run wrapper cache-aware scenarios through a separate persistent server when persistent mode is selected.
- [x] 2.4 Persist selected server mode and lifecycle boundary timings in result JSON.

## 3. Summary and Tests

- [x] 3.1 Add server context timing columns to benchmark summaries.
- [x] 3.2 Add or update tests for lifecycle timing and summary parsing.
- [x] 3.3 Run focused unit tests and `openspec validate --all --strict`.
