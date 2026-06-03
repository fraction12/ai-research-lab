## Context

The `session` cache mode restored a saved prefix slot once into a persistent server, then measured full changed-tail prompts. It produced a perfect session-hit rate but almost no total prompt-eval savings because the first measured full prompt still reprocessed the entire prefix. Later turns were cheap only after that first full prompt had repopulated the in-session prompt cache.

The next question is whether llama.cpp can treat a restored slot as the active prefix state when the benchmark sends only the changed tail.

## Decision

Add a `session-tail` cache mode to `benchmarks/flashcache_wrapper_benchmark.py`.

The mode will share the setup path with `session`:

1. prewarm the selected reusable prefix with the first scenario,
2. start a persistent wrapper server,
3. derive the same cache key,
4. restore the prefix slot once,
5. run all selected scenarios on that server.

The difference is the measured prompt:

- `session` sends the full prompt assembled from stable prefix plus tail.
- `session-tail` sends only `ParsedChatRequest.tail_prompt`.

Measured `session-tail` runs will use cache state `session-tail-hit` and include `prompt_mode: "tail-only"` in run telemetry. This keeps the result distinct from `session-hit` and avoids confusing prompt-token counts with full-prompt runs.

## Risks

- llama.cpp may not interpret a tail-only `/completion` request after slot restore as continuation from the restored prefix; the result may be invalid, flat, or semantically poor.
- Tail-only completions are a benchmark probe, not a complete OpenAI-compatible chat API contract.
- Output quality is not scored in this step; the first metric is prompt processing behavior and whether tail-only mode runs without backend errors.

## Validation

- Unit test cache-mode validation and hit counting for `session-tail`.
- Unit test that session prompt selection uses tail-only prompt text when requested.
- Python compile checks, unit tests, OpenSpec strict validation, benchmark help.
- Local small-model smoke run before any PC ladder run.
