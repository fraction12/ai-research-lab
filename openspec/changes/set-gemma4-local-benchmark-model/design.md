## Context

Gemma 4 12B is the new current local model target for benchmark and test work. DushyantPC had Ollama `0.24.0`, which rejected `gemma4:12b` with a manifest-version error. Updating to Ollama `0.30.4` allows the pull to start.

The repo has two model surfaces that should not be collapsed:

- Ollama benchmark/test surface: model names such as `gemma4:12b`.
- llama.cpp/GGUF surface: file paths or Hugging Face GGUF repos passed to `llama-server`.

That distinction matters because Track 02 correctness/session controls use llama.cpp slot semantics, while the broader workflow benchmark uses Ollama timing APIs.

## Decisions

### Decision 1: Pin the current Ollama model to `gemma4:12b`

Use `gemma4:12b` instead of `gemma4:latest` for new Ollama benchmark commands, prefix manifests, and local model availability checks.

Rationale: a pinned tag is reproducible enough for internal experiment routing and avoids silent behavior changes from a moving `latest` alias.

### Decision 2: Keep GPT-OSS evidence historical

Existing `gpt-oss:20b` and `gpt-oss-20b-mxfp4.gguf` artifacts remain valid historical evidence. New benchmark docs and runner defaults should not present them as the default local model.

### Decision 3: Pin the current llama.cpp Gemma 4 target

Use `ggml-org/gemma-4-12B-it-GGUF:Q4_K_M` as the current llama.cpp/HF GGUF target for new correctness and cache-control tests. Do not pass the Ollama tag `gemma4:12b` to llama.cpp commands.

Rationale: Track 02 correctness/session controls use llama.cpp slot semantics, so they need a GGUF path or `-hf` repo rather than an Ollama tag. The ggml-org repo gives the repo a concrete Gemma 4 default while preserving exact backend/model metadata in every run.

### Decision 4: Exclude vault-mind permanently

The vault-mind model was an experimental fine-tune with bad output quality. It must not be used as a benchmark model, stronger-model control, or paper-facing comparison point.

## DushyantPC Setup Contract

Expected setup commands:

```powershell
irm https://ollama.com/install.ps1 | iex
ollama serve
ollama pull gemma4:12b
ollama list
```

Notes:

- `ollama serve` is acceptable for SSH-run benchmarks if the Windows tray/GUI app cannot auto-start.
- The local benchmark runner should record `ollama --version`, `ollama list`, model tag, model id, and command line in raw artifacts or summaries.
- `gemma4:12b` is an Ollama model tag. llama.cpp controls should use `--hf-repo ggml-org/gemma-4-12B-it-GGUF:Q4_K_M` or an explicit downloaded Gemma 4 GGUF path.

## Risks / Trade-offs

- `gemma4:12b` may improve quality while changing timing, so historical `gpt-oss` results must not be blended with new Gemma 4 results without model splits.
- Ollama and llama.cpp may use different quantization/runtime paths for nominally similar Gemma models, so backend identity must remain part of cache keys and reports.
- Pulling the model can be slow and machine-local. The repo should document commands, not commit model files.
