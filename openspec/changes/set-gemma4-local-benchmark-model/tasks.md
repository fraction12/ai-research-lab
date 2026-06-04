## 1. OpenSpec

- [x] 1.1 Create proposal, design, tasks, and spec delta for the local model policy.
- [x] 1.2 Validate the OpenSpec change with `openspec validate --all --strict`.

## 2. Implementation

- [x] 2.1 Pin Ollama workflow benchmark default model to `gemma4:12b`.
- [x] 2.2 Pin prefix-block metadata default model to `gemma4:12b`.
- [x] 2.3 Pin focused llama.cpp mechanism-probe defaults to `ggml-org/gemma-4-12B-it-GGUF:Q4_K_M`.
- [x] 2.4 Update benchmark docs, Track 02 docs, active GraphWalks command shapes, and the agent handoff.

## 3. DushyantPC Setup

- [x] 3.1 Update Ollama to a version that accepts `gemma4:12b`.
- [x] 3.2 Pull `gemma4:12b` on DushyantPC and verify it appears in `ollama list`.

## 4. Validation

- [x] 4.1 Run relevant unit tests for the touched benchmark defaults.
- [x] 4.2 Record any DushyantPC startup caveat needed for SSH-run benchmarks.
