# Large Prefix Benchmark Ladder

## Purpose

The first Printy fixture has a reusable prefix of about 5.5 KB. It showed repeated Flashcache wrapper savings on DushyantPC, but that prefix is smaller than a real local-agent session with tool schemas, repo maps, memory, and specs.

This ladder tests whether cache value grows as reusable prefix size increases.

## Generated Fixtures

Generate or refresh the fixtures from the Mac/Git repo:

```bash
python3 benchmarks/generate_large_prefix_fixtures.py
```

Generated fixtures:

```text
benchmarks/fixtures/printtestbot-printing-press-workflow-large-prefix-16kb.json
benchmarks/fixtures/printtestbot-printing-press-workflow-large-prefix-32kb.json
benchmarks/fixtures/printtestbot-printing-press-workflow-large-prefix-64kb.json
```

Dry-run inspection:

```bash
python3 benchmarks/generate_large_prefix_fixtures.py --dry-run
python3 benchmarks/ollama_workflow_benchmark.py --fixture benchmarks/fixtures/printtestbot-printing-press-workflow-large-prefix-16kb.json --dry-run
```

## Current Context Guidance

| Fixture | Target prefix | Actual reusable prefix | Largest prompt | Recommended ctx |
| --- | ---: | ---: | ---: | ---: |
| `large-prefix-16kb` | 16,384 bytes | 16,384 bytes | ~17.1 KB | 8,192 |
| `large-prefix-32kb` | 32,768 bytes | 32,768 bytes | ~33.4 KB | 16,384 |
| `large-prefix-64kb` | 65,536 bytes | 65,536 bytes | ~66.2 KB | 32,768 |

The generator records exact values in each fixture's `metadata.generated_large_prefix` object.

## DushyantPC Commands

Use the portable llama.cpp build for `gpt-oss-20b-mxfp4.gguf`:

```powershell
$server = 'C:\Users\Dushyant\Tools\llama-b9482-vulkan\llama-server.exe'
$model = 'benchmarks\models\gpt-oss-20b-mxfp4.gguf'
$out = 'benchmarks\datasets\printtestbot-large-prefix-2026-06-02\raw'
```

16 KB:

```powershell
python benchmarks\llama_cpp_prompt_cache_benchmark.py --server-bin $server --model $model --fixture benchmarks\fixtures\printtestbot-printing-press-workflow-large-prefix-16kb.json --predict 8 --temperature 0 --timeout 1200 --ctx-size 8192 --output-dir $out
python benchmarks\flashcache_wrapper_benchmark.py --server-bin $server --model $model --fixture benchmarks\fixtures\printtestbot-printing-press-workflow-large-prefix-16kb.json --predict 8 --temperature 0 --timeout 1200 --ctx-size 8192 --output-dir $out
```

32 KB:

```powershell
python benchmarks\llama_cpp_prompt_cache_benchmark.py --server-bin $server --model $model --fixture benchmarks\fixtures\printtestbot-printing-press-workflow-large-prefix-32kb.json --predict 8 --temperature 0 --timeout 1500 --ctx-size 16384 --output-dir $out
python benchmarks\flashcache_wrapper_benchmark.py --server-bin $server --model $model --fixture benchmarks\fixtures\printtestbot-printing-press-workflow-large-prefix-32kb.json --predict 8 --temperature 0 --timeout 1500 --ctx-size 16384 --output-dir $out
```

64 KB:

```powershell
python benchmarks\llama_cpp_prompt_cache_benchmark.py --server-bin $server --model $model --fixture benchmarks\fixtures\printtestbot-printing-press-workflow-large-prefix-64kb.json --predict 8 --temperature 0 --timeout 2400 --ctx-size 32768 --output-dir $out
python benchmarks\flashcache_wrapper_benchmark.py --server-bin $server --model $model --fixture benchmarks\fixtures\printtestbot-printing-press-workflow-large-prefix-64kb.json --predict 8 --temperature 0 --timeout 2400 --ctx-size 32768 --output-dir $out
```

## Interpretation

Summarize result JSONs:

```bash
python3 benchmarks/summarize_results.py benchmarks/datasets/printtestbot-large-prefix-2026-06-02/raw
```

The decision rule:

- If wrapper savings grow with prefix size, Flashcache is a promising local-agent context cache layer.
- If wrapper savings flatten around the current 11-13%, the wrapper is useful but not the whole SSD-native inference thesis.
- If large context runs fail from memory/runtime pressure, the next layer should be adaptive prefix selection and eviction, not simply bigger saved prefixes.

## 2026-06-03 Result Snapshot

The first DushyantPC ladder completed for `gpt-oss-20b-mxfp4.gguf`.

| Fixture | Prefix bytes | Direct slot delta | Flashcache wrapper delta | Wrapper ratio | Hit rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| 16 KB | 16,402 | 224,799.817 ms | 2,714.827 ms | 13.7% | 85.7% |
| 32 KB | 32,786 | -168.360 ms | 4,943.916 ms | 12.8% | 85.7% |
| 64 KB | 65,554 | 182.939 ms | 11,388.079 ms | 13.9% | 85.7% |

Read this as:

- Flashcache wrapper savings scale in absolute terms as reusable prefix grows.
- Wrapper percentage reduction stayed near 13% for these generated fixtures.
- Raw direct slot restore remains noisy and should not be the product metric by itself.
- 64 KB reusable prefixes are mechanically feasible on DushyantPC with `ctx-size 32768`, but slot files grow to hundreds of megabytes.
