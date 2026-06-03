# GraphWalks Repair Mechanism Ladder

Date: 2026-06-03

This experiment extends the first six-case Track 02 GraphWalks ladder with mechanism and repair controls.

## Scope

Fixed case set: `graphwalks-6`, `graphwalks-9`, `graphwalks-11`, `graphwalks-13`, `graphwalks-16`, and `graphwalks-19`.

No broad benchmarks were run.

## Main Result

Every live control had 0/6 pass rate.

The most important new result is that `live-tail` no-restore also failed 0/6. That means the collapse appears before disk save/restore; it is not primarily explained by slot-file restore or SSD/runtime storage behavior.

## Repair Signal

Prompt-level anchor recompute proxies did not fully repair any case:

| Control | Pass rate | Mean score |
| --- | ---: | ---: |
| `live_tail` | 0/6 | 0.0 |
| `query_visible_graph_hidden` | 0/6 | 0.0 |
| `anchor_recompute_64` | 0/6 | 0.0909 |
| `anchor_recompute_128` | 0/6 | 0.1111 |
| `anchor_recompute_256` | 0/6 | 0.4202 |
| `graph_and_query_visible_tail` | 0/6 | 0.0 |
| `graph_and_query_visible_session_format` | 0/6 | 0.0 |

The 256-token anchor provides partial evidence that visible anchors can move the model toward the answer, but it is not a correctness-safe repair.

## Interpretation

For this model/protocol stack, GraphWalks-style reasoning-over-prefix tasks should fall back to full-prompt execution. The next useful mechanism work would be either a lower-level KV/layer selective recompute control or a different same-backend model/format control, not broader benchmarking yet.

## Artifacts

- `summary.json`: aggregate results, timings, artifact hashes, and findings.
- `repair-outcomes.json`: one row per case/control.
- `failure-classifications.json`: updated mechanism classifications.
- `fallback-policy.md`: conservative policy for the fixed six cases.
- `commands.md`: exact commands.
- `model-info.json`: machine, model, backend, and run parameters.
- `prior-art-mechanism-map.md`: paper/system map for the mechanism interpretation.
- `artifact-manifest.json`: input and raw artifact hashes and paths.
- `control-feasibility.md`: control coverage and harness-change note.
