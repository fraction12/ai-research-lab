## Why

The current benchmark shows that exact replay can become cheap while changed-tail workflow prompts still pay prompt evaluation cost. The next question is whether a reusable-prefix strategy provides real value when the tail changes.

## What Changes

- Add a benchmark strategy that primes Ollama with the reusable stable prefix, then runs volatile workflow tails using the returned context.
- Add a comparison mode that runs full-prompt baseline and prefix-context strategy against the same fixture and reports deltas.
- Persist strategy-level summaries so repeated runs can compare whether the proxy strategy is faster, slower, or inconclusive.
- Document that Ollama context reuse is a proxy experiment because the API marks `context` as deprecated and it is not SSD-backed KV persistence.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `ollama-workflow-benchmark`: add strategy comparison for full prompt versus prefix-context reuse.

## Impact

- Updates `benchmarks/ollama_workflow_benchmark.py`.
- Updates benchmark documentation and result notes.
- Does not add dependencies.
- Does not implement persistent SSD-backed KV cache.
