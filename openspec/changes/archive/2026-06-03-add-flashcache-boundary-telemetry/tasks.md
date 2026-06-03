## 1. Telemetry Model

- [x] 1.1 Add a small wrapper-visible boundary timing helper.
- [x] 1.2 Add boundary timing fields to Flashcache response telemetry and debug output.

## 2. Wrapper Instrumentation

- [x] 2.1 Instrument direct, cache-bypass completions.
- [x] 2.2 Instrument cache miss phases: prompt assembly/keying, cache lookup, prefix prime, slot save, tail completion, and total wrapper time.
- [x] 2.3 Instrument cache hit phases: prompt assembly/keying, cache lookup, slot restore, tail completion, and total wrapper time.
- [x] 2.4 Preserve existing cache behavior, response fields, and headers.

## 3. Benchmark and Summary

- [x] 3.1 Persist boundary timing telemetry in Flashcache wrapper benchmark result JSON.
- [x] 3.2 Extend benchmark summary rows and output columns for boundary timing totals.

## 4. Verification

- [x] 4.1 Add or update unit tests for debug telemetry shape and headers compatibility.
- [x] 4.2 Add or update unit tests for benchmark summary parsing with boundary fields and missing optional values.
- [x] 4.3 Run focused unit tests and `openspec validate --all --strict`.
