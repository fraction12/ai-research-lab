# Printtestbot Session Cache Benchmark Dataset

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

This dataset reruns the Printtestbot large-prefix benchmark with `--cache-mode session`.

Session mode prewarms the reusable prefix slot, restores that slot once into a persistent wrapper server, then measures all changed-tail turns without restoring the slot before every turn. It tests whether a restore-once local-agent session can replace the stronger but more expensive restore-every-turn hot-cache path.

## Raw Results

- `raw/20260603T023920Z-gpt-oss-20b-mxfp4-printtestbot-printing-press-workflow-large-prefix-16kb-flashcache-wrapper.json`
- `raw/20260603T024051Z-gpt-oss-20b-mxfp4-printtestbot-printing-press-workflow-large-prefix-32kb-flashcache-wrapper.json`
- `raw/20260603T024242Z-gpt-oss-20b-mxfp4-printtestbot-printing-press-workflow-large-prefix-64kb-flashcache-wrapper.json`

## Headline Results

| Fixture | Context | Prefix bytes | Direct prompt ms | Session prompt ms | Delta | Ratio | Hit rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 16 KB | 8,192 | 16,402 | 4,517.140 | 4,312.205 | 204.935 | 4.5% | 100.0% |
| 32 KB | 16,384 | 32,786 | 7,316.808 | 7,225.688 | 91.120 | 1.2% | 100.0% |
| 64 KB | 32,768 | 65,554 | 13,760.647 | 13,807.604 | -46.957 | -0.3% | 100.0% |

## Session Setup Read

| Fixture | Session setup wall ms | One-time restore ms | Slot file bytes |
| --- | ---: | ---: | ---: |
| 16 KB | 20,795.213 | 38.073 | 94,310,428 |
| 32 KB | 21,122.299 | 71.123 | 184,636,844 |
| 64 KB | 20,705.990 | 147.963 | 360,863,116 |

The setup wall includes starting the persistent server and reading server identity. The one-time slot restore itself is much smaller.

## Per-Turn Finding

The first measured session turn still reprocessed the full prompt:

| Fixture | First session prompt ms | First session prompt tokens | Later prompt token range |
| --- | ---: | ---: | ---: |
| 16 KB | 2,756.506 | 3,840 | 132-153 |
| 32 KB | 5,461.731 | 7,513 | 132-153 |
| 64 KB | 11,735.198 | 14,678 | 132-153 |

Later turns became cheap because the running server had in-session prompt state after the first measured full prompt.

## Interpretation

This is a useful negative result. Restore-once plus full-prompt replay does not reproduce the hot-cache savings. The session hit rate is 100%, but the first measured full prompt still pays nearly the full prefix cost, so total prompt savings are near zero across seven turns.

The hot-cache dataset is still the stronger proof that restored prefix state can reduce prompt processing. This session dataset says the next layer cannot simply restore once and continue sending full prompts. It likely needs one of these shapes:

- restore the clean prefix before each independent changed-tail turn,
- keep multiple clean/resident prefix slots,
- or send tail-only requests against a restored resident prefix with explicit session semantics.

Summarize with:

```bash
python3 benchmarks/summarize_results.py benchmarks/datasets/printtestbot-session-cache-2026-06-03/raw
```
