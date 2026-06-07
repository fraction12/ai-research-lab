# Printtestbot Large Prefix Benchmark Dataset

Date: 2026-06-02

Machine: DushyantPC

Purpose: test whether Flashcache wrapper savings grow as reusable Printy-style agent context scales from the original ~5.5 KB prefix to 16 KB, 32 KB, and 64 KB prefixes.

Fixture generator:

```text
benchmarks/generate_large_prefix_fixtures.py
```

Generated fixtures:

```text
benchmarks/fixtures/printtestbot-printing-press-workflow-large-prefix-16kb.json
benchmarks/fixtures/printtestbot-printing-press-workflow-large-prefix-32kb.json
benchmarks/fixtures/printtestbot-printing-press-workflow-large-prefix-64kb.json
```

Raw results should be stored under:

```text
benchmarks/datasets/printtestbot-large-prefix-2026-06-02/raw/
```

## Raw Results

- `raw/20260603T003000Z-gpt-oss-20b-mxfp4-printtestbot-printing-press-workflow-large-prefix-16kb-llama-cpp-prompt-cache.json`
- `raw/20260603T003542Z-gpt-oss-20b-mxfp4-printtestbot-printing-press-workflow-large-prefix-16kb-flashcache-wrapper.json`
- `raw/20260603T004209Z-gpt-oss-20b-mxfp4-printtestbot-printing-press-workflow-large-prefix-32kb-llama-cpp-prompt-cache.json`
- `raw/20260603T004836Z-gpt-oss-20b-mxfp4-printtestbot-printing-press-workflow-large-prefix-32kb-flashcache-wrapper.json`
- `raw/20260603T005624Z-gpt-oss-20b-mxfp4-printtestbot-printing-press-workflow-large-prefix-64kb-llama-cpp-prompt-cache.json`
- `raw/20260603T010405Z-gpt-oss-20b-mxfp4-printtestbot-printing-press-workflow-large-prefix-64kb-flashcache-wrapper.json`

## Headline Results

| Fixture | Prefix bytes | Direct slot delta | Flashcache wrapper delta | Wrapper ratio | Hit rate | Slot cache bytes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 16 KB | 16,402 | 224,799.817 ms | 2,714.827 ms | 13.7% | 85.7% | 94,507,164 |
| 32 KB | 32,786 | -168.360 ms | 4,943.916 ms | 12.8% | 85.7% | 184,833,580 |
| 64 KB | 65,554 | 182.939 ms | 11,388.079 ms | 13.9% | 85.7% | 361,035,260 |

The wrapper result is the cleanest product-shaped signal: absolute prompt-processing savings grew with reusable-prefix size while percentage reduction stayed near 13%.

The direct slot benchmark is mechanically useful but noisy. The 16 KB direct run showed a very large restored-prefix gain, while 32 KB and 64 KB were effectively flat. Treat raw slot restore as a backend diagnostic, not the product decision metric.

Summarize with:

```bash
python3 benchmarks/summarize_results.py benchmarks/datasets/printtestbot-large-prefix-2026-06-02/raw
```

Interpretation rule:

- Growing wrapper savings across larger prefixes supports the local-agent reusable-context cache direction.
- Flat savings means the wrapper is useful but not yet a complete SSD-native inference layer.
- Runtime or memory failure means the next design target is adaptive prefix selection and eviction.

Current interpretation: wrapper savings are not flat in absolute terms. Larger reusable prefixes produce larger time savings on DushyantPC, and the 64 KB run completes successfully at `ctx-size 32768`. The next useful experiment is repeated samples and a quality/routing rubric, because prompt timing alone does not prove agent usefulness.
