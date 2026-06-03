## Context

Flashcache wraps llama.cpp slot save/restore and already returns coarse cache telemetry such as cache state, cache key, prompt timing, save timing, restore timing, and fallback reason. The latest benchmark direction asks a sharper question: not just whether caching helped, but where the time went across the cache boundary.

The current wrapper can measure phases it controls: request parsing, prompt assembly, cache key derivation, manifest lookup, prefix priming, slot save, slot restore, tail/direct completion, and total wrapper wall time. It cannot yet measure lower-level internals such as tensor serialization, SSD read throughput, GPU upload, or llama.cpp scheduler costs without backend changes.

## Goals / Non-Goals

**Goals:**

- Add `boundary_timings` telemetry for wrapper-visible cache phases.
- Persist those timings in Flashcache wrapper benchmark results.
- Summarize boundary totals from result JSONs so large-prefix runs can be compared quickly.
- Preserve existing response compatibility and avoid changing model prompts, cache keys, or cache behavior.

**Non-Goals:**

- No custom KV cache format.
- No llama.cpp patching.
- No claim that wrapper timings fully explain SSD, GPU upload, or serialization costs.
- No raw volatile prompt persistence beyond current debug behavior.

## Decisions

### Use monotonic wrapper timers

Record phase durations with `time.perf_counter()` around wrapper-controlled calls.

Rationale: the wrapper can reliably measure its own wall-clock phase costs without adding dependencies or changing llama.cpp. These timings are enough to reveal whether wrapper overhead, save/restore calls, or completion calls dominate the current benchmark.

Alternative considered: parse llama.cpp server logs for deeper timing. Rejected for this change because logs are backend-version-sensitive and harder to test deterministically.

### Make boundary telemetry optional and additive

Return boundary timings in the existing debug object and benchmark JSON, but do not add required response headers for every field.

Rationale: the API stays compatible while debug consumers get machine-readable details. Existing clients and tests that only inspect cache state or prompt timing continue to work.

Alternative considered: add one HTTP header per phase. Rejected because the phase list will evolve and JSON is a better fit for structured telemetry.

### Separate measured phases from unavailable phases

Represent unavailable lower-level fields as absent or `null`, not estimated.

Rationale: this repo values evidence over claims. If the wrapper cannot see SSD read throughput or GPU upload time yet, telemetry should not invent those numbers.

Alternative considered: infer disk throughput from slot file size and restore duration. Rejected for the first version because restore duration includes more than disk reads.

### Summarize only stable comparison fields

Expose compact totals in `benchmarks/summarize_results.py`, especially direct total wall time, wrapper total wall time, save time, restore time, and tail/direct completion time where available.

Rationale: the summary table should answer "where is the obvious cost?" without becoming a full trace viewer.

Alternative considered: print every phase from every request. Rejected because it would make the normal summary too noisy.

## Risks / Trade-offs

- [Risk] Boundary timings are wall-clock and include backend/network/process scheduling noise. -> Mitigation: label them as wrapper-visible timings and keep raw JSON for deeper inspection.
- [Risk] The phase vocabulary may change as the backend gets closer to metal. -> Mitigation: keep telemetry additive and tolerate missing optional fields in summaries.
- [Risk] Extra timing code could clutter wrapper logic. -> Mitigation: centralize timing helpers and keep phase names simple.
- [Risk] Benchmarks may overfocus on prompt timing while output quality remains unscored. -> Mitigation: keep this change scoped to timing and leave quality/routing rubric for a later change.

## Migration Plan

No migration is required. Existing cache manifests and result JSONs remain readable. Older result files simply show `n/a` for boundary summary fields.

Rollback is removing the additive telemetry fields and summary columns; cache behavior is unchanged.

## Open Questions

- Which lower-level fields should become first-class once llama.cpp or a custom backend exposes them: SSD read/write bytes, mmap page faults, GPU upload time, or tokenization time?
- Should later result summaries support a verbose mode that prints per-phase distributions instead of only aggregate totals?
