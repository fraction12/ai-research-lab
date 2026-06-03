## Why

Session-tail benchmarks show meaningful prompt-processing savings, but speed is not enough: we need evidence that tail-only completions preserve answer quality versus full-prompt completions. The next benchmark layer should use free, scoreable Hugging Face datasets before we trust session-tail for local agent loops.

## What Changes

- Add a correctness-eval benchmark capability for comparing full-prompt and session-tail outputs.
- Define the first supported datasets: `google/IFEval`, `openai/mrcr`, and `openai/graphwalks`.
- Add dataset registry metadata, sample materialization, prompt-pair records, deterministic scorers, and JSON result reporting.
- Keep downloaded dataset rows and generated eval outputs out of git.
- Document how to run a small local correctness sample before running larger PC benchmarks.

## Capabilities

### New Capabilities
- `flashcache-correctness-eval-suite`: Dataset-backed correctness comparison for full-prompt versus session-tail Flashcache experiments.

### Modified Capabilities
- None.

## Impact

- Affects benchmark tooling, tests, docs, and ignore rules.
- Adds optional Hugging Face dataset loading behavior with a clear error when the `datasets` package is unavailable.
- Does not change the Flashcache wrapper HTTP API or existing latency benchmark result schema.
