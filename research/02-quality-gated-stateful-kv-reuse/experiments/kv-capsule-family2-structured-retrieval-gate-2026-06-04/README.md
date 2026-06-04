# KV Capsule Family 2 Structured-Retrieval Gate

Date: 2026-06-04

## Decision

`family2_restored_capsule_structured_retrieval_passed`

The 5-case fabricated structured-retrieval Family 2 gate passed through all ordered controls. Native full-visible contained the requested values, fresh tail-only missed, native live append contained the values, and restored capsule append contained the values.

## Scores

| Control | Answer-contained | Exact-only | Interpretation |
| --- | ---: | ---: | --- |
| `native_full_visible_prefix_plus_tail` | 5/5 | 0/5 | positive structured-retrieval guard passed |
| `native_fresh_tail_only` | 0/5 | 0/5 | negative control missed as expected |
| `native_live_append_tail_only` | 5/5 | 0/5 | live append structured retrieval passed |
| `native_restored_capsule_append_tail_only` | 5/5 | 0/5 | restored capsule structured retrieval passed |

Exact-only output did not pass; responses contained extra explanatory text. The semantic gate uses answer-contained scoring, consistent with the Family 1 and native/server parity scoring rules.

## Interpretation

This is a positive restored-capsule semantic continuation result for a small structured-retrieval mechanism gate. It shows the native C API save/restore path can preserve enough prefix state for five fabricated key-value/table lookup cases where the answer is hidden in the prefix and not resent in the tail.

This does not prove mini-graph behavior, GraphWalks correctness, long-prefix reasoning, noiseless evidence repair, or broad benchmark quality.

## Raw Evidence

Prompt-bearing raw artifacts are ignored under:

```text
research/01-ssd-native-inference-current/benchmarks/kv-capsule-family2-structured-retrieval-gate-2026-06-04/raw/
```

## Stop Rule

The run stopped after restored capsule passed. Family 3, mini graph, GraphWalks, noiseless evidence, server bridge, and broad benchmarks were not run.
