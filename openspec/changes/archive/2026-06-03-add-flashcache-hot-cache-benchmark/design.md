## Context

The current Flashcache wrapper benchmark does useful end-to-end measurement, but the first wrapper turn is always a cache miss. That measures cold cache fill plus later hits. The latest server-version-cache run showed the next bottleneck is first-turn prefix priming: about 2.7s at 16 KB, 5.4s at 32 KB, and 11.6s at 64 KB.

For a regular local agent loop, stable instructions, tool schemas, and repo context may already have a persisted slot cache. We need a benchmark shape that measures that steady-state path.

## Goals / Non-Goals

**Goals:**

- Add an explicit benchmark cache mode for hot-cache measurement.
- Keep the current mixed miss-plus-hit behavior unchanged by default.
- Prewarm the exact same namespace, stable prefix, block hashes, model identity, and llama.cpp settings that measured requests will use.
- Store prewarm telemetry separately from measured wrapper runs.
- Make summary output distinguish cold/mixed runs from hot-cache runs.

**Non-Goals:**

- No change to wrapper cache-key semantics.
- No production cache scheduler, daemon, or eviction policy.
- No quality scoring or answer evaluation in this change.
- No claim that hot-cache mode replaces cold-fill measurement.

## Decisions

### Use `--cache-mode cold|hot`

The benchmark gets a cache-mode option. `cold` is the default and preserves the current behavior: the first measured wrapper run is a miss and later runs are hits. `hot` prewarms once, then measures all scenarios as cache-aware requests.

Rationale: `server_mode` already controls process lifecycle. Cache mode should be an orthogonal axis.

### Store prewarm separately

Hot mode writes prewarm data under `wrapper_prewarm` and excludes it from `wrapper_cache_aware`.

Rationale: The measured comparison should show hot-hit turns only. We still keep prewarm telemetry for auditability and debugging.

### Prewarm with the first selected scenario

The first scenario has the same stable prefix and block hashes as the later measured requests. It is enough to create the prefix slot cache, and it avoids inventing a synthetic benchmark-only payload.

Rationale: This keeps prewarm representative while keeping implementation small.

### Measure all selected scenarios after prewarm

Hot mode still runs the full selected scenario set after prewarm. The first measured scenario should be a hit because the prewarm already created the cache.

Rationale: This lets hot-cache results compare cleanly against existing direct full-prompt baselines.

## Risks / Trade-offs

- [Risk] Hot mode can overstate first-session user experience because it excludes cold fill. -> Mitigation: record `cache_mode` and keep cold mode as the default.
- [Risk] Prewarm uses a real scenario tail, which could affect server prompt state in persistent mode. -> Mitigation: the wrapper restores the saved slot before each hit, and direct and wrapper phases already use separate persistent servers.
- [Risk] Existing summaries get wider. -> Mitigation: `cache_mode` is a compact column and is central to interpreting the result.
