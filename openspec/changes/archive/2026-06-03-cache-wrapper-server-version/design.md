## Context

The 2026-06-03 persistent-server benchmark removed the hidden process startup residual. The remaining avoidable wrapper cost is `llama_server_version(self.config.server_bin)`, which shells out once per wrapper request.

On DushyantPC, seven wrapper turns spent about 25 seconds total in `server_version_ms`. This is not SSD cache work and does not need to happen for every request when the wrapper config is stable.

## Goals / Non-Goals

**Goals:**

- Cache server-version identity once per `FlashcacheWrapper` instance.
- Preserve the exact server-version string used for cache-key derivation and telemetry.
- Keep boundary telemetry honest: first lookup records process cost; later requests record the cached path cost under the same phase.
- Make benchmark summaries report `server_version_ms`.

**Non-Goals:**

- No global cross-process version cache.
- No file watcher or automatic invalidation if the llama.cpp binary changes while a wrapper is alive.
- No change to cache-key material.
- No lower-level SSD/KV storage change.

## Decisions

### Cache per wrapper instance

The wrapper stores the server-version string after the first successful lookup.

Rationale: The wrapper config already represents one local llama.cpp setup. Per-instance caching avoids stale global state while removing repeated subprocess cost during an agent session.

Alternative considered: global cache keyed by `server_bin`. Rejected for now because per-instance caching is enough for the benchmark and avoids global invalidation questions.

### Keep `server_version_ms` as the phase name

Repeated requests still execute inside the `server_version_ms` boundary phase, but the work becomes a quick in-memory read.

Rationale: Existing datasets and parsers can compare the same phase before/after the fix.

### Add summary visibility

The summarizer should include `boundary_server_version_ms` for wrapper benchmark results.

Rationale: This was only visible through ad hoc analysis before. It should be part of the standard benchmark table because it can dominate wrapper wall time.

## Risks / Trade-offs

- [Risk] A wrapper instance could continue using an old version string if the binary is replaced while the process stays alive. -> Mitigation: this is acceptable for a single benchmark/session; new wrapper instances refresh the version.
- [Risk] Threaded callers could race on first lookup. -> Mitigation: duplicate first lookups are not harmful for correctness; this wrapper is currently benchmark-oriented and not a production concurrent server.
- [Risk] Summary tables grow wider. -> Mitigation: the added column is directly tied to a measured bottleneck.
