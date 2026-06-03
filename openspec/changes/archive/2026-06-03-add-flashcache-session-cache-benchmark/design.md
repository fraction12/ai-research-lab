## Context

Current Flashcache wrapper benchmarks have two cache modes:

- `cold`: the first measured cache-aware turn can miss, prime the prefix, save a slot file, and continue.
- `hot`: the benchmark prewarms the prefix first, then every measured turn restores the saved slot before completion.

`hot` isolates cache-hit behavior, but it still charges `slot_restore_ms` once per turn. A real local agent session should restore reusable state once at session start, then keep the llama.cpp slot resident while multiple changed-tail turns run.

## Decision

Add a `session` cache mode to `benchmarks/flashcache_wrapper_benchmark.py`.

The mode will require `--server-mode persistent`, because session residency only makes sense while one wrapper-side llama.cpp server remains alive. The benchmark will:

1. prewarm the cache with the first selected scenario using the existing wrapper flow,
2. start a persistent wrapper server,
3. restore the selected prefix slot once into that server,
4. run all selected changed-tail scenarios through direct llama.cpp completions against the resident slot without per-turn restore,
5. write the one-time restore/setup telemetry to `wrapper_session_setup`,
6. keep measured runs in `wrapper_cache_aware` so existing comparison logic continues to work.

Measured session runs will mark `cache_state` as `session-hit`. The prompt sent to llama.cpp will remain the full prompt for now. This preserves comparability with hot mode while testing whether llama.cpp's in-session prompt cache can avoid reprocessing the already-resident prefix on aligned full prompts.

## Alternatives Considered

- Add public HTTP session APIs now. Rejected for this step because the next unknown is benchmark value, not API shape.
- Send only volatile tails after restore. Rejected for this step because llama.cpp slot semantics still need comparable full-prompt alignment first; tail-only behavior can follow if the session benchmark shows value.
- Mutate `hot` mode. Rejected because restore-every-turn and restore-once answer different questions and should remain separately comparable.

## Risks

- llama.cpp may still reprocess some prefix tokens even after one restore if prompt alignment or cache semantics do not match expectations.
- A session-resident benchmark is not crash-persistent by itself; persistence still comes from the prewarm/slot file and the one-time restore.
- If users run `session` with per-request server mode, the benchmark would produce misleading data, so the CLI should reject that combination.

## Validation

- Unit test summary parsing for session setup timing and `session` cache mode.
- Unit test benchmark helper behavior where practical without launching llama.cpp.
- Run Python compile checks, unit tests, `openspec validate --all --strict`, and benchmark CLI help.
