## Context

Flashcache now records wrapper-visible boundary timings, but the first PC run showed a large difference between named phases and `total_wrapper_ms`. The wrapper currently opens a `ManagedLlamaServer` context for each direct, cache miss, and cache hit request. On Windows with a 20B GGUF model, server startup alone can take many seconds per request.

The benchmark needs a way to separate cache mechanics from process lifecycle cost. The wrapper also needs to make lifecycle cost explicit in its boundary telemetry.

## Goals / Non-Goals

**Goals:**

- Measure server context enter and exit time as first-class boundary phases.
- Add a benchmark mode where direct and wrapper phases use persistent llama.cpp server processes.
- Keep existing per-request benchmark behavior unchanged by default.
- Make persistent and per-request result JSONs distinguishable.

**Non-Goals:**

- No production server pool or daemon lifecycle manager.
- No change to cache key semantics, prompts, slot files, or cache policy.
- No claim that persistent-server prompt timings represent cold-start persistence behavior.
- No lower-level KV storage format work.

## Decisions

### Use `server_enter_ms` and `server_exit_ms`

Record the time spent entering and exiting `ManagedLlamaServer` contexts.

Rationale: `ManagedLlamaServer` may either start/stop a process or connect to an existing server, depending on config. `server_enter_ms` is more accurate than always calling the phase `server_start_ms`.

Alternative considered: only add persistent mode and skip lifecycle timing. Rejected because the previous benchmark showed a large unattributed wall-time gap that should be measured directly.

### Add `--server-mode` with `per-request` default

The benchmark SHALL keep current behavior unless users opt into `--server-mode persistent`.

Rationale: existing datasets remain comparable. Persistent mode becomes a diagnostic mode for isolating cache work from backend process startup.

Alternative considered: replace current behavior with persistent mode. Rejected because previous large-prefix results were collected in per-request mode and should remain reproducible.

### Use separate persistent servers for direct and wrapper phases

The benchmark starts one persistent server for direct full-prompt runs and another for wrapper cache-aware runs.

Rationale: this avoids direct baseline state contaminating wrapper cache state while still removing per-request process startup from both phases.

Alternative considered: reuse one server across all phases. Rejected because slot/cache state from direct prompts could affect wrapper measurements.

### Treat persistent direct timings as warm-server diagnostics

Persistent direct runs may benefit from llama.cpp in-session prompt cache behavior. They are useful for diagnosing "agent server stays alive" behavior, not for proving cold-start SSD persistence.

Rationale: this distinction keeps interpretation honest and avoids mixing benchmark modes.

## Risks / Trade-offs

- [Risk] Persistent direct runs can reduce baseline prompt timing by using in-session cache behavior. -> Mitigation: record `server_mode` and describe persistent mode as a diagnostic comparison.
- [Risk] Existing-server health checks still appear in `server_enter_ms`. -> Mitigation: use context wording rather than start-only wording.
- [Risk] Long-lived server state may carry slot state between wrapper turns. -> Mitigation: use a fresh cache directory for benchmark runs and separate direct/wrapper server processes.
- [Risk] Persistent mode still does not expose lower-level GPU upload or OS page-cache metrics. -> Mitigation: keep these fields out of telemetry until observable.
