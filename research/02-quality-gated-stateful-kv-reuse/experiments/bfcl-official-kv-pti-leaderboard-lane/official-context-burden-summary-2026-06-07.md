# Official BFCL Context-Burden Summary - 2026-06-07

## Scope

This summary covers the initial full BFCL non-live official-evaluator run used in the paper-site comparison table.

- Run label: `bfcl-official-full-nonlive-kv-pti-per-case-v1`
- Model/runtime label: `gemma4-kv-capsule-pti`
- Model profile: `gemma4-12b`
- Records: `1390`
- Source record file on DushyantPC: `C:\ai\bfcl-official-smoke\research\02-quality-gated-stateful-kv-reuse\experiments\bfcl-official-kv-pti-leaderboard-lane\raw\bfcl-official-full-nonlive-kv-pti-per-case-v1-model-loop-records.jsonl`

## Prompt-Size Telemetry

These values come from the `prompt_sizes` fields in the matching full official model-loop records.

| Metric | Total | Mean per record |
| --- | ---: | ---: |
| Fresh visible task-tail tokens after restore | 45,332 | 32.61 |
| Stable-prefix tokens represented by the capsule | 159,883 | 115.02 |
| Full-prompt-equivalent tokens | 205,215 | 147.64 |
| Visible evidence tokens | 0 | 0.00 |

## Boundary

This is the context-burden telemetry for the initial full official BFCL non-live run. It replaces the earlier repeated-work-stream value in the BFCL reference comparison table.
