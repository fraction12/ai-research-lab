# Compact Visible Evidence Repair

Date: 2026-06-04

Machine: DushyantPC

Scope: only `graphwalks-16` and `graphwalks-19`, the two remaining failures from `visible-evidence-slice-repair-2026-06-04`.

## Result

Compact-answer visible evidence repaired both remaining cases at the same `--predict 192` cap.

Focused six-case chain:

```text
hidden-prefix/session-tail:          0/6
visible evidence tail:               4/6
compact visible evidence tail:       6/6
```

This is a focused mechanism result, not a broad benchmark.

| Case | Previous visible score | Compact score | Prompt tokens | Predicted tokens | Evidence edges | Evidence bytes | Repaired |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `graphwalks-16` | 0.0 | 1.0 | 205 | 47 | 6 | 149 | yes |
| `graphwalks-19` | 0.0 | 1.0 | 178 | 31 | 4 | 99 | yes |

## Interpretation

The two remaining failures were prompt-protocol / verbosity failures. The evidence content was unchanged, the hidden-prefix mechanics were unchanged, and the model/runner/settings were unchanged. The compact tail made GPT-OSS emit the final node list directly instead of explaining until the JSON answer truncated.

This supports role-aware context compilation / quality-gated context scheduling: hidden state alone failed, visible evidence repaired most cases, and compact answer scheduling repaired the rest. It does not prove pure KV reuse and it does not claim general GraphWalks quality.
