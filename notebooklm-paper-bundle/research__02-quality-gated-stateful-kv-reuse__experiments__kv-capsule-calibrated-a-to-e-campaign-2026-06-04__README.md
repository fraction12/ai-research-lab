# KV Capsule Calibrated A-to-E Campaign - 2026-06-04

## Result

The calibrated A-to-E campaign completed with exit code 0, but stopped at Phase A. All six 10-row full-visible calibration variants failed promotion, so no retrieval unit was frozen for capsule evidence.

This is a benchmarkability/model-protocol boundary for the pinned native GPT-OSS direct C API route. It is not evidence against restored KV capsules: Phase B live/restored controls did not run, Phase C scale search did not advance, Phase D amortization was not interpretable, and Phase E agent-context was gated off.

## Phase A Calibration

Promotion rule: full-visible semantic match 10/10 and exact-or-normalized 10/10.

Best attempt: `tsv_value_only_v1` with `5/10` semantic matches and `0/10` exact-or-normalized matches.

| Variant | Prompt Shape | Semantic | Exact/Norm | Promoted |
| --- | --- | ---: | ---: | --- |
| `kv_block_value_only_v1` | `compact_key_value_blocks` | 3/10 | 3/10 | false |
| `equals_line_value_only_v1` | `equals_line_records` | 0/10 | 0/10 | false |
| `answer_channel_v1` | `answer_channel_records` | 0/10 | 0/10 | false |
| `tsv_value_only_v1` | `two_column_tsv` | 5/10 | 0/10 | false |
| `jsonl_value_only_v1` | `jsonl_objects` | 1/10 | 0/10 | false |
| `natural_fact_value_only_v1` | `compact_natural_language_facts` | 0/10 | 0/10 | false |

## Phase Status

- Phase A: completed, no variant promoted at 10 rows.
- Phase B: not run because no retrieval unit was promoted.
- Phase C: not run because the retrieval evidence ladder did not run.
- Phase D: not run because no restored-capsule-passing unit exists.
- Phase E: not run because retrieval restored-capsule pass was the precondition.

## Interpretation

The earlier Family 1 and Family 2 positives remain valid for simple codeword and small structured retrieval. This campaign shows that the current calibrated A-to-E retrieval instrument still cannot produce a boringly reliable full-visible baseline at 10 rows under the pinned native route and generation protocol. The next useful work is native prompt/generation protocol calibration, not broader capsule claims.

## Artifacts

Committed sanitized summaries are in this directory. Prompt-bearing raw records, responses, console logs, runner scripts, and diagnostics are ignored under:

`research/01-ssd-native-inference-current/benchmarks/kv-capsule-calibrated-a-to-e-campaign-2026-06-04/raw/`
