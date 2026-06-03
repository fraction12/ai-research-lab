## Why

Long local 20B benchmark runs can look frozen for minutes because the scripts only print a final summary. We need lightweight progress output and a repeatable result summarizer so PC/Mac runs are easier to monitor and compare.

## What Changes

- Add phase/scenario progress output to the direct llama.cpp prompt-cache benchmark.
- Add phase/scenario progress output to the Flashcache wrapper benchmark.
- Add a benchmark result summarizer that scans result JSON files and reports model, fixture, timing deltas, ratios, hit rates, and artifact paths.
- Preserve existing benchmark JSON schemas and generated raw result artifacts.

## Capabilities

### New Capabilities
- `benchmark-result-summary`: Summarize benchmark result JSON files into a compact comparison table or text report.

### Modified Capabilities
- `llama-cpp-prompt-cache-benchmark`: Benchmark runs emit progress before long server/model phases.
- `llama-cpp-agent-cache-wrapper`: Wrapper benchmark runs emit progress before direct and cache-aware phases.

## Impact

- Affected code: `benchmarks/llama_cpp_prompt_cache_benchmark.py`, `benchmarks/flashcache_wrapper_benchmark.py`, and a new benchmark summary script.
- Affected tests: benchmark unit tests or new focused tests for summary parsing.
- No new external dependencies, model downloads, public APIs, or persisted cache format changes.
