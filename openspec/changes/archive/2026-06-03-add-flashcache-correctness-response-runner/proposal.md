## Why

The correctness suite can now build cases and score responses, but it still needs a runner that actually produces comparable `full` and `session-tail` model outputs. Without that bridge, we cannot answer whether the faster tail-only path preserves output quality.

## What Changes

- Add a correctness response runner that reads case JSONL and writes response JSONL.
- Support `full`, `session-tail`, and `both` modes.
- Run full-prompt completions from `full_prompt`.
- Run session-tail completions by priming/restoring `stable_prefix` into a llama.cpp slot, then completing only `tail_prompt`.
- Record response text, latency, timing metadata, prompt hashes, and session setup telemetry.
- Optionally score responses immediately after generation using the existing correctness scorer.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `flashcache-correctness-eval-suite`: Add model response generation for full-prompt and session-tail correctness comparisons.

## Impact

- Affects `benchmarks/flashcache_correctness_eval.py`, benchmark docs, and tests.
- Uses existing llama.cpp process/client helpers and the existing ignored correctness output directories.
- Does not change the Flashcache wrapper HTTP API or the prior latency benchmark schema.
