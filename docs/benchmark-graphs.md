# Benchmark Graphs

Date: 2026-06-03

These graphs summarize what the current Printy / Print-a-Bot benchmark data says about Flashcache and SSD-backed prompt or KV state.

For a browser-friendly version, open [Benchmark Graphs HTML](benchmark-graphs.html).

The charts are generated with Matplotlib from the raw JSON files under:

- `benchmarks/datasets/printtestbot-printing-press-2026-06-02/raw/`
- `benchmarks/datasets/printtestbot-large-prefix-2026-06-02/raw/`

Regenerate them with:

```bash
python3 -m pip install -r requirements-dev.txt
python3 benchmarks/plot_benchmark_graphs.py
```

Each chart is exported as SVG, PDF, and PNG under `docs/assets/benchmark-graphs/`.

## What We Learned

1. Warm local agent loops are much cheaper than restarted local agent loops.
2. Exact prompt replay is already easy; it is not the interesting product claim.
3. On the small 5.5KB reusable prefix, the tiny Gemma model shows a big cache win, but `gpt-oss-20b` direct slot restore is basically flat.
4. The Flashcache wrapper gives a repeatable `gpt-oss-20b` win around 12% on the small Printy prefix.
5. With larger stable prefixes, Flashcache wrapper savings stay around 13%, but the absolute saved time grows from about 2.7s to 11.4s across seven turns.
6. Saved slot files get large quickly, so the next layer needs partial restore, better layout, and I/O instrumentation instead of whole-slot blobs forever.

## Warm vs Restarted

![Warm vs restarted Ollama benchmark](assets/benchmark-graphs/ollama-warm-vs-restarted.svg)

The strongest current signal is the persistence gap. Ollama keeps changed-tail prompts warm while the model stays loaded, but restarts lose much of that benefit.

For the seven-turn Printy workflow:

- warm prompt eval sum: `4.43s`
- restarted prompt eval sum: `10.46s`
- restarted prompt eval was `2.36x` warm
- restarted total request time was `48.11s` versus `15.46s` warm

This is the opening for persistent SSD-backed state. The goal is to keep useful prefix/KV state alive across cold or restarted sessions.

## Exact Replay Control

![Exact replay control](assets/benchmark-graphs/ollama-exact-repeat-control.svg)

Exact replay gets cheap: the second identical Ollama prompt dropped from about `462ms` prompt eval to `74ms`.

That proves a known primitive, not our deeper thesis. Real agent work is changed-tail reuse: the stable prefix repeats, but command output, diffs, tool results, and planner state keep changing.

## Small Prefix Cache Outcomes

![Small prefix cache outcomes](assets/benchmark-graphs/small-prefix-cache-outcomes.svg)

On the original Printy fixture with a 5.5KB reusable prefix:

- Gemma slot restore saved `53.7%`.
- Gemma Flashcache saved `60.3%`.
- `gpt-oss-20b` direct slot restore averaged only `0.8%`.
- `gpt-oss-20b` Flashcache wrapper averaged `12.2%`.

Interpretation: cache mechanics work, but the bigger model/backend does not automatically turn whole-slot restore into a large win at this prefix size. The wrapper path is better, but the result says we need deeper timing around restore, prefill, copy/upload, and tail handling.

## Large Prefix Ladder

![Large prefix Flashcache ladder](assets/benchmark-graphs/large-prefix-flashcache-ladder.svg)

The large-prefix ladder is closer to the future local-agent problem: long stable repo/tool/session context plus small changing tails.

For `gpt-oss-20b` over seven turns:

| Reusable prefix | Direct prompt eval | Flashcache prompt eval | Saved |
| --- | ---: | ---: | ---: |
| 16KB | 19.81s | 17.09s | 2.71s |
| 32KB | 38.62s | 33.68s | 4.94s |
| 64KB | 81.95s | 70.56s | 11.39s |

The percentage win is steady around 13%, but the absolute win grows with prefix size. That supports the direction: local agent workloads get interesting when reusable context becomes large and persistent.

## SSD Cost

![Slot file size ladder](assets/benchmark-graphs/slot-file-size-ladder.svg)

The cost side is obvious too. Whole-slot files are big:

| Reusable prefix | Slot file |
| --- | ---: |
| 5.4KB | 31.1MB |
| 16.0KB | 94.5MB |
| 32.0KB | 184.8MB |
| 64.0KB | 361.0MB |

This is why the next Flashcache layer should not stop at whole-slot blobs. We need block layout, partial restore, cache eviction, and I/O telemetry.

## Gains Projection

![Flashcache gains projection](assets/benchmark-graphs/flashcache-gains-projection.svg)

The projection figure combines the measured large-prefix ladder with the next research target. The 128KB point is a directional linear projection from the measured 16KB, 32KB, and 64KB results, not a measured benchmark result.

The current projection is:

- measured 64KB savings: `11.4s` across seven turns
- projected 128KB savings: `23.0s` across seven turns
- next metal target: about `25%` savings from partial KV restore, prefetch, and better layout

## Next Graphs To Add

- prefill vs restore vs save time
- SSD read/write bytes and throughput
- GPU or accelerator upload time, if observable
- tail-only prefill time after restored prefix
- quality or next-action agreement against uncached baseline

The current data says Flashcache is worth taking deeper, but the next round must explain where the time goes.
