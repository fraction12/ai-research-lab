# KV Capsule Family 3 Mini-Graph Gate

Date: 2026-06-04

## Decision

`family3_stage_a_full_visible_guard_failed`

The Family 3 run stopped at the first hard stop rule. Stage A native full-visible one-hop mini-graph retrieval contained the expected answer for 2 of 3 cases, so the positive guard did not pass.

## Scores

| Stage | Control | Answer-contained | Exact-only | Interpretation |
| --- | --- | ---: | ---: | --- |
| Stage A | `native_full_visible_prefix_plus_tail` | 2/3 | 0/3 | positive guard failed |
| Stage A | `native_fresh_tail_only` | not run | not run | blocked by full-visible guard |
| Stage A | `native_live_append_tail_only` | not run | not run | blocked by full-visible guard |
| Stage A | `native_restored_capsule_append_tail_only` | not run | not run | blocked by full-visible guard |
| Stage B | all controls | not run | not run | blocked by Stage A full-visible guard |

## Interpretation

This is not a restored-capsule failure. The model/native prompt route failed the full-visible positive control for one Stage A one-hop mini-graph case, so live append and restored capsule semantics are uninterpretable for this run.

This is useful boundary evidence: after Family 1 codeword and Family 2 structured retrieval passed, the first mini-graph bridge exposed a prompt/model/full-visible limitation before the capsule mechanism could be tested.

## Raw Evidence

Prompt-bearing raw artifacts are ignored under:

```text
research/01-ssd-native-inference-current/benchmarks/kv-capsule-family3-mini-graph-gate-2026-06-04/raw/
```

## Stop Rule

The run stopped after `family3_stage_a_full_visible_guard_failed`. Fresh-tail, live-append, restored-capsule, Stage B, GraphWalks, noiseless evidence, server bridge, and broad benchmarks were not run.
