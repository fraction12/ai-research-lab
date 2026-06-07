# Staged Model-Run Analysis

Date: 2026-06-05

## Staged Path

The experiment did not start clean. The first model-bearing smoke failed because the adapter treated Gemma's tool intent as a final answer instead of running a host-mediated Code-mode loop. That was a protocol failure, not capsule evidence.

The repaired runner introduced a bounded `EXEC -> EXEC_RESULT -> FINAL` loop, hidden-catalog execution, model-authored result rejection, and host-answer finalization. A later two-case smoke passed the required controls.

The first 12-case v8 run then exposed a narrower bridge issue: Gemma emitted near-template names such as `max_failure_modulo` instead of canonical `max_failure_module`. Full-visible, native live append, and restored capsule failed identically on `parallel_aggregation-08`, which pointed to adapter brittleness rather than restored-state divergence.

The v9 runner normalized observed compiled-template aliases, recorded canonical template/alias telemetry, and flushed JSONL after each row. A targeted rerun of `parallel_aggregation-08` passed the core controls, then the full 12-case and 30-case runs passed the Code-mode/KV core.

## Thirty-Case Result

Decision: `thirty-case-v9_passed_core_with_secondary_gap`.

- `code_mode_full_visible`: 30/30 gate, 30/30 answer.
- `code_mode_native_live_append`: 30/30 gate, 30/30 answer.
- `code_mode_restored_kv_capsule`: 30/30 gate, 30/30 answer.
- `code_mode_fresh_tail_only`: 30/30 negative gate, 0/30 answer.
- `code_mode_wrong_capsule_negative`: 30/30 negative gate, 0/30 answer.
- Live/restored hash parity: 30/30 for generated token, normalized response, and response hashes.

Secondary baselines:

- `direct_full_visible_tools`: 19/30 gate, 23/30 answer.
- `compact_visible_evidence_code_mode`: 11/30 gate, 11/30 answer.

## Failure Interpretation

No core Code-mode/KV failures remained in v9.

Direct-tool failures cluster in bounded retry and trace continuation, with additional tool-path mismatches in policy and trace cases. That supports the runtime-harness framing: direct visible tool schemas can be a brittle surface for Gemma 4 on local-agent loops.

Compact visible evidence failures cluster in dependent multi-tool, parallel aggregation, bounded retry, and trace continuation. That means small visible summaries are not an adequate substitute for the stable hidden prefix/capsule on these task families.

The remaining claim boundary is external validity: this is a controlled fixture suite. The next benchmark must test non-handmade task sources before the result can become a paper-scale claim.
