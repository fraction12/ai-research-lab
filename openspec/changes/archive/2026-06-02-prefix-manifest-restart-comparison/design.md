## Context

The current benchmark shows that prompt layout matters: stable blocks should stay aligned at the beginning of the prompt. It also shows that the public Ollama `context` proxy does not currently beat full aligned prompts. The unanswered question is whether the speedup is only in-session reuse inside a warm Ollama model.

If stopping Ollama before each changed-tail prompt removes the benefit, this creates a concrete persistence gap. That gap is the target for an SSD-backed prefix/KV cache: preserve reusable state across sessions instead of recomputing the stable prefix.

## Goals / Non-Goals

**Goals:**

- Produce a prefix manifest that future cache code can use as cache-key material.
- Measure warm sequence versus restarted sequence with the same fixture and model.
- Record restart actions and timing.
- Keep the implementation dependency-free.

**Non-Goals:**

- Persist real KV tensors.
- Prove SSD-backed reuse yet.
- Manage Ollama server lifecycle beyond `ollama stop <model>`.
- Compare model output quality beyond short response excerpts.

## Decisions

- **Add `restart-compare` as a strategy.** It keeps the CLI mental model consistent with `full`, `prefix-context`, and `compare`.
- **Use full aligned prompts for restart comparison.** This isolates whether Ollama's in-session aligned-prefix reuse survives restarts.
- **Stop the selected model, not the Ollama server.** `ollama stop <model>` unloads the model without killing the API server.
- **Write prefix manifests separately only when requested.** Result JSON will include the manifest, while `--write-prefix-manifest` creates a dedicated artifact for future cache work.

## Risks / Trade-offs

- **Ollama may preserve some state despite `ollama stop`.** -> Mitigation: record stop commands and load durations so the result can be interpreted cautiously.
- **Restart comparison adds time.** -> Mitigation: keep generated tokens low and scenario count configurable.
- **Manifest is metadata only.** -> Mitigation: label it as Phase 1 scaffolding, not real KV persistence.
