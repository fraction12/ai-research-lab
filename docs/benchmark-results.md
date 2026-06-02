# Benchmark Results

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
