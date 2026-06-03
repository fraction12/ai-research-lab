# Printtestbot Session-Tail Benchmark Dataset

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

This dataset tests `--cache-mode session-tail`.

Session-tail mode prewarms the reusable prefix slot, restores that slot once into a persistent wrapper server, and then sends only the changed tail for each measured turn. It directly tests the product-shaped hypothesis that stable repo/tool/session context can be loaded once while later agent turns only append new state.

## Raw Results

- `raw/20260603T025255Z-gpt-oss-20b-mxfp4-printtestbot-printing-press-workflow-large-prefix-16kb-flashcache-wrapper.json`
- `raw/20260603T025423Z-gpt-oss-20b-mxfp4-printtestbot-printing-press-workflow-large-prefix-32kb-flashcache-wrapper.json`
- `raw/20260603T025602Z-gpt-oss-20b-mxfp4-printtestbot-printing-press-workflow-large-prefix-64kb-flashcache-wrapper.json`

## Headline Results

| Fixture | Context | Prefix bytes | Direct prompt ms | Session-tail prompt ms | Delta | Ratio | Hit rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 16 KB | 8,192 | 16,402 | 4,292.852 | 2,108.684 | 2,184.168 | 50.9% | 100.0% |
| 32 KB | 16,384 | 32,786 | 7,385.725 | 2,379.596 | 5,006.129 | 67.8% | 100.0% |
| 64 KB | 32,768 | 65,554 | 13,765.509 | 2,775.570 | 10,989.939 | 79.8% | 100.0% |

## Session Setup Read

| Fixture | Session setup wall ms | One-time restore ms | Slot file bytes |
| --- | ---: | ---: | ---: |
| 16 KB | 21,072.291 | 46.759 | 94,310,428 |
| 32 KB | 21,696.854 | 68.169 | 184,636,844 |
| 64 KB | 21,147.377 | 156.260 | 360,863,116 |

The setup wall includes server startup and server identity lookup. The one-time restore itself is small compared with repeatedly restoring the slot before every turn.

## Interpretation

This is the strongest current support for the SSD-native local-agent direction.

The previous `session` benchmark restored the prefix once but kept sending full prompts. It barely helped because the first measured turn still reprocessed the full prefix. `session-tail` changes the shape: restore the stable prefix once, then send only changed tails. That brings back almost the same scaling as hot-cache mode without paying per-turn restore.

The result does not prove final answer quality yet. It proves the benchmark path can preserve prompt-processing savings in the shape a real local-agent session wants.

## Next Question

The next prototype should turn this benchmark-only mode into an explicit session API:

- open or restore a cache-backed session,
- append changed-tail turns,
- reset to the clean prefix when needed,
- and score output quality against the full-prompt baseline.

Summarize with:

```bash
python3 benchmarks/summarize_results.py benchmarks/datasets/printtestbot-session-tail-2026-06-03/raw
```
