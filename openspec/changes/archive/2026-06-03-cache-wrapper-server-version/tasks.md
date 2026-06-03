## 1. Wrapper Version Cache

- [x] 1.1 Cache `llama_server_version()` on `FlashcacheWrapper` after the first lookup.
- [x] 1.2 Preserve `server_version_ms` boundary telemetry around both first lookup and cached reuse.
- [x] 1.3 Add a unit test proving repeated completions on one wrapper instance call `llama_server_version()` once.

## 2. Summary Visibility

- [x] 2.1 Add `boundary_server_version_ms` to Flashcache wrapper summary rows.
- [x] 2.2 Update summary tests for server-version timing output.

## 3. Validation and Benchmark

- [x] 3.1 Run focused tests and `openspec validate --all --strict`.
- [x] 3.2 Rerun the persistent-server PC benchmark and store the result dataset.
- [x] 3.3 Archive the OpenSpec change after implementation.
