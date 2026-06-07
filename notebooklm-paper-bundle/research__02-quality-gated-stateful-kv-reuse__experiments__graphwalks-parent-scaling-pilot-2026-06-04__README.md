# GraphWalks Parents Scaling Pilot - 2026-06-04

This is a controlled Track 02 pilot for GraphWalks `parents`, not a broad benchmark. The full deterministic 50-case cohort and five-control matrix completed with the pinned GPT-OSS llama.cpp path.

## Result

| Control | Passes | Mean F1 |
| --- | ---: | ---: |
| `full_visible_compact_prompt` | 3/50 | 0.357 |
| `hidden_prefix_session_tail` | 0/50 | 0.000 |
| `hidden_prefix_compact_tail_no_evidence` | 0/50 | 0.000 |
| `hidden_prefix_compact_visible_evidence_tail` | 27/50 | 0.696 |
| `fresh_compact_visible_evidence_only` | 27/50 | 0.696 |

## Hidden KV Value Check

The hidden-prefix plus compact visible-evidence condition matched fresh compact evidence-only on all 50 cases by exact response string and by score.

| Measure | Value |
| --- | ---: |
| Score-equal pairs | 50/50 |
| Response-string-equal pairs | 50/50 |
| Hidden positive correctness signals | 0 |
| Hidden negative correctness signals | 0 |
| Mean latency delta, hidden minus fresh | 14926.7 ms |
| Mean prompt-token delta, hidden minus fresh | 0.0 |
| Mean prompt-time delta, hidden minus fresh | 486.9 ms |

Interpretation: this full 50-case pilot shows no observable correctness value from hidden KV/session state beyond the visible evidence slice. The useful mechanism is role-aware evidence scheduling / token-efficient context compilation. Hidden-prefix/session mechanics add slot/cache setup work and latency in this runner path.

## Evidence Sufficiency

Evidence extraction used only the graph prefix and requested target node. Reference parent sets were used only after extraction to measure sufficiency. The sufficiency report separates recall coverage from exact/no-extra source-set match. The extracted evidence contained all reference parents for 50/50 cases. It was an exact source-set match for 33/50 cases; the other 17 cases included an extra target self-loop source, so the slice was recall-sufficient but noisy.

## Slot/Cache Telemetry

Slot/cache telemetry was captured for hidden-prefix controls through llama.cpp slot save/restore responses. Fresh evidence-only controls have slot telemetry marked unavailable because no hidden prefix is used.

Key hidden+evidence means:

- prime prompt tokens: 1024.9
- prime prompt ms: 14173.6
- setup wall ms: 14235.6
- save ms: 21.0
- restore ms: 21.5

## Failure Notes

Compact visible evidence repaired many hidden-prefix failures, but the same repairs occurred with fresh evidence-only. Remaining misses are therefore not session/cache-specific in this setup; they are model/prompt-protocol failures over a sufficient compact evidence slice, including malformed abbreviated node ids and JSON truncation/parse failures.

## Artifact Layout

Prompt-bearing raw inputs and outputs are under ignored Track 01 paths listed in `artifact-manifest.json`. Committed Track 02 summaries are in this directory.
