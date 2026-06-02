## Context

Ollama proved a persistence gap: warm aligned prompts were much cheaper than restarted prompts. The research-positioning docs now identify llama.cpp as a close local baseline because it supports prompt cache reuse and server slot save/restore.

The benchmark should test whether llama.cpp already provides the persistence behavior this project needs. If it does, the next prototype should wrap or extend llama.cpp rather than rebuild cache mechanics prematurely. If it does not, we have a sharper reason to inspect lower-level KV persistence.

## Goals / Non-Goals

**Goals:**

- Use llama.cpp server as the first close backend baseline.
- Save and restore a reusable prefix slot cache.
- Compare full-prompt baseline with restored-prefix changed-tail runs.
- Keep model/cache/result artifacts local and ignored.

**Non-Goals:**

- Implement custom llama.cpp internals.
- Benchmark large production models.
- Claim quality equivalence beyond a smoke check and response excerpts.
- Build an OpenAI-compatible wrapper in this change.

## Decisions

- **Use llama.cpp server, not only CLI prompt-cache.** The server exposes slot save/restore endpoints with explicit timing and byte counts.
- **Use a small GGUF model.** The purpose is cache mechanics, not quality. The benchmark keeps model selection configurable.
- **Use the existing fixture parser.** This keeps prompt block ordering and cache-key material consistent with the Ollama benchmark.
- **Start/stop server inside the script.** This lets the benchmark test restored-prefix behavior after a fresh server process.

## Risks / Trade-offs

- **Homebrew package or model download may fail.** -> Mitigation: script accepts explicit binary and model paths, and reports missing prerequisites clearly.
- **Small model timings may not scale linearly.** -> Mitigation: treat this as feasibility and run larger fixtures/models later.
- **Server APIs can change.** -> Mitigation: record llama.cpp version and server command in the result JSON.
