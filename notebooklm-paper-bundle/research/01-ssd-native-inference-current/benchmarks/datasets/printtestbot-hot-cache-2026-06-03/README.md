# Printtestbot Hot Cache Benchmark Dataset

Date: 2026-06-03

Machine: DushyantPC

Model:

```text
gpt-oss-20b-mxfp4.gguf
```

llama.cpp:

```text
version: 9482 (4fb16eccc)
built with Clang 19.1.5 for Windows x86_64
```

## Purpose

This dataset reruns the persistent-server Printtestbot large-prefix benchmark with `--cache-mode hot`.

Hot mode prewarms the reusable prefix slot first, records that prewarm miss under `wrapper_prewarm`, and then measures all selected workflow turns as cache-aware requests. This separates cold cache-fill cost from steady-state local-agent turns where a stable prefix slot already exists on disk.

## Raw Results

- `raw/20260603T022014Z-gpt-oss-20b-mxfp4-printtestbot-printing-press-workflow-large-prefix-16kb-flashcache-wrapper.json`
- `raw/20260603T022118Z-gpt-oss-20b-mxfp4-printtestbot-printing-press-workflow-large-prefix-32kb-flashcache-wrapper.json`
- `raw/20260603T022235Z-gpt-oss-20b-mxfp4-printtestbot-printing-press-workflow-large-prefix-64kb-flashcache-wrapper.json`

## Headline Results

| Fixture | Prefix bytes | Direct prompt ms | Hot wrapper prompt ms | Delta | Ratio | Hit rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 16 KB | 16,402 | 4,317.695 | 1,891.131 | 2,426.564 | 56.2% | 100.0% |
| 32 KB | 32,786 | 7,250.831 | 2,090.956 | 5,159.875 | 71.2% | 100.0% |
| 64 KB | 65,554 | 13,774.331 | 2,482.388 | 11,291.943 | 82.0% | 100.0% |

## Boundary Timing Read

| Fixture | Measured wrapper wall ms | Restore ms | Tail ms | Server enter ms | Server version ms |
| --- | ---: | ---: | ---: | ---: | ---: |
| 16 KB | 3,509.356 | 396.043 | 2,982.981 | 69.149 | 0.005 |
| 32 KB | 4,289.532 | 696.132 | 3,422.256 | 110.083 | 0.006 |
| 64 KB | 5,527.960 | 1,268.418 | 4,070.490 | 126.037 | 0.005 |

## Excluded Prewarm Cost

| Fixture | Prewarm wall ms | Prefix prime ms | Slot save ms | Tail ms |
| --- | ---: | ---: | ---: | ---: |
| 16 KB | 6,833.248 | 2,737.965 | 88.954 | 427.481 |
| 32 KB | 9,639.331 | 5,457.417 | 160.392 | 475.297 |
| 64 KB | 16,114.354 | 11,752.549 | 246.484 | 555.298 |

## Interpretation

The measured hot-cache path is now clean: every measured wrapper turn is a cache hit. This is the best current approximation of a regular local-agent session after stable context has already been persisted.

Flashcache still saves more absolute prompt-processing time as reusable prefix size grows. The 64 KB fixture saves about 11.3 seconds of prompt processing across seven changed-tail turns.

The remaining hot-hit cost is mostly slot restore plus tail completion. That makes the next design question sharper: can we reduce restore overhead or avoid restoring the full prefix slot on every turn while preserving correctness?

Summarize with:

```bash
python3 benchmarks/summarize_results.py benchmarks/datasets/printtestbot-hot-cache-2026-06-03/raw
```
