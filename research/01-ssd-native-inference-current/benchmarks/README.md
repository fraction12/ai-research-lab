# Ollama Workflow Benchmark

This benchmark measures local prompt evaluation cost for repeated agent workflows. It is a baseline for future prefix-cache and KV-cache work; it does not implement SSD-backed KV reuse yet.

For the current system-level interpretation of the Flashcache/SSD-backed local-agent approach, see [Flashcache System Report](../docs/flashcache-system-report.md).

## Run

```bash
python3 benchmarks/ollama_workflow_benchmark.py --model gemma4:latest --runs 1 --num-predict 16
```

Compare full-prompt baseline against the Ollama context proxy:

```bash
python3 benchmarks/ollama_workflow_benchmark.py \
  --strategy compare \
  --fixture benchmarks/fixtures/lightningitb_deepclean_campaign.json \
  --model gemma4:latest \
  --runs 1 \
  --num-predict 8 \
  --prime-num-predict 1 \
  --temperature 0
```

Use `--vary-runs` when `--runs` is greater than 1 and you want repeated samples to avoid exact prompt replay.

Compare warm in-session reuse against restarting the model before each prompt:

```bash
python3 benchmarks/ollama_workflow_benchmark.py \
  --strategy restart-compare \
  --fixture benchmarks/fixtures/lightningitb_deepclean_campaign.json \
  --model gemma4:latest \
  --runs 1 \
  --num-predict 8 \
  --temperature 0 \
  --write-prefix-manifest
```

Use `--dry-run` to verify prompt assembly without calling Ollama:

```bash
python3 benchmarks/ollama_workflow_benchmark.py --dry-run
```

Results are written to `benchmarks/results/*.json`.

Prefix manifests are written to `benchmarks/prefix-manifests/*.json` when `--write-prefix-manifest` is set.

Build a metadata-only prefix block store:

```bash
python3 benchmarks/prefix_block_store.py \
  --fixture benchmarks/fixtures/lightningitb_deepclean_campaign.json \
  --model gemma4:latest
```

Prefix store artifacts are written to `benchmarks/prefix-store/`.

Run the llama.cpp prompt-cache feasibility benchmark:

```bash
python3 benchmarks/llama_cpp_prompt_cache_benchmark.py \
  --model benchmarks/models/gemma-3-270m-it-Q8_0.gguf \
  --fixture benchmarks/fixtures/lightningitb_deepclean_campaign.json \
  --predict 8 \
  --temperature 0
```

This starts `llama-server`, primes the reusable prefix, saves the slot cache, restarts for cold full-prompt baselines, then restarts again and restores the saved slot before changed-tail prompts.

Use `--hf-repo` with a current llama.cpp build when the model should be pulled by llama.cpp instead of supplied as a local GGUF path:

```bash
python3 benchmarks/llama_cpp_prompt_cache_benchmark.py \
  --server-bin /path/to/llama-server \
  --hf-repo ggml-org/gpt-oss-20b-GGUF \
  --fixture benchmarks/fixtures/printtestbot_printing_press_workflow.json \
  --predict 8 \
  --temperature 0
```

llama.cpp artifacts are written under `benchmarks/llama-cpp-*` and ignored.

Run the Flashcache wrapper service:

```bash
python3 -m flashcache.cli \
  --model benchmarks/models/gemma-3-270m-it-Q8_0.gguf \
  serve \
  --port 8099
```

Send a cache-aware local chat request:

```bash
curl http://127.0.0.1:8099/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "local-gemma",
    "messages": [{"role": "user", "content": "Changed tail for this agent turn"}],
    "max_tokens": 8,
    "temperature": 0,
    "ssd_cache": {
      "namespace": "demo-agent-workflow",
      "stable_prefix_text": "Reusable agent instructions and tool schema go here.",
      "debug": true
    }
  }'
```

The response includes `X-Flashcache-*` headers. With `debug: true`, the response body also includes a `flashcache` object with cache state, prompt timing, slot save/restore timing, and fallback reason when applicable.

Compare direct llama.cpp calls against the Flashcache wrapper:

```bash
python3 benchmarks/flashcache_wrapper_benchmark.py \
  --model benchmarks/models/gemma-3-270m-it-Q8_0.gguf \
  --fixture benchmarks/fixtures/lightningitb_deepclean_campaign.json \
  --predict 8 \
  --temperature 0
```

Use `--cache-mode hot` to prewarm the prefix before measured turns, `--cache-mode session --server-mode persistent` to restore the prefix once and replay full prompts, or `--cache-mode session-tail --server-mode persistent` to restore the prefix once and measure tail-only turns.

Flashcache wrapper artifacts are written under `benchmarks/flashcache/` and `benchmarks/flashcache-results/`, both ignored.

Prepare and score correctness eval cases:

```bash
python3 benchmarks/flashcache_correctness_eval.py list-datasets

python3 benchmarks/flashcache_correctness_eval.py sample \
  --dataset ifeval \
  --limit 8 \
  --output-dir benchmarks/correctness-eval-inputs

python3 benchmarks/flashcache_correctness_eval.py score \
  --cases benchmarks/correctness-eval-inputs/ifeval-sample-8.jsonl \
  --responses benchmarks/correctness-eval-results/ifeval-responses.jsonl
```

The first correctness datasets are `google/IFEval`, `openai/mrcr`, and `openai/graphwalks`. Sampled case files contain `stable_prefix`, `tail_prompt`, and derived `full_prompt` fields so the same case can be run through full-prompt and session-tail modes. Generated correctness inputs/results are local artifacts and ignored.

Response JSONL records should use `{"case_id": "...", "mode": "full" | "session-tail", "response": "...", "latency_ms": 123.4}`. The scorer reports per-mode scores and `session_tail_minus_full_score` for matching case ids.

Build a larger mixed candidate file for a baseline-pass ladder:

```bash
python3 benchmarks/flashcache_correctness_eval.py build-candidates \
  --mix ifeval:80,graphwalks:20 \
  --profile easy \
  --max-prompt-chars 5000 \
  --output benchmarks/correctness-eval-inputs/easy-mixed-candidates-100.jsonl
```

`--profile easy` currently filters IFEval to single supported checks with bounded parameters. It leaves GraphWalks and MRCR unfiltered except for prompt-length and offset options. Candidate JSONL files contain prompt text, so keep them under `benchmarks/correctness-eval-inputs/` or another ignored path.

Generate model responses for a sampled case file:

```bash
python3 benchmarks/flashcache_correctness_eval.py run \
  --cases benchmarks/correctness-eval-inputs/ifeval-sample-8.jsonl \
  --mode both \
  --answer-protocol json-answer \
  --server-bin /path/to/llama-server \
  --model benchmarks/models/gemma-3-270m-it-Q8_0.gguf \
  --ctx-size 4096 \
  --predict 64 \
  --temperature 0 \
  --score
```

`full` mode sends each case's `full_prompt`. `session-tail` mode primes a llama.cpp slot with `stable_prefix`, saves/restores that slot, then sends only `tail_prompt`. Use `--dry-run` to validate response JSONL shape without starting llama.cpp.

`--answer-protocol json-answer` wraps the prompt with final-answer instructions and sends a llama.cpp `/completion` `json_schema` requiring `{"answer": "..."}`. The scorer reads the extracted `answer` while the response JSONL keeps `raw_response` for debugging. This keeps the experiment on the same raw slot save/restore path while avoiding free-form reasoning text in scorer inputs.

The JSON answer protocol also includes a dataset-specific hint for the answer string shape. For example, GraphWalks asks for a JSON-style node list in the `answer` string, while MRCR asks for the exact requested text. Raw protocol runs do not add these hints.

Run the baseline-pass ladder:

```bash
python3 benchmarks/flashcache_correctness_eval.py baseline-ladder \
  --cases benchmarks/correctness-eval-inputs/mixed-quality-smoke-3.jsonl \
  --answer-protocol json-answer \
  --server-bin /path/to/llama-server \
  --model benchmarks/models/gemma-3-270m-it-Q8_0.gguf \
  --ctx-size 32768 \
  --predict 128 \
  --temperature 0 \
  --min-full-score 1.0
```

The ladder writes full baseline responses/scores first, selects only cases where full mode meets `--min-full-score`, then runs session-tail on that selected set. If zero cases pass full mode, the report is still useful: it says the model/prompt protocol is not ready for parity testing yet.

## Fixtures

- `codex_deepclean_workflow.json`: small synthetic Codex/DeepClean workflow used as the first controlled baseline.
- `lightningitb_deepclean_campaign.json`: sanitized real workflow prompt distilled from the LightningITB DeepClean P1/P2 campaign archive. The fixture records source artifact paths and notes that the raw chat transcript is not stored verbatim.
- `printtestbot_printing_press_workflow.json`: sanitized Printy/printtestbot-style Printing Press CLI workflow with stable bot/runtime/tool rules and seven changed command-output tails.
- `printtestbot-printing-press-workflow-large-prefix-16kb.json`, `32kb.json`, and `64kb.json`: generated large-prefix variants for testing whether Flashcache value scales as reusable agent context grows.

## Recorded Datasets

- `benchmarks/datasets/printtestbot-printing-press-2026-06-02/`: DushyantPC runs for the Printy fixture, including raw Ollama, llama.cpp slot-cache, and Flashcache wrapper result JSON.
  - Includes `gpt-oss:20b` Ollama baseline data plus official `gpt-oss-20b-mxfp4.gguf` llama.cpp/Flashcache follow-up data.
- `benchmarks/datasets/printtestbot-large-prefix-2026-06-02/`: DushyantPC runs for generated larger-prefix Printy fixtures.
- `benchmarks/datasets/printtestbot-hot-cache-2026-06-03/`: DushyantPC hot-cache large-prefix runs where measured turns restore the prefix slot before every changed-tail prompt.
- `benchmarks/datasets/printtestbot-session-cache-2026-06-03/`: DushyantPC session-cache large-prefix runs where the prefix slot is restored once into a persistent server before measured turns.
- `benchmarks/datasets/printtestbot-session-tail-2026-06-03/`: DushyantPC session-tail large-prefix runs where the prefix slot is restored once and measured turns send only changed-tail prompt text.
- `benchmarks/datasets/flashcache-correctness-smoke-2026-06-03/`: DushyantPC GPT-OSS 20B paired full/session-tail correctness smoke across IFEval, GraphWalks, and MRCR.
- `benchmarks/datasets/flashcache-baseline-pass-ladder-2026-06-03/`: DushyantPC GPT-OSS 20B baseline-pass ladder where full-passing IFEval cases were rechecked with session-tail.
- `benchmarks/datasets/flashcache-correctness-parity-2026-06-03/`: DushyantPC GPT-OSS 20B baseline-pass ladder with 42 full-passing selected cases across IFEval and GraphWalks; session-tail passed 31/42 overall.

## What To Look At

- `prompt_eval_duration`: local time spent evaluating the input prompt.
- `prompt_eval_count`: prompt tokens processed by Ollama.
- `load_duration`: model loading time, which should be considered separately from prompt cost.
- `reusable_prefix_bytes`: stable or semi-stable prompt bytes that would be candidates for future prefix/KV caching.
- `comparison.baseline_minus_prefix_context_prompt_eval_duration`: positive means the context proxy reduced prompt eval; negative means it was slower.
- `restart_comparison.restarted_minus_warm_prompt_eval_duration`: positive means model restarts removed warm-prefix benefit and created a persistence gap.
- `prefix_manifest.cache_key_sha256`: metadata-only cache key scaffold for future prefix/KV cache work.
- `comparison.baseline_minus_restored_prompt_ms`: positive means llama.cpp slot restore reduced prompt processing time versus fresh full-prompt baselines.
- `comparison.direct_minus_wrapper_prompt_ms`: positive means the Flashcache wrapper reduced prompt processing time versus direct full-prompt llama.cpp calls.

Generate large-prefix fixture variants:

```bash
python3 benchmarks/generate_large_prefix_fixtures.py
```

The generator uses only allowlisted repo-local context, checks common secret patterns, preserves the original volatile tails, and records context-size guidance in fixture metadata.

## Strategy Modes

- `full`: send the full scenario prompt every time.
- `prefix-context`: prime Ollama once with the common stable/semi-stable prefix, then send each changed tail with Ollama's returned `context`.
- `compare`: run both strategies and report the delta.
- `restart-compare`: run aligned full prompts in a warm sequence, then stop the Ollama model before each prompt and compare the prompt evaluation cost.

The `prefix-context` strategy is a proxy experiment. Ollama's generate API documents `context` as conversational memory and marks it deprecated, so this is not proof of SSD-backed KV persistence.

## Prefix Block Store

The prefix block store is Phase 1 scaffolding. It writes content-addressed metadata for prompt blocks and classifies them as:

- `attention-sink-candidate`: earliest reusable prefix blocks that should stay hot in later KV experiments.
- `stable-prefix`: reusable workflow context that is a candidate for SSD persistence.
- `rolling-tail-candidate`: semi-stable tail state that may be warm but not universal.
- `volatile-tail`: current findings, CI output, review comments, or other state that should not be blindly persisted.

If repeated Codex-style workflows spend meaningful time in `prompt_eval_duration`, then an SSD-backed prefix/KV cache has a real target to beat.

## llama.cpp Prompt Cache

The llama.cpp benchmark is the first close backend baseline for persistence. It saves the reusable prefix slot cache to disk, starts fresh server processes, restores the slot, and measures changed-tail prompt processing cost.

Use it to decide whether the next prototype should wrap llama.cpp slot persistence, compare against it, or move lower-level into custom KV storage.

## Flashcache Wrapper

The Flashcache wrapper is the first product-shaped layer. It accepts an OpenAI-style chat request plus optional `ssd_cache` metadata, manages llama.cpp slot save/restore, and returns cache telemetry to the caller.

Treat the wrapper as an experimental local API subset: non-streaming text responses only, cache-aware requests opt in explicitly, and volatile tail text is not persisted unless debug behavior asks for it.
