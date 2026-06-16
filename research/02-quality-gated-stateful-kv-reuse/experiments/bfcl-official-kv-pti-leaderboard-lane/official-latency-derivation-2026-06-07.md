# Official BFCL Latency Derivation - 2026-06-07

## Scope

This note records the latency values used for the custom local `Gemma 4 12B + KV Capsule + PTI` row in the paper-site BFCL reference table.

- Run label: `bfcl-official-full-nonlive-kv-pti-per-case-v1`
- Model/runtime label: `gemma4-kv-capsule-pti`
- Records: `1390`
- Source record file on DushyantPC: `C:\ai\bfcl-official-smoke\research\02-quality-gated-stateful-kv-reuse\experiments\bfcl-official-kv-pti-leaderboard-lane\raw\bfcl-official-full-nonlive-kv-pti-per-case-v1-model-loop-records.jsonl`

## Reported Values

| Metric | Value | Derivation boundary |
| --- | ---: | --- |
| Measured mean latency per generated record | `13.0 s` | Mean per-record model-loop latency over `1390` generated records. |
| Amortized mean latency per generated record | `12.6 s` | Recomputed from the same model-loop records by charging stable-prefix capsule build cost once per non-live source-category family. |
| Model-loop wall-clock window | `2026-06-07T08:11:52Z` to `2026-06-07T13:12:11Z` | Metadata from the raw model-loop run. |
| Total wall-clock window | `5.01 h` | End timestamp minus start timestamp before local evaluator scoring. |

## Amortization Method

The amortized value starts from the raw model-loop records and treats `initial_prompt_eval_ms + capsule_save_ms` as a stable-prefix capsule build cost. That build cost is charged once per non-live source-category family rather than once per generated record, then removed from the remaining rows in that family.

This reflects the runtime setting KV Capsules target: repeated task tails sharing fixed prompt/protocol context. It is not a hosted BFCL serving metric, not a dollar-cost estimate, and not directly comparable to hosted-provider latency accounting.

## Reproducibility Boundary

The compact paper repository now commits the derived values and the source-file pointer, but the raw Windows JSONL listed above is not present in this checkout. Re-auditing the arithmetic from raw rows requires that raw model-loop file.
