# Printtestbot Server Version Cache Benchmark Dataset

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

This dataset reruns the persistent-server Printtestbot large-prefix benchmark after caching `llama-server --version` output per `FlashcacheWrapper` instance.

The previous persistent-server run proved that process startup was no longer the hidden cost, but `server_version_ms` still consumed about 25 seconds across seven wrapper turns. This run tests whether caching the version identity removes that repeated wrapper tax.

## Raw Results

- `raw/20260603T021001Z-gpt-oss-20b-mxfp4-printtestbot-printing-press-workflow-large-prefix-16kb-flashcache-wrapper.json`
- `raw/20260603T021105Z-gpt-oss-20b-mxfp4-printtestbot-printing-press-workflow-large-prefix-32kb-flashcache-wrapper.json`
- `raw/20260603T021221Z-gpt-oss-20b-mxfp4-printtestbot-printing-press-workflow-large-prefix-64kb-flashcache-wrapper.json`

## Headline Results

| Fixture | Prefix bytes | Direct prompt ms | Wrapper prompt ms | Delta | Ratio | Hit rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 16 KB | 16,402 | 4,308.069 | 1,875.669 | 2,432.400 | 56.5% | 85.7% |
| 32 KB | 32,786 | 7,217.569 | 2,096.418 | 5,121.151 | 71.0% | 85.7% |
| 64 KB | 65,554 | 13,782.102 | 2,475.412 | 11,306.690 | 82.0% | 85.7% |

## Boundary Timing Comparison

| Fixture | Previous wrapper wall ms | New wrapper wall ms | Previous server version ms | New server version ms |
| --- | ---: | ---: | ---: | ---: |
| 16 KB | 31,468.648 | 9,909.417 | 25,270.727 | 3,581.485 |
| 32 KB | 34,423.260 | 13,327.631 | 24,973.971 | 3,532.332 |
| 64 KB | 42,112.979 | 20,682.871 | 25,230.780 | 3,538.058 |

## Interpretation

Caching server-version identity worked. The wrapper now pays the llama.cpp version subprocess cost once per benchmark fixture instead of once per wrapper turn.

The cache-value story is unchanged and slightly clearer: Flashcache still saves more absolute prompt-processing time as reusable prefix size grows, while wrapper wall time is no longer dominated by repeated binary introspection.

The next bottleneck is the first cache miss: priming the large reusable prefix still costs 2.7s at 16 KB, 5.4s at 32 KB, and 11.6s at 64 KB. The next useful design step is to separate cold cache-fill cost from hot cache-hit turns and build the benchmark around an agent session that already has the stable prefix slot on disk.

Summarize with:

```bash
python3 benchmarks/summarize_results.py benchmarks/datasets/printtestbot-server-version-cache-2026-06-03/raw
```
