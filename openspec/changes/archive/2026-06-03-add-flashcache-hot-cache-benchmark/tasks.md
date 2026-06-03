## 1. Hot Cache Benchmark Mode

- [x] 1.1 Add `--cache-mode cold|hot` to the Flashcache wrapper benchmark with `cold` as the default.
- [x] 1.2 Prewarm the wrapper cache before measured wrapper turns when hot mode is selected.
- [x] 1.3 Persist `cache_mode` metadata and separate `wrapper_prewarm` telemetry in result JSON.
- [x] 1.4 Keep direct baseline and persistent-server behavior unchanged.

## 2. Summary and Tests

- [x] 2.1 Add cache-mode output to benchmark summaries.
- [x] 2.2 Update tests for cache-mode parsing/rendering.
- [x] 2.3 Run focused unit tests and `openspec validate --all --strict`.

## 3. Benchmark and Archive

- [x] 3.1 Rerun the PC persistent-server benchmark with hot cache mode and store the dataset.
- [x] 3.2 Archive the OpenSpec change after implementation.
