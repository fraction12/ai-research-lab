# Benchmark Results

## 2026-06-02: Printtestbot Printing Press Workflow on DushyantPC

Fixture: `benchmarks/fixtures/printtestbot_printing_press_workflow.json`

Recorded dataset: `benchmarks/datasets/printtestbot-printing-press-2026-06-02/`

Source shape: sanitized Printy/printtestbot-style workflow distilled from Print-A-Bot prompt assembly and a Printing Press CLI fix/retry loop. The fixture is not a raw transcript and contains no secrets, tokens, private chat IDs, private keys, or personal context.

### Fixture Shape

| Block role | Blocks | Bytes | Notes |
| --- | ---: | ---: | --- |
| Stable prefix | 7 | 4,138 | Printy identity, runtime contract, model routing, tool schema, guardrails, workflow rules. |
| Semi-stable context | 1 | 586 | Current repo/task/test-plan context. |
| Volatile tails | 7 | 2,609 | User request, command output, failures, patch state, review notes, final validation. |

The reusable prefix boundary is before the volatile tail:

```text
stable bot/runtime/tool/policy prefix + semi-stable repo/task context -> save or reuse
volatile command-output tail per turn -> do not blindly cache
```

### Frontier vs Local No-Custom-Cache Simulation

User intent: compare the normal Print-A-Bot local model route against frontier Codex. For frontier, this uses Codex `gpt-5.5`, not a generic OpenAI API model. For local, this uses normal Ollama `gpt-oss:20b` on DushyantPC, with no Flashcache, no llama.cpp slot restore, and no custom KV persistence.

Codex command:

```bash
python3 benchmarks/codex_frontier_workflow_benchmark.py --fixture benchmarks/fixtures/printtestbot_printing_press_workflow.json --model gpt-5.5 --reasoning-effort xhigh --runs 2 --sandbox read-only --timeout 900 --output-dir benchmarks/datasets/printtestbot-printing-press-2026-06-02/raw
```

Codex result:

```text
benchmarks/datasets/printtestbot-printing-press-2026-06-02/raw/20260603T001326Z-gpt-5.5-printtestbot-printing-press-workflow-codex-frontier.json
```

Ollama timing command:

```powershell
python benchmarks\ollama_workflow_benchmark.py --fixture benchmarks\fixtures\printtestbot_printing_press_workflow.json --model gpt-oss:20b --host http://localhost:11434 --strategy full --runs 3 --vary-runs --num-predict 64 --temperature 0 --timeout 900 --output-dir benchmarks\datasets\printtestbot-printing-press-2026-06-02\raw
```

Ollama timing result:

```text
benchmarks/datasets/printtestbot-printing-press-2026-06-02/raw/20260603T001246Z-gpt-oss-20b-printtestbot_printing_press_workflow.json
```

Ollama `think=false` probe:

```powershell
python benchmarks\ollama_workflow_benchmark.py --fixture benchmarks\fixtures\printtestbot_printing_press_workflow.json --model gpt-oss:20b --host http://localhost:11434 --strategy full --runs 2 --num-predict 128 --think false --temperature 0 --timeout 900 --output-dir benchmarks\datasets\printtestbot-printing-press-2026-06-02\raw
```

Ollama `think=false` result:

```text
benchmarks/datasets/printtestbot-printing-press-2026-06-02/raw/20260603T002322Z-gpt-oss-20b-printtestbot_printing_press_workflow.json
```

| Runner | Runs | Mean wall | Mean prompt/input tokens | Mean uncached input | Mean output/gen tokens | Final response success |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Codex `gpt-5.5` | 14 | 13,680.5 ms | 15,087.9 input | 11,997.6 | 588.6 output, 475.9 reasoning | 14 / 14 |
| Ollama `gpt-oss:20b`, 64-token cap | 21 | 7,650.9 ms | 1,360.7 prompt | n/a | 64.0 generated | 0 / 21 |
| Ollama `gpt-oss:20b`, `think=false`, 128-token cap | 14 | 16,071.8 ms | 1,335.7 prompt | n/a | 128.0 generated | 0 / 14 |

Token-efficiency read:

- Codex used about `11.1x` more reported input tokens per turn than Ollama reported prompt tokens.
- Counting only uncached Codex input, Codex still used about `8.8x` more input tokens per turn.
- This is not a tokenizer-pure measurement; it captures real Codex agent runtime overhead, project instructions, and the benchmark prompt.

Cost-effectiveness read:

- Codex CLI exposes token usage but not an exact per-run dollar charge, so this dataset does not claim precise Codex dollars.
- Local Ollama has no marginal API bill on owned hardware and is much cheaper for bulk prompt-cost simulation.
- The current local `gpt-oss:20b` route is not yet a good Print-A-Bot replacement for Codex because the Ollama API returned thinking-channel content without final `response` text in the local probes. Print-A-Bot's current local runner reads `response`, so these local runs would be treated as empty and fall back to Codex.
- Practical result: local is more token-frugal, but Codex remains the reliable answer path until the local runner/model pairing can produce final response text consistently.

### Ollama Full Prompt Baseline

Command run on DushyantPC:

```bash
python benchmarks/ollama_workflow_benchmark.py --fixture benchmarks/fixtures/printtestbot_printing_press_workflow.json --model gpt-oss:20b --host http://localhost:11434 --strategy full --runs 1 --num-predict 8 --temperature 0 --timeout 900
```

Result JSON:

```text
benchmarks/datasets/printtestbot-printing-press-2026-06-02/raw/ollama-full-gpt-oss-20b.json
```

| Scenario | Prompt tokens | Total | Load | Prompt eval |
| --- | ---: | ---: | ---: | ---: |
| `turn-01-intake` | 1,324 | 2,404.5 ms | 291.9 ms | 1,658.0 ms |
| `turn-02-inspect` | 1,354 | 1,090.7 ms | 203.6 ms | 439.8 ms |
| `turn-03-verify-failure` | 1,336 | 1,185.1 ms | 261.6 ms | 457.0 ms |
| `turn-04-patch-state` | 1,347 | 1,202.7 ms | 270.3 ms | 454.6 ms |
| `turn-05-test-and-vet-failure` | 1,335 | 1,170.6 ms | 257.1 ms | 428.4 ms |
| `turn-06-review-feedback` | 1,334 | 1,137.9 ms | 258.4 ms | 424.0 ms |
| `turn-07-final-handoff` | 1,355 | 1,157.8 ms | 257.7 ms | 454.4 ms |

### Exact Repeat Control

Command:

```bash
python benchmarks/ollama_workflow_benchmark.py --fixture benchmarks/fixtures/printtestbot_printing_press_workflow.json --model gpt-oss:20b --host http://localhost:11434 --scenario turn-03-verify-failure --strategy full --runs 2 --num-predict 8 --temperature 0 --timeout 900
```

Result JSON:

```text
benchmarks/datasets/printtestbot-printing-press-2026-06-02/raw/ollama-exact-repeat-gpt-oss-20b.json
```

| Run | Prompt tokens | Total | Load | Prompt eval |
| --- | ---: | ---: | ---: | ---: |
| 1 | 1,336 | 1,189.9 ms | 280.6 ms | 461.6 ms |
| 2 | 1,336 | 778.5 ms | 266.1 ms | 74.0 ms |

This proves exact replay gets cheap, but exact replay is not the target workload.

### Ollama Context Proxy

Command:

```bash
python benchmarks/ollama_workflow_benchmark.py --fixture benchmarks/fixtures/printtestbot_printing_press_workflow.json --model gpt-oss:20b --host http://localhost:11434 --strategy compare --runs 1 --num-predict 8 --prime-num-predict 1 --temperature 0 --timeout 900
```

Result JSON:

```text
benchmarks/datasets/printtestbot-printing-press-2026-06-02/raw/ollama-prefix-context-compare-gpt-oss-20b.json
```

| Strategy | Prompt eval sum | Notes |
| --- | ---: | --- |
| Full prompt | 3,252.7 ms | Aligned full prompts stayed warm inside Ollama. |
| Prefix-context proxy | 4,826.2 ms | Includes 1,489.8 ms prime cost. |
| Full minus prefix-context | -1,573.6 ms | Negative means the proxy was slower by 48.4%. |

Interpretation: Ollama's deprecated `context` proxy is not the layer to build around. Aligned full prompts already benefit while the model is warm.

### Warm vs Restarted Persistence Gap

Command:

```bash
python benchmarks/ollama_workflow_benchmark.py --fixture benchmarks/fixtures/printtestbot_printing_press_workflow.json --model gpt-oss:20b --host http://localhost:11434 --strategy restart-compare --runs 1 --num-predict 8 --temperature 0 --timeout 900 --write-prefix-manifest
```

Result JSON:

```text
benchmarks/datasets/printtestbot-printing-press-2026-06-02/raw/ollama-restart-compare-gpt-oss-20b.json
```

Prefix manifest:

```text
benchmarks/datasets/printtestbot-printing-press-2026-06-02/raw/prefix-manifest-gpt-oss-20b.json
```

| Sequence | Prompt eval sum | Total duration sum | Load duration sum |
| --- | ---: | ---: | ---: |
| Warm sequence | 4,428.6 ms | 15,458.2 ms | 7,806.6 ms |
| Restarted sequence | 10,456.5 ms | 48,107.0 ms | 33,831.4 ms |
| Restarted minus warm | 6,027.9 ms | 32,648.9 ms | 26,024.8 ms |

Restarted prompt eval was `2.36x` the warm sequence. This is the strongest signal for SSD-native prefix/KV persistence: changed-tail workflows get warm-prefix benefit while the model remains loaded, and lose much of it when the model is restarted between turns.

### llama.cpp Slot Save/Restore

Command run on DushyantPC after installing `ggml.llamacpp` with winget and downloading `gemma-3-270m-it-Q8_0.gguf`:

```bash
python benchmarks/llama_cpp_prompt_cache_benchmark.py --model benchmarks/models/gemma-3-270m-it-Q8_0.gguf --fixture benchmarks/fixtures/printtestbot_printing_press_workflow.json --predict 8 --temperature 0 --timeout 240
```

Result JSON:

```text
benchmarks/datasets/printtestbot-printing-press-2026-06-02/raw/llama-cpp-slot-cache-gemma-3-270m-it-q8.json
```

Server:

```text
llama-server version: 9469 (d178a1181)
```

| Metric | Value |
| --- | ---: |
| Reusable prefix bytes | 5,487 |
| Slot cache file bytes | 19,567,436 |
| Baseline prompt ms sum | 466.950 ms |
| Restored prompt ms sum | 216.115 ms |
| Baseline minus restored | 250.835 ms |
| Reduction ratio | 53.7% |

This validates the slot save/restore boundary on the same fixture. It uses a small model for cache mechanics, not quality.

### Flashcache Wrapper

Command:

```bash
python benchmarks/flashcache_wrapper_benchmark.py --model benchmarks/models/gemma-3-270m-it-Q8_0.gguf --fixture benchmarks/fixtures/printtestbot_printing_press_workflow.json --predict 8 --temperature 0 --timeout 240
```

Result JSON:

```text
benchmarks/datasets/printtestbot-printing-press-2026-06-02/raw/flashcache-wrapper-gemma-3-270m-it-q8.json
```

| Metric | Value |
| --- | ---: |
| Direct prompt ms sum | 484.884 ms |
| Wrapper prompt ms sum | 192.692 ms |
| Direct minus wrapper | 292.192 ms |
| Reduction ratio | 60.3% |
| Wrapper cache hit rate | 85.7% |

The wrapper had one expected miss while priming the prefix and six hits afterward.

### OpenAI OSS / gpt-oss-20b GGUF Follow-Up

Command run on DushyantPC after installing portable llama.cpp `b9482` and downloading `ggml-org/gpt-oss-20b-GGUF`:

```bash
python benchmarks/llama_cpp_prompt_cache_benchmark.py --server-bin C:\Users\Dushyant\Tools\llama-b9482-vulkan\llama-server.exe --model benchmarks\models\gpt-oss-20b-mxfp4.gguf --fixture benchmarks\fixtures\printtestbot_printing_press_workflow.json --predict 8 --temperature 0 --timeout 900 --ctx-size 4096
```

Result JSON:

```text
benchmarks/datasets/printtestbot-printing-press-2026-06-02/raw/20260602T220157Z-gpt-oss-20b-mxfp4-printtestbot_printing_press_workflow-llama-cpp-prompt-cache.json
```

| Metric | Value |
| --- | ---: |
| Model bytes | 12,109,566,560 |
| Reusable prefix bytes | 5,487 |
| Slot cache file bytes | 31,108,988 |
| Baseline prompt ms sum | 8,412.695 ms |
| Restored prompt ms sum | 8,442.375 ms |
| Baseline minus restored | -29.680 ms |
| Reduction ratio | -0.35% |

The one-turn smoke was also recorded:

```text
benchmarks/datasets/printtestbot-printing-press-2026-06-02/raw/20260602T215635Z-gpt-oss-20b-mxfp4-printtestbot_printing_press_workflow-llama-cpp-prompt-cache.json
```

Smoke result: baseline `1,300.479 ms`, restored `1,243.571 ms`, restore `17.093 ms`, slot file `31,108,988` bytes. The full seven-turn run is the better signal: slot restore itself is cheap, but with this model/build/prefix size, direct restored full-prompt evaluation did not beat direct cold full-prompt evaluation.

Flashcache wrapper comparison with the same `gpt-oss-20b` GGUF:

```bash
python benchmarks/flashcache_wrapper_benchmark.py --server-bin C:\Users\Dushyant\Tools\llama-b9482-vulkan\llama-server.exe --model benchmarks\models\gpt-oss-20b-mxfp4.gguf --fixture benchmarks\fixtures\printtestbot_printing_press_workflow.json --predict 8 --temperature 0 --timeout 900 --ctx-size 4096
```

Result JSON:

```text
benchmarks/datasets/printtestbot-printing-press-2026-06-02/raw/20260602T220711Z-gpt-oss-20b-mxfp4-printtestbot_printing_press_workflow-flashcache-wrapper.json
```

| Metric | Value |
| --- | ---: |
| Direct prompt ms sum | 8,452.938 ms |
| Wrapper prompt ms sum | 7,374.758 ms |
| Direct minus wrapper | 1,078.180 ms |
| Reduction ratio | 12.8% |
| Wrapper cache hit rate | 85.7% |

Important backend notes:

- Winget `ggml.llamacpp` version `9469` could not load either the Ollama `gpt-oss:20b` blob or the official GGUF: `unknown model architecture: 'gptoss'`.
- Portable llama.cpp `b9482` could load the official `gpt-oss-20b-mxfp4.gguf`.
- The Ollama `gpt-oss:20b` blob still failed under `b9482`, so the llama.cpp benchmark uses the official `ggml-org` GGUF, not the Ollama blob.

### Interpretation

The Printy fixture supports the core hypothesis: real changed-tail agent workflows have a stable-prefix persistence gap.

What worked:

- Aligned prompt layout matters.
- Warm Ollama runs reuse enough prefix work to make later changed-tail turns cheaper.
- Restarting the model removes much of that benefit.
- llama.cpp slot save/restore and the Flashcache wrapper reduce prompt processing on the same boundary.
- For `gpt-oss-20b`, the wrapper produced a measurable win, but direct slot restore did not. The larger model/backend changes the shape of the result.

What did not work:

- Exact replay is too easy and not meaningful for the product claim.
- Ollama `context` proxy was slower than aligned full prompts.
- The small llama.cpp model does not tell us whether a larger local model remains correct; it only tests cache mechanics.
- Direct restored full-prompt evaluation on `gpt-oss-20b` was effectively flat/slightly worse on this small prefix. This points to prompt layout/prefix size/backend behavior, not a blanket win for slot restore.

Next benchmark step: keep this fixture, raise generation length, and add a quality rubric so speedup is measured alongside whether the local model chooses the same next action after restore.

## 2026-06-02: Ollama Codex/DeepClean Workflow Baseline

Command:

```bash
python3 benchmarks/ollama_workflow_benchmark.py --model gemma4:latest --runs 1 --num-predict 8 --temperature 0
```

Fixture: `benchmarks/fixtures/codex_deepclean_workflow.json`

Model: `gemma4:latest`

### Changed-tail workflow runs

| Scenario | Prompt tokens | Total | Load | Prompt eval | Prompt eval rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| `deepclean-autofix-intake` | 1,076 | 16,336.3 ms | 10,524.1 ms | 5,091.4 ms | 211.3 tok/s |
| `ci-fix-loop` | 1,062 | 3,970.2 ms | 154.4 ms | 3,586.0 ms | 296.2 tok/s |
| `review-comment-loop` | 1,060 | 4,218.5 ms | 143.4 ms | 3,845.7 ms | 275.6 tok/s |

### Exact repeated prompt run

Command:

```bash
python3 benchmarks/ollama_workflow_benchmark.py --model gemma4:latest --scenario deepclean-autofix-intake --runs 2 --num-predict 8 --temperature 0
```

| Run | Prompt tokens | Total | Load | Prompt eval | Prompt eval rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 1,076 | 4,093.2 ms | 197.0 ms | 3,666.4 ms | 293.5 tok/s |
| 2 | 1,076 | 408.3 ms | 142.6 ms | 33.6 ms | 32,023.4 tok/s |

### Interpretation

This baseline suggests Ollama can make an exact repeated prompt dramatically cheaper while changed-tail workflow prompts still pay several seconds of prompt evaluation.

For this repo, that distinction matters: exact prompt replay is not enough for agent workloads. The future SSD-native target is reusable prefix or KV state for the stable workflow prefix while allowing the volatile tail to change.

## 2026-06-02: LightningITB DeepClean Campaign Fixture

Command:

```bash
python3 benchmarks/ollama_workflow_benchmark.py --model gemma4:latest --fixture benchmarks/fixtures/lightningitb_deepclean_campaign.json --runs 1 --num-predict 8 --temperature 0
```

Fixture: `benchmarks/fixtures/lightningitb_deepclean_campaign.json`

Source: sanitized prompt distilled from the LightningITB archived DeepClean P1/P2 campaign design and testing delta.

### Changed-tail workflow runs

| Scenario | Prompt tokens | Total | Load | Prompt eval | Prompt eval rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| `scoped-run-next-action` | 1,088 | 19,551.3 ms | 12,529.7 ms | 6,495.4 ms | 167.5 tok/s |
| `pr-review-ci-loop` | 847 | 4,101.0 ms | 159.0 ms | 3,668.2 ms | 230.9 tok/s |
| `ledger-after-merge` | 805 | 4,103.1 ms | 149.1 ms | 3,682.1 ms | 218.6 tok/s |

### Exact repeated prompt run

Command:

```bash
python3 benchmarks/ollama_workflow_benchmark.py --model gemma4:latest --fixture benchmarks/fixtures/lightningitb_deepclean_campaign.json --scenario scoped-run-next-action --runs 2 --num-predict 8 --temperature 0
```

| Run | Prompt tokens | Total | Load | Prompt eval | Prompt eval rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 1,088 | 5,533.0 ms | 222.7 ms | 5,005.5 ms | 217.4 tok/s |
| 2 | 1,088 | 461.4 ms | 142.5 ms | 41.9 ms | 25,966.6 tok/s |

### Interpretation

The LightningITB fixture confirms the first benchmark result with a real campaign-shaped prompt: exact prompt replay becomes cheap, but changed-tail workflow scenarios still spend seconds in prompt evaluation.

This points the next prototype toward stable-prefix reuse with a changing tail rather than whole-prompt exact replay.

## 2026-06-02: Full Prompt vs Ollama Context Proxy

Command:

```bash
python3 benchmarks/ollama_workflow_benchmark.py --strategy compare --model gemma4:latest --fixture benchmarks/fixtures/lightningitb_deepclean_campaign.json --runs 1 --num-predict 8 --prime-num-predict 1 --temperature 0
```

This run uses the corrected prompt layout, where scenario metadata appears after reusable blocks so the stable prefix is actually aligned.

### One-pass comparison

| Strategy | Prompt eval sum | Notes |
| --- | ---: | --- |
| Full prompt | 4,852.3 ms | Later scenarios benefited from aligned-prefix reuse inside Ollama. |
| Prefix-context proxy | 5,442.6 ms | Includes 2,475.2 ms prime cost plus changed-tail calls. |
| Full minus prefix-context | -590.2 ms | Negative means the proxy was slower by 12.2%. |

Full-prompt scenario detail:

| Scenario | Prompt tokens | Prompt eval |
| --- | ---: | ---: |
| `scoped-run-next-action` | 1,089 | 3,755.2 ms |
| `pr-review-ci-loop` | 848 | 653.4 ms |
| `ledger-after-merge` | 806 | 443.7 ms |

Prefix-context detail:

| Step | Prompt tokens | Prompt eval |
| --- | ---: | ---: |
| Prime reusable prefix | 713 | 2,475.2 ms |
| `scoped-run-next-action` tail | 1,166 | 1,656.1 ms |
| `pr-review-ci-loop` tail | 925 | 727.3 ms |
| `ledger-after-merge` tail | 883 | 583.9 ms |

### Controlled unload pair

Commands:

```bash
ollama stop gemma4:latest
python3 benchmarks/ollama_workflow_benchmark.py --strategy full --model gemma4:latest --fixture benchmarks/fixtures/lightningitb_deepclean_campaign.json --runs 1 --num-predict 8 --temperature 0
ollama stop gemma4:latest
python3 benchmarks/ollama_workflow_benchmark.py --strategy prefix-context --model gemma4:latest --fixture benchmarks/fixtures/lightningitb_deepclean_campaign.json --runs 1 --num-predict 8 --prime-num-predict 1 --temperature 0
```

| Strategy | Prompt eval sum | Notes |
| --- | ---: | --- |
| Full prompt | 6,783.3 ms | First scenario paid 5,625.5 ms; later aligned-prefix scenarios were 698.0 ms and 459.8 ms. |
| Prefix-context proxy | 8,036.2 ms | Prime cost was 4,757.9 ms; tails were 1,853.2 ms, 728.3 ms, and 696.8 ms. |
| Full minus prefix-context | -1,252.9 ms | Negative means the proxy was slower by 18.5%. |

### Interpretation

The API-level `context` proxy does not currently beat simply sending well-aligned full prompts to Ollama for this fixture. The useful signal is that prompt layout matters: once stable blocks are aligned before volatile state, Ollama appears to reuse the common prefix inside the running model session.

That changes the next target. The repo should not spend much effort wrapping Ollama `context` as the product layer. The more valuable question is whether we can make aligned-prefix reuse persistent, inspectable, portable across sessions, and eventually SSD-backed.

## 2026-06-02: Warm vs Restarted Persistence Gap

Command:

```bash
python3 benchmarks/ollama_workflow_benchmark.py --strategy restart-compare --model gemma4:latest --fixture benchmarks/fixtures/lightningitb_deepclean_campaign.json --runs 1 --num-predict 8 --temperature 0 --write-prefix-manifest
```

This run compares:

- `warm-sequence`: stop the model once, then run all changed-tail prompts while Ollama stays warm.
- `restarted-sequence`: stop the model before every changed-tail prompt.

### Warm sequence

| Scenario | Prompt tokens | Load | Prompt eval |
| --- | ---: | ---: | ---: |
| `scoped-run-next-action` | 1,089 | 14,070.0 ms | 6,588.6 ms |
| `pr-review-ci-loop` | 848 | 164.0 ms | 827.5 ms |
| `ledger-after-merge` | 806 | 148.1 ms | 569.0 ms |

Warm prompt eval sum: `7,985.0 ms`

### Restarted sequence

| Scenario | Prompt tokens | Load | Prompt eval |
| --- | ---: | ---: | ---: |
| `scoped-run-next-action` | 1,089 | 7,349.0 ms | 7,576.1 ms |
| `pr-review-ci-loop` | 848 | 6,364.7 ms | 7,003.2 ms |
| `ledger-after-merge` | 806 | 6,869.5 ms | 6,485.8 ms |

Restarted prompt eval sum: `21,065.1 ms`

### Persistence gap

| Metric | Value |
| --- | ---: |
| Warm prompt eval sum | 7,985.0 ms |
| Restarted prompt eval sum | 21,065.1 ms |
| Restarted minus warm | 13,080.1 ms |
| Ratio | 1.638 |

### Interpretation

This is the clearest value signal so far. Ollama appears to reuse aligned stable-prefix work while the model stays warm, but that benefit largely disappears when the model is stopped before each prompt.

For SSD-native inference, this creates a concrete target: preserve reusable prefix/KV state across sessions so restarted or cold local-agent workflows behave more like the warm sequence.

## 2026-06-02: Prefix Block Store Metadata

Command:

```bash
python3 benchmarks/prefix_block_store.py --fixture benchmarks/fixtures/lightningitb_deepclean_campaign.json --model gemma4:latest
```

Cache key:

```text
7d5757b388ea98c9c7c4568e73478f23b1543fde6d8417b6b95dc472c8b56c6c
```

Generated manifest:

```text
benchmarks/prefix-store/manifests/7d5757b388ea98c9c7c4568e73478f23b1543fde6d8417b6b95dc472c8b56c6c.json
```

The generated prefix store is ignored and can be rebuilt from the fixture.

### Role summary

| Role | Blocks | Bytes | Meaning |
| --- | ---: | ---: | --- |
| `attention-sink-candidate` | 1 | 384 | First reusable block to keep hot in later KV experiments. |
| `stable-prefix` | 4 | 2,035 | Reusable workflow context, SSD-persistent candidate. |
| `rolling-tail-candidate` | 1 | 765 | Semi-stable tail context that may stay warm but is not universal. |
| `volatile-tail` | 3 | 1,023 | Current run state that should not be blindly persisted. |

Attention-sink candidate:

```text
codex-agent-contract
```

### Interpretation

This is Phase 1 scaffolding, not a speedup yet. It gives the next backend experiment explicit cache-key material and memory-tier roles so real KV persistence can avoid treating all old prompt state as equally disposable.

## 2026-06-02: llama.cpp Slot Prompt Cache Feasibility

Command:

```bash
python3 benchmarks/llama_cpp_prompt_cache_benchmark.py --model benchmarks/models/gemma-3-270m-it-Q8_0.gguf --fixture benchmarks/fixtures/lightningitb_deepclean_campaign.json --predict 8 --temperature 0
```

Server:

```text
llama-server version: 9430 (d48a56eff)
```

Model: `gemma-3-270m-it-Q8_0.gguf`

Result JSON:

```text
benchmarks/llama-cpp-results/20260602T194436Z-gemma-3-270m-it-Q8_0-lightningitb_deepclean_campaign-llama-cpp-prompt-cache.json
```

### Reusable prefix

| Metric | Value |
| --- | ---: |
| Prefix bytes | 2,898 |
| Prefix prompt tokens | 665 |
| Saved slot tokens | 672 |
| Slot cache file bytes | 12,405,596 |
| Save time | 1.479 ms |

### Full-prompt baseline

Each row starts a fresh `llama-server` process and sends the full changed-tail prompt.

| Scenario | Prompt tokens processed | Prompt eval |
| --- | ---: | ---: |
| `scoped-run-next-action` | 1,074 | 112.817 ms |
| `pr-review-ci-loop` | 833 | 125.011 ms |
| `ledger-after-merge` | 791 | 72.858 ms |

Baseline prompt eval sum: `310.686 ms`

### Restored-prefix runs

Each row starts a fresh `llama-server` process, restores the saved prefix slot, then sends the same full changed-tail prompt.

| Scenario | Prompt tokens processed | Prompt eval | Restore time |
| --- | ---: | ---: | ---: |
| `scoped-run-next-action` | 410 | 96.208 ms | 1.815 ms |
| `pr-review-ci-loop` | 169 | 26.438 ms | 1.601 ms |
| `ledger-after-merge` | 127 | 50.265 ms | 1.458 ms |

Restored prompt eval sum: `172.911 ms`

### Comparison

| Metric | Value |
| --- | ---: |
| Baseline prompt eval sum | 310.686 ms |
| Restored prompt eval sum | 172.911 ms |
| Baseline minus restored | 137.775 ms |
| Reduction | 52.3% |

### Interpretation

llama.cpp can persist and restore reusable prompt/KV state across fresh local server processes for this fixture. On this small model, restored-prefix runs processed fewer prompt tokens and cut prompt evaluation time by roughly half before counting the tiny restore overhead.

This does not make the SSD-native idea obsolete. It sharpens the bar. A custom local-agent layer now needs to either wrap llama.cpp slot persistence cleanly, provide better cache indexing and eviction around it, or demonstrate value that llama.cpp's existing slot cache does not cover.

## 2026-06-02: Flashcache Wrapper Smoke Benchmark

Command:

```bash
python3 benchmarks/flashcache_wrapper_benchmark.py --model benchmarks/models/gemma-3-270m-it-Q8_0.gguf --fixture benchmarks/fixtures/lightningitb_deepclean_campaign.json --predict 8 --temperature 0
```

Result JSON:

```text
benchmarks/flashcache-results/20260602T200242Z-gemma-3-270m-it-Q8_0-lightningitb_deepclean_campaign-flashcache-wrapper.json
```

### Direct llama.cpp full-prompt baseline

| Scenario | Prompt tokens processed | Prompt eval |
| --- | ---: | ---: |
| `scoped-run-next-action` | 1,074 | 133.507 ms |
| `pr-review-ci-loop` | 833 | 79.803 ms |
| `ledger-after-merge` | 791 | 71.655 ms |

Direct prompt eval sum: `284.965 ms`

### Flashcache wrapper cache-aware calls

| Scenario | Cache state | Prompt tokens processed | Prompt eval | Slot overhead |
| --- | --- | ---: | ---: | ---: |
| `scoped-run-next-action` | `miss` | 415 | 49.776 ms | save 4.454 ms |
| `pr-review-ci-loop` | `hit` | 174 | 55.597 ms | restore 2.029 ms |
| `ledger-after-merge` | `hit` | 132 | 30.550 ms | restore 2.436 ms |

Wrapper prompt eval sum: `135.923 ms`

### Comparison

| Metric | Value |
| --- | ---: |
| Direct prompt eval sum | 284.965 ms |
| Wrapper prompt eval sum | 135.923 ms |
| Direct minus wrapper | 149.042 ms |
| Reduction | 52.3% |
| Wrapper cache hit rate | 66.7% |

### Interpretation

The first wrapper layer reproduced the llama.cpp feasibility signal through a product-shaped API. A cache-aware request missed once, saved the stable prefix slot cache, then restored it for the next two changed-tail scenarios.

This is still a small-model smoke benchmark, not a production claim. The useful result is architectural: an OpenAI-style local endpoint can hide raw slot-file mechanics while still producing measurable cache telemetry for local-agent workflows.
