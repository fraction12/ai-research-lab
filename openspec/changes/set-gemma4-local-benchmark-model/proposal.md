## Why

The lab needs a stable current local model target for benchmark and test runs. `gemma4:latest` is too floating for paper-facing evidence, and the previous `gpt-oss-20b` runs should remain historical evidence rather than the default model choice.

## What Changes

- Set `gemma4:12b` as the current Ollama local benchmark/test model.
- Pin Ollama workflow and prefix-block metadata defaults to `gemma4:12b`.
- Set `ggml-org/gemma-4-12B-it-GGUF:Q4_K_M` as the current llama.cpp/HF GGUF target for new correctness and cache-control tests.
- Document the DushyantPC setup contract: Ollama `0.30.4` or newer, `ollama serve` for SSH-run benchmarks when the Windows GUI app does not auto-start, and `ollama pull gemma4:12b`.
- Keep llama.cpp/GGUF controls explicit: use a compatible GGUF/Hugging Face repo path instead of passing an Ollama tag to llama.cpp.
- Explicitly exclude the experimental vault-mind model from benchmark/control use.

## Capabilities

### New Capabilities
- `local-benchmark-model-policy`: Defines the current local model target and backend-specific model selection rules for benchmark and correctness work.

### Modified Capabilities
None.

## Impact

- Updates benchmark CLI defaults for Ollama-backed workflows, prefix-block metadata, and focused llama.cpp mechanism probes.
- Updates Track 01 benchmark docs, Track 02 research docs, and the root handoff.
- Requires no benchmark execution as part of this change; DushyantPC model availability is verified outside the repo through Ollama.
