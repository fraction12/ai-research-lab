# Printtestbot Persistent Server Benchmark Dataset

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

This dataset reruns the Printtestbot large-prefix Flashcache wrapper benchmark with `--server-mode persistent`.

The goal is to separate reusable-prefix cache value from llama.cpp process startup cost. Direct full-prompt scenarios run through one persistent server. Wrapper cache-aware scenarios run through a separate persistent server.

## Raw Results

- `raw/20260603T015859Z-gpt-oss-20b-mxfp4-printtestbot-printing-press-workflow-large-prefix-16kb-flashcache-wrapper.json`
- `raw/20260603T020024Z-gpt-oss-20b-mxfp4-printtestbot-printing-press-workflow-large-prefix-32kb-flashcache-wrapper.json`
- `raw/20260603T020202Z-gpt-oss-20b-mxfp4-printtestbot-printing-press-workflow-large-prefix-64kb-flashcache-wrapper.json`

## Headline Results

| Fixture | Prefix bytes | Direct prompt ms | Wrapper prompt ms | Delta | Ratio | Hit rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 16 KB | 16,402 | 4,324.078 | 1,966.268 | 2,357.810 | 54.5% | 85.7% |
| 32 KB | 32,786 | 7,295.224 | 2,181.403 | 5,113.821 | 70.1% | 85.7% |
| 64 KB | 65,554 | 13,790.789 | 2,555.625 | 11,235.164 | 81.5% | 85.7% |

## Boundary Timing Read

| Fixture | Wrapper wall ms | Server enter ms | Server exit ms | Server version ms | Prefix prime ms | Save ms | Restore ms | Tail ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 16 KB | 31,468.648 | 10.401 | 0.007 | 25,270.727 | 2,742.213 | 83.712 | 240.832 | 3,073.653 |
| 32 KB | 34,423.260 | 26.830 | 0.008 | 24,973.971 | 5,449.249 | 147.068 | 432.522 | 3,345.318 |
| 64 KB | 42,112.979 | 14.295 | 0.006 | 25,230.780 | 11,651.340 | 247.251 | 852.882 | 4,068.091 |

## Interpretation

Persistent-server mode shows that Flashcache savings still scale with reusable prefix size in the local-agent shape where the model process stays alive.

The new server lifecycle fields are doing their job: `server_enter_ms` and `server_exit_ms` are tiny in persistent mode. The old missing wall-time bucket is no longer hidden.

The next avoidable cost is `server_version_ms`. The wrapper currently shells out to inspect the llama.cpp binary on every request, and that costs about 25 seconds across seven turns on this machine. The next benchmark should cache server-version identity per wrapper/config instance and rerun this same dataset shape.

Summarize with:

```bash
python3 benchmarks/summarize_results.py benchmarks/datasets/printtestbot-persistent-server-2026-06-03/raw
```
