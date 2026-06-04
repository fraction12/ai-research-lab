## ADDED Requirements

### Requirement: Define current local benchmark model
The system SHALL define a current local benchmark/test model for new Ollama-backed experiments.

#### Scenario: Use pinned Gemma 4 Ollama tag
- **WHEN** a new Ollama-backed benchmark, prefix manifest, or local model availability check is prepared
- **THEN** it uses `gemma4:12b` as the default local model tag
- **AND** it records the exact model tag, Ollama version, command line, machine, and model id when available
- **AND** it does not use `gemma4:latest` for new paper-facing benchmark commands

#### Scenario: Preserve backend boundary
- **WHEN** a correctness or cache-control command uses llama.cpp
- **THEN** it uses `ggml-org/gemma-4-12B-it-GGUF:Q4_K_M` as the default Hugging Face GGUF repo unless an experiment explicitly selects another Gemma 4 GGUF path or quantization
- **AND** it does not substitute the Ollama tag `gemma4:12b` into a llama.cpp `--model` argument
- **AND** it records backend version, quantization when known, context size, and exact command line before interpreting results

#### Scenario: Keep historical models separated
- **WHEN** summaries compare new Gemma 4 results with existing `gpt-oss:20b` or `gpt-oss-20b-mxfp4.gguf` evidence
- **THEN** they split results by model and backend
- **AND** they label prior GPT-OSS runs as historical evidence rather than the current default model

#### Scenario: Exclude bad experimental model
- **WHEN** a benchmark model, stronger-model control, or paper-facing comparison point is selected
- **THEN** the experimental vault-mind model is not used
- **AND** any old vault-mind sanity-check artifact is treated as excluded historical context only
