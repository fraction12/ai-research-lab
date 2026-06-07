# Official BFCL Evaluator Summary - 2026-06-07

## Scope

This summary covers the first full non-live BFCL candidate prediction run for the disclosed custom runtime:

- Model/runtime label: `gemma4-kv-capsule-pti`
- Runtime: Gemma 4 with per-case restored llama.cpp KV/sequence-state capsule plus PTI output contract
- Dataset scope: BFCL V4 non-live categories
- Scoreable records: 1390
- Run status: candidate prediction generation completed; official BFCL evaluator run completed locally against exported predictions

## Evaluator Setup

The official evaluator was run in an isolated Python 3.11 environment because Python 3.14 dependency resolution failed for the BFCL package on DushyantPC.

- Package: `bfcl-eval==2025.12.17`
- Extra dependency needed for CLI import: `soundfile`
- Export source: copied from DushyantPC `official-export/result/gemma4-kv-capsule-pti/non_live/`
- Local evaluator root: `/tmp/bfcl-official-eval-run/official-export`

The official BFCL CLI rejected the custom model key until a local evaluator-only `MODEL_CONFIG_MAPPING["gemma4-kv-capsule-pti"]` entry was added. This shim only lets the evaluator recognize the pre-generated result directory; it does not alter predictions or scorer logic.

## Export Fix Required

The first evaluator attempt exposed an exporter ID bug in the simple categories:

- Exported internal adapter IDs: `simple_0`, `java_0`, `javascript_0`
- Official BFCL expected IDs: `simple_python_0`, `simple_java_0`, `simple_javascript_0`

The evaluator copy was corrected before scoring. The source exporter now maps these adapter aliases to official BFCL IDs.

## Official BFCL Evaluator Scores

From `bfcl evaluate` on the seven non-live categories:

| Category | Correct | Total | Accuracy |
| --- | ---: | ---: | ---: |
| simple_python | 324 | 400 | 81.00% |
| simple_java | 42 | 100 | 42.00% |
| simple_javascript | 33 | 50 | 66.00% |
| multiple | 171 | 200 | 85.50% |
| parallel | 133 | 200 | 66.50% |
| parallel_multiple | 129 | 200 | 64.50% |
| irrelevance | 137 | 240 | 57.08% |
| non-live overall | 969 | 1390 | 69.88% |

BFCL's `data_overall.csv` reports `Overall Acc` as `9.84%` because unevaluated live, multi-turn, web-search, memory, and format-sensitivity categories are counted as zero/empty in the overall table. The appropriate result for this run is the non-live score: `69.88%`.

## Interpretation

This is now an official-evaluator score for the exported non-live candidate predictions, not merely the local runner gate.

It still is not a public leaderboard submission. Any leaderboard discussion must disclose:

- Custom inference harness
- Restored hidden KV/sequence state
- Per-case hidden BFCL function catalog
- PTI contract
- Evaluator-only model-key shim used to score pre-generated predictions

## Immediate Follow-Up

1. Regenerate exports from the fixed exporter so no manual ID correction is needed.
2. Copy official evaluator score artifacts into a stable ignored/archive location or add compact summaries to tracked paper artifacts.
3. Analyze failures by category, with priority on `simple_java`, `irrelevance`, and multi-call ordering/argument normalization errors.
