# GraphWalks Parents Scaling Pilot - 2026-06-04

This is a controlled Track 02 pilot for GraphWalks `parents`, not a broad benchmark.

The OpenSpec planned a deterministic 50-case cohort and five controls per case. The full 50x5 matrix would require 250 local GPT-OSS model calls; the first-10 slice took 2504.6s, so the stop rule was triggered and this run reports the deterministic first 10 cases only.

## Result

| Control | Passes | Mean F1 |
| --- | ---: | ---: |
| `full_visible_compact_prompt` | 1/10 | 0.415 |
| `hidden_prefix_session_tail` | 0/10 | 0.000 |
| `hidden_prefix_compact_tail_no_evidence` | 0/10 | 0.000 |
| `hidden_prefix_compact_visible_evidence_tail` | 7/10 | 0.801 |
| `fresh_compact_visible_evidence_only` | 7/10 | 0.801 |

## Interpretation

Compact visible evidence repaired 7/10 hidden-prefix failures, while compact no-evidence repaired 0/10. However, fresh compact evidence-only matched hidden-prefix plus compact evidence on all 10 cases by exact response string and score.

That means this slice supports role-aware evidence scheduling / token-efficient context compilation. It does not show a material hidden-KV correctness contribution for GraphWalks `parents` in this control setup.

Full-visible compact prompt underperformed compact evidence-only. Treat this as a pilot signal for retrieval-burden reduction, not as a general GraphWalks quality claim.

## Failure Notes

The three compact visible-evidence misses were not session/cache-specific:

- `graphwalks-parent-001-row-1`: both evidence controls produced a malformed abbreviated node id (`c81e...`).
- `graphwalks-parent-007-row-7`: both evidence controls abbreviated one node (`e4da3`).
- `graphwalks-parent-009-row-9`: both evidence controls produced truncated invalid JSON at the 192-token cap.

## Artifact Layout

Prompt-bearing raw inputs and outputs are under ignored Track 01 paths listed in `artifact-manifest.json`. Committed Track 02 summaries are in this directory.
