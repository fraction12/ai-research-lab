## Context

Fixed source-of-truth base:

```text
commit: 4404939 Record KV capsule Family 2 gate
family1 decision: family1_restored_capsule_semantic_passed
family2 decision: family2_restored_capsule_structured_retrieval_passed
native route: python ctypes direct libllama C API against pinned b9493/GPT-OSS bundle
canonical route: full prompt/prefix prefill add_special=true; appended tail add_special=false
```

Family 2 showed restored capsule semantic continuation for five fabricated structured-retrieval key-value/table cases:

- `native_full_visible_prefix_plus_tail`: 5/5 answer-contained
- `native_fresh_tail_only`: 0/5 answer-contained
- `native_live_append_tail_only`: 5/5 answer-contained
- `native_restored_capsule_append_tail_only`: 5/5 answer-contained

Family 3 keeps the same runtime abstraction but changes the prefix content from a table to a tiny invented relation graph. It is intentionally below GraphWalks complexity and splits one-hop retrieval from two-hop path retrieval so failures can be classified precisely.

## Goals / Non-Goals

**Goals:**

- Test whether a restored native state capsule can preserve a tiny hidden relation graph for tail-only graph queries.
- Separate Stage A one-hop relation retrieval from Stage B two-hop path retrieval.
- Preserve ordered controls and hard stop rules so restored capsule semantics are interpreted only after full-visible and live-append guards pass for the current stage.
- Record answer-contained and exact-only scoring separately.
- Preserve exact commands, model/backend metadata, token counts, timings, state byte counts, and hashes in sanitized summaries.
- Keep raw prompt text, responses, expected answer strings, token IDs, generated token slices, top-k arrays, and state bytes out of committed artifacts.

**Non-Goals:**

- Do not run GraphWalks, noiseless evidence repair, server bridge, Family 4, or broad benchmarks.
- Do not import historical GraphWalks cases.
- Do not change the pinned model/backend route unless the full-visible guard forces a documented route-change stop.
- Do not claim broad graph-reasoning correctness, long-prefix correctness, or paper-level correctness from this 5-case gate.
- Do not modify tracked Track 01 harness code.

## Research Question

Can a native direct C API session save and restore a tiny relation-graph prefix state capsule such that:

```text
restore(capsule(mini_graph_prefix)) + append(graph_query_tail)
```

is semantically equivalent to:

```text
mini_graph_prefix + graph_query_tail
```

without resending the graph prefix text in the tail request?

## Task Shape

Use 5 deterministic fabricated mini-graph cases total:

- Stage A: 3 one-hop edge retrieval cases. The prefix contains invented nodes and relation labels with distractor edges. The tail asks for the exact node/value reached by one relation from a source node.
- Stage B: 2 two-hop tiny path cases. The prefix contains invented nodes and relation labels with distractor edges. The tail asks for the exact node reached by following two named relations from a source node.

The expected answer appears only in the hidden prefix graph, not in the tail. Prompt-bearing graph text stays only in ignored raw artifacts. Committed summaries record stage, hop count, case ids, prompt/content hashes, token counts, answer-contained booleans, exact-only booleans, output status, timings, state byte counts, and classifications.

## Controls

Run controls in this exact order for the current stage:

| Control | Purpose | Advance condition |
| --- | --- | --- |
| `native_full_visible_prefix_plus_tail` | Positive guard that the native route can solve the visible graph prompt. | Must contain the expected answer for all cases in the current stage. |
| `native_fresh_tail_only` | Negative leakage/scorer control. | Must contain 0 expected answers in the current stage; any contained answer stops or quarantines the run. |
| `native_live_append_tail_only` | Same-context prefix prefill, then tail-only append. | Must contain the expected answer for all cases in the current stage before restored capsule can be interpreted. |
| `native_restored_capsule_append_tail_only` | Save prefix state, restore into a fresh context, append tail only. | Main capsule result for the current stage. |

Stage B runs only after Stage A restored capsule passes.

## Metrics

Raw records under ignored paths should include full evidence needed to audit the run. Committed summaries retain only sanitized fields:

- case id, family, stage, hop count, task shape, and control
- prompt, prefix, tail, expected-answer, response, and normalized-response hashes
- exact-match and answer-contained booleans
- output status: `exact_only`, `contains_with_extra_text`, `missing`, or `malformed`
- failure class
- prefix token count, tail token count, full prompt token count, generated token count
- prompt/decode/total timings
- `n_past_before_tail_append`
- `generation_start_pos`
- `final_position`
- state/capsule byte counts and save/restore timings when restored capsule runs
- model, runner, lib, backend, source, hardware, and command metadata

Committed artifacts must not include raw prompts, raw responses, expected answer strings, token ID arrays/slices, generated token arrays/slices, top-k arrays, or state bytes.

## Stop Rules

Stage A:

- If `native_full_visible_prefix_plus_tail` fails any Stage A case, stop as `family3_stage_a_full_visible_guard_failed`; do not interpret live append or restored capsule.
- If `native_fresh_tail_only` contains any Stage A expected answer, stop or quarantine as `family3_stage_a_fresh_tail_leakage_or_scorer_issue`.
- If `native_live_append_tail_only` fails any Stage A case, stop as `family3_stage_a_live_append_protocol_blocker`; do not interpret restored capsule.
- If live append passes and restored capsule fails on Stage A, classify `family3_stage_a_restored_capsule_one_hop_failure` and stop before Stage B.
- If Stage A restored capsule passes, proceed to Stage B.

Stage B:

- If `native_full_visible_prefix_plus_tail` fails any Stage B case, classify `family3_stage_b_full_visible_guard_failed`; do not interpret Stage B live append or restored capsule.
- If `native_fresh_tail_only` contains any Stage B expected answer, stop or quarantine as `family3_stage_b_fresh_tail_leakage_or_scorer_issue`.
- If `native_live_append_tail_only` fails any Stage B case, classify `family3_stage_b_live_append_protocol_blocker`; do not interpret restored capsule.
- If live append passes and restored capsule fails on Stage B, classify `family3_stage_b_restored_capsule_two_hop_failure`.
- If both stages pass restored capsule, classify `family3_restored_capsule_mini_graph_passed` and stop before expansion.

## Artifact Layout

Prompt-bearing raw artifacts stay under ignored Track 01 paths:

```text
research/01-ssd-native-inference-current/benchmarks/kv-capsule-family3-mini-graph-gate-2026-06-04/raw/
```

Committed Track 02 summaries live under:

```text
research/02-quality-gated-stateful-kv-reuse/experiments/kv-capsule-family3-mini-graph-gate-2026-06-04/
```

Required committed files:

```text
README.md
summary.json
case-metrics.json
failure-classifications.json
commands.md
model-info.json
artifact-manifest.json
capsule-contract.md  # only if native_restored_capsule_append_tail_only actually runs
```

If restored capsule is not run, do not create a synthetic capsule contract. Record the missing restored-capsule contract in `summary.json` and `artifact-manifest.json`.

## Risks / Trade-offs

- Mini-graph prompts may expose model reasoning or prompt-protocol weakness rather than capsule weakness. The full-visible guard stops before capsule interpretation.
- Fresh-tail leakage would invalidate the task as hidden-prefix retrieval. The fresh-tail control stops or quarantines that condition.
- Two-hop Stage B may fail even if one-hop Stage A passes; this should be treated as a useful boundary, not rescued by changing the task.
- Exact-only output may fail even when the semantic answer is present. Answer-contained is the semantic metric; exact-only remains a secondary output-discipline metric.
- The pinned GPT-OSS/b9493 route remains ABI-risk by nature of the Python `ctypes` direct API. Family 1 and Family 2 successes reduce but do not remove that risk.

## Migration Plan

Create and validate this OpenSpec change, add ignore coverage for the raw benchmark path, adapt the ignored Family 2 native runner into a Family 3-only runner, run syntax and grep sanity checks locally, report local sanity evidence before sync, sync only necessary ignored runner/worktree state to DushyantPC, run `--mode family3`, copy raw artifacts back, package sanitized Track 02 summaries, run OpenSpec validation, confirm raw ignored status, and commit locally without pushing.
