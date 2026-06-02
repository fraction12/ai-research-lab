## Context

This repo is currently a research and prototype workspace. The first concrete experiment should measure the cost of repeatedly processing a large agent workflow prompt before attempting SSD-backed prefix or KV persistence.

Ollama's non-streaming `/api/generate` endpoint returns usage metrics including prompt token count and prompt evaluation duration. Those metrics are enough to establish a baseline for the "size of the prize": how much local time is spent on stable prompt context in repeated Codex-style workflows.

## Goals / Non-Goals

**Goals:**

- Provide a small local CLI benchmark with no third-party Python dependencies.
- Model a repeated Codex/DeepClean workflow as named prompt blocks.
- Record Ollama prompt evaluation metrics and write JSON artifacts.
- Make the output useful for future prefix cache and KV cache design.

**Non-Goals:**

- Implement persistent KV cache reuse.
- Compare against frontier model internals that are not observable from Codex.
- Automate DeepClean, GitHub, CI, or PR actions.
- Benchmark output quality deeply; this first harness limits generation to keep runs cheap.

## Decisions

- **Use Python standard library.** This keeps the harness runnable in a sparse research repo without package setup.
- **Use Ollama `/api/generate` with `stream: false`.** Non-streaming responses return all relevant usage metrics in one JSON object.
- **Use a JSON fixture.** A fixture makes prompt block boundaries explicit and gives future cache manifest code something to evolve from.
- **Benchmark prompt cost with short completions.** The harness should use a small `num_predict` value by default so prompt evaluation dominates the measurement.
- **Persist results under `benchmarks/results/`.** JSON results allow later comparison across models, fixture revisions, and cache implementations.

## Risks / Trade-offs

- **Ollama may internally reuse loaded model state across runs.** Mitigation: report load duration separately and focus on prompt evaluation metrics.
- **A synthetic fixture may not match a real Codex transcript.** Mitigation: make the fixture path configurable and preserve block hashes so a real fixture can be swapped in.
- **Prompt eval metrics do not prove SSD cache speedup.** Mitigation: document this benchmark as a baseline only.
- **Model-specific timing can vary heavily.** Mitigation: include model name, options, and fixture hash in each result.

## Migration Plan

No migration is required. The change adds standalone benchmark files.

## Open Questions

- Which real Codex/DeepClean transcript should replace the synthetic fixture later?
- Should the next benchmark use MLX or llama.cpp once this baseline is stable?
