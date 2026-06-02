## Why

The SSD-native inference thesis needs local measurements before cache architecture decisions can be trusted. A repeated Codex-style DeepClean workflow is a practical first workload because it has a large stable agent prefix and a small volatile tail.

## What Changes

- Add a local benchmark harness that sends repeated workflow prompts to Ollama and records prompt evaluation timing.
- Add a realistic synthetic Codex/DeepClean workflow fixture with stable, semi-stable, and volatile prompt blocks.
- Add report output that separates model load time, prompt evaluation time, generation time, prompt token count, and derived throughput.
- Document how to run the benchmark and how to interpret the result as a baseline for future prefix/KV cache work.

## Capabilities

### New Capabilities

- `ollama-workflow-benchmark`: Measures local Ollama prompt evaluation cost for repeated agent workflow prompts.

### Modified Capabilities

None.

## Impact

- Adds benchmark code and fixtures under `benchmarks/`.
- Updates research references with the Ollama API timing source.
- Does not add runtime dependencies beyond Python standard library and a local Ollama server.
- Does not implement SSD-backed prefix or KV cache yet.
