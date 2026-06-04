# KV Capsule Family 1 Semantic Gate

Date: 2026-06-04

## Decision

`family1_restored_capsule_semantic_passed`

The 3-case simple codeword Family 1 gate passed through all ordered controls. Native full-visible contained the codeword, fresh tail-only missed, native live append contained the codeword, and restored capsule append contained the codeword.

## Scores

| Control | Answer-contained | Exact-only | Interpretation |
| --- | ---: | ---: | --- |
| `native_full_visible_prefix_plus_tail` | 3/3 | 0/3 | positive guard passed |
| `native_fresh_tail_only` | 0/3 | 0/3 | negative control missed as expected |
| `native_live_append_tail_only` | 3/3 | 0/3 | live append semantics passed |
| `native_restored_capsule_append_tail_only` | 3/3 | 0/3 | restored capsule semantics passed |

Exact-only output did not pass; responses contained extra explanatory text. The semantic gate uses answer-contained scoring, consistent with the prior bridge and sanity-probe scoring rules.

## Interpretation

This is the first positive restored-capsule semantic continuation result for Track 02, but only for the narrow Family 1 simple codeword mechanism gate. It should not be generalized to GraphWalks, evidence scheduling, or broad benchmark quality.

## Raw Evidence

Prompt-bearing raw artifacts are ignored under:

```text
research/01-ssd-native-inference-current/benchmarks/kv-capsule-family1-semantic-gate-2026-06-04/raw/
```

## Stop Rule

The run stopped after restored capsule passed. Family 2, mini graph, GraphWalks, noiseless evidence, and broad benchmarks were not run.
