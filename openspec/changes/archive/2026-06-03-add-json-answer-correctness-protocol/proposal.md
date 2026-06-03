## Why

The first correctness smoke proved the response pipeline works, but raw `/completion` produced reasoning and partial text that the scorers could not fairly judge. llama.cpp's current server docs support schema-constrained JSON output on `/completion`, which fits our slot save/restore path better than switching the runner to chat completions.

## What Changes

- Add an answer protocol option for the correctness runner.
- Support a `json-answer` protocol that wraps prompts with final-answer instructions.
- Send a llama.cpp `json_schema` constraint so `/completion` emits `{"answer": "..."}`.
- Extract `answer` into the response field used by scorers while preserving raw model output for debugging.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `flashcache-correctness-eval-suite`: Add constrained final-answer generation for correctness response runs.

## Impact

- Affects the correctness runner, llama.cpp client helper, benchmark docs, and tests.
- Does not change the Flashcache HTTP wrapper or latency benchmark schema.
