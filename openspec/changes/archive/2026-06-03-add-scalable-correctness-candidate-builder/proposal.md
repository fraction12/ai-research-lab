## Why

The first baseline-pass ladder proved the method but selected only three full-passing cases. To judge Flashcache session-tail quality fairly, we need a repeatable way to build larger candidate sets and give each dataset a scoring-aligned answer hint before running expensive PC benchmarks.

## What Changes

- Add a correctness candidate builder command that creates mixed candidate JSONL files from supported Hugging Face datasets.
- Add dataset-specific answer hints to the JSON answer protocol so generated answers better match each scorer's expected shape.
- Keep sampled candidate prompts in ignored local benchmark input directories while recording only response, score, report, and summary artifacts.
- Document the scalable benchmark loop for baseline-pass parity runs.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `flashcache-correctness-eval-suite`: Add scalable candidate-set construction and dataset-specific answer guidance for fairer baseline-pass ladder runs.

## Impact

- Affects `benchmarks/flashcache_correctness_eval.py`, correctness tests, and benchmark docs.
- Uses the existing optional `datasets` dependency.
- Does not change the Flashcache wrapper API, llama.cpp slot mechanics, or recorded result schema except for additional metadata in generated cases/responses.
