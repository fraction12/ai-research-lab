# Printtestbot Printing Press Benchmark Dataset

Date: 2026-06-02

Machine: DushyantPC

Fixture: `benchmarks/fixtures/printtestbot_printing_press_workflow.json`

## Purpose

This dataset tests a Printy/printtestbot-style long agent workflow with a stable reusable prefix and changing command-output tails. It is meant to answer whether local-agent prompts can preserve useful prefix/KV work across changed-tail turns and restarts.

The fixture is sanitized and hand-curated. It is not a raw Telegram transcript and contains no secrets, tokens, private chat IDs, private keys, or personal context.

## Raw Results

- `raw/ollama-full-gpt-oss-20b.json`: full prompt every changed-tail turn.
- `raw/ollama-exact-repeat-gpt-oss-20b.json`: exact repeated prompt control for one scenario.
- `raw/ollama-prefix-context-compare-gpt-oss-20b.json`: full prompt versus Ollama `context` proxy.
- `raw/ollama-restart-compare-gpt-oss-20b.json`: warm sequence versus stopping the model before each turn.
- `raw/prefix-manifest-gpt-oss-20b.json`: reusable prefix block manifest and cache-key material.
- `raw/llama-cpp-slot-cache-gemma-3-270m-it-q8.json`: llama.cpp slot save/restore result.
- `raw/flashcache-wrapper-gemma-3-270m-it-q8.json`: Flashcache wrapper versus direct llama.cpp result.
- `raw/20260602T215635Z-gpt-oss-20b-mxfp4-printtestbot_printing_press_workflow-llama-cpp-prompt-cache.json`: one-scenario `gpt-oss-20b` slot save/restore smoke.
- `raw/20260602T220157Z-gpt-oss-20b-mxfp4-printtestbot_printing_press_workflow-llama-cpp-prompt-cache.json`: full seven-turn `gpt-oss-20b` slot save/restore result.
- `raw/20260602T220711Z-gpt-oss-20b-mxfp4-printtestbot_printing_press_workflow-flashcache-wrapper.json`: full seven-turn `gpt-oss-20b` Flashcache wrapper versus direct llama.cpp result.
- `raw/20260603T001246Z-gpt-oss-20b-printtestbot_printing_press_workflow.json`: normal Ollama `gpt-oss:20b` no-custom-cache timing simulation, 3 runs per scenario, 64 generated tokens.
- `raw/20260603T001326Z-gpt-5.5-printtestbot-printing-press-workflow-codex-frontier.json`: Codex `gpt-5.5` frontier simulation, 2 runs per scenario.
- `raw/20260603T001826Z-gpt-oss-20b-printtestbot_printing_press_workflow.json`: normal Ollama `gpt-oss:20b` no-custom-cache quality-cap probe, 1 run per scenario, 256 generated tokens.
- `raw/20260603T002322Z-gpt-oss-20b-printtestbot_printing_press_workflow.json`: normal Ollama `gpt-oss:20b` no-custom-cache `think=false` probe, 2 runs per scenario, 128 generated tokens.

## Environment

Ollama model:

```text
gpt-oss:20b
```

llama.cpp:

```text
version: 9469 (d178a1181)
built with Clang 19.1.5 for Windows x86_64
```

This winget build cannot load `gpt-oss` GGUF files. The `gpt-oss-20b` GGUF follow-up used portable llama.cpp:

```text
version: 9482 (4fb16eccc)
built with Clang 19.1.5 for Windows x86_64
```

GGUF cache-mechanics model:

```text
gemma-3-270m-it-Q8_0.gguf
291,545,600 bytes
```

OpenAI OSS GGUF follow-up model:

```text
gpt-oss-20b-mxfp4.gguf
12,109,566,560 bytes
```

## Headline Results

Ollama warm versus restarted on `gpt-oss:20b`:

```text
warm prompt eval sum:      4,428.6 ms
restarted prompt eval sum: 10,456.5 ms
restarted minus warm:       6,027.9 ms
```

llama.cpp slot save/restore on Gemma 270M Q8:

```text
baseline prompt ms sum: 466.950 ms
restored prompt ms sum: 216.115 ms
delta:                  250.835 ms
slot cache file:         19,567,436 bytes
```

Flashcache wrapper on Gemma 270M Q8:

```text
direct prompt ms sum:  484.884 ms
wrapper prompt ms sum: 192.692 ms
delta:                 292.192 ms
cache hit rate:          0.8571428571
```

llama.cpp slot save/restore on `gpt-oss-20b-mxfp4.gguf`:

```text
baseline prompt ms sum: 8,412.695 ms
restored prompt ms sum: 8,442.375 ms
delta:                  -29.680 ms
slot cache file:         31,108,988 bytes
```

Flashcache wrapper on `gpt-oss-20b-mxfp4.gguf`:

```text
direct prompt ms sum:  8,452.938 ms
wrapper prompt ms sum: 7,374.758 ms
delta:                 1,078.180 ms
cache hit rate:          0.8571428571
```

Codex `gpt-5.5` frontier simulation:

```text
runs:                     14
mean wall time:            13,680.5 ms
mean input tokens:         15,087.9
mean cached input tokens:   3,090.3
mean uncached input tokens: 11,997.6
mean output tokens:           588.6
mean reasoning tokens:         475.9
```

Normal Ollama `gpt-oss:20b` no-custom-cache simulation, 64 generated tokens:

```text
runs:                       21
mean wall time:              7,650.9 ms
mean prompt tokens:          1,360.7
mean generated tokens:          64.0
mean prompt eval:              471.4 ms
non-empty final responses:        0 / 21
```

Normal Ollama `gpt-oss:20b` no-custom-cache probe with `think=false`, 128 generated tokens:

```text
runs:                       14
mean wall time:             16,071.8 ms
mean prompt tokens:          1,335.7
mean generated tokens:         128.0
mean prompt eval:            1,016.9 ms
non-empty final responses:        0 / 14
non-empty thinking fields:       14 / 14
```

## Interpretation

The useful signal is not exact replay. The exact repeat control drops prompt eval sharply, but that is not the product workload.

The real signal is the restarted comparison: DushyantPC gets warm-session-like prompt eval on changed-tail turns while the model stays loaded, then loses that advantage when `gpt-oss:20b` is stopped before every turn. That creates a concrete target for persistent prefix/KV state.

The llama.cpp and Flashcache runs show the same cache boundary can reduce prompt processing on a small GGUF model. Those runs prove cache mechanics, not large-model answer quality.

The `gpt-oss-20b` follow-up is mixed. Direct slot restore is flat to slightly worse on the full seven-turn fixture, while the Flashcache wrapper still reduces prompt processing by about 12.8%. That means the useful path is not "slot restore always wins"; it is wrapper-level prompt layout and cache policy, with larger-prefix tests needed before claiming a large-model persistence win.

The frontier-versus-local simulation says local Ollama is materially more prompt-token efficient for this fixture, but the current `gpt-oss:20b` route is not yet an adequate Print-A-Bot replacement for Codex. Codex `gpt-5.5` used about 11.1x more reported input tokens per turn than Ollama reported prompt tokens, or about 8.8x more when only uncached Codex input is counted. That reflects Codex runtime overhead plus different tokenizers, so treat it as a workload-level comparison rather than a tokenizer-pure number.

Cost effectiveness depends on the definition of cost. Codex CLI reports token usage but not a per-run dollar charge, so the dataset does not claim exact Codex dollars. For bulk simulations on owned hardware, local Ollama has no marginal API bill and far lower prompt-token accounting. For useful Print-A-Bot replies today, the current local route often fails because Ollama returns thinking-channel content without final `response` text; Print-A-Bot's current local runner reads only `response`, so those runs would fall back to Codex.

## Caveats

- Ollama `context` is a deprecated API proxy and was slower than aligned full prompts on this fixture.
- The llama.cpp/Flashcache tests use a small model because they test slot save/restore mechanics.
- Direct `gpt-oss-20b` slot restore was tested later and did not beat direct full prompts on this fixture.
- Generation was capped at 8 tokens to keep prompt evaluation dominant.
- Later local/frontier comparisons used larger caps, but they are still task simulations, not a scored answer-quality benchmark.
- Codex `gpt-5.5` usage is Codex agent-runtime usage, not raw OpenAI API usage.
- The current Print-A-Bot local Ollama path streams the `response` field; it does not consume the `thinking` field observed in the `gpt-oss:20b` probe.
- Output quality was not scored beyond response excerpts. A later benchmark should add a quality rubric with larger `n_predict`.
