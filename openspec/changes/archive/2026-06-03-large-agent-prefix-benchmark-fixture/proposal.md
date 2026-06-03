## Why

The current Printy fixture has only about 5.5 KB of reusable prefix, yet the Flashcache wrapper already repeats roughly 11-13% prompt-processing savings on DushyantPC. We need larger, realistic agent-prefix fixtures to test whether cache value grows toward the real local-agent workload: long-lived instructions, tools, repo context, memory, and repeated changed-tail turns.

## What Changes

- Add a deterministic large-prefix fixture generator that scales a sanitized Printy-style workflow to target reusable-prefix byte sizes.
- Add fixture safety checks for stable/volatile boundaries, prefix size, context budget, and common secret patterns.
- Generate a small ladder of benchmark fixtures for target prefix sizes such as 16 KB, 32 KB, and 64 KB.
- Add documentation for the DushyantPC benchmark ladder and result interpretation.
- Keep generated model/cache/log artifacts local while allowing curated fixture JSON and raw result JSON to be committed as evidence.

## Capabilities

### New Capabilities
- `large-agent-prefix-benchmark-fixture`: Generate sanitized, size-targeted agent workflow fixtures for testing reusable-prefix cache value.

### Modified Capabilities

## Impact

- Affected code: new benchmark fixture generator and focused tests.
- Affected artifacts: generated fixture JSON files under `benchmarks/fixtures/` and dataset notes for large-prefix runs.
- Affected systems: DushyantPC benchmark working tree for large `gpt-oss-20b-mxfp4` runs.
- No new dependencies, production behavior changes, model downloads, or cache format changes.
