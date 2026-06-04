## Context

Fixed source-of-truth base:

```text
commit: 382e677 Record KV capsule Family 1 gate
family1 decision: family1_restored_capsule_semantic_passed
native route: python ctypes direct libllama C API against pinned b9493/GPT-OSS bundle
canonical route: full prompt/prefix prefill add_special=true; appended tail add_special=false
```

Family 1 showed restored capsule semantic continuation for a simple codeword mechanism gate:

- `native_full_visible_prefix_plus_tail`: 3/3 answer-contained
- `native_fresh_tail_only`: 0/3 answer-contained
- `native_live_append_tail_only`: 3/3 answer-contained
- `native_restored_capsule_append_tail_only`: 3/3 answer-contained

Family 2 keeps the same runtime abstraction but raises the prefix task from a single codeword sentence to a compact fabricated structured prefix. Each case contains multiple key-value facts or a tiny table, and the tail asks for one exact value by key or row. The answer must be present only in the prefix.

## Goals / Non-Goals

**Goals:**

- Test whether a restored native state capsule can preserve a small structured prefix for tail-only retrieval.
- Preserve ordered controls and hard stop rules so restored capsule semantics are interpreted only after full-visible and live-append guards pass.
- Record answer-contained and exact-only scoring separately.
- Preserve exact commands, model/backend metadata, token counts, timings, state byte counts, and hashes in sanitized summaries.
- Keep raw prompt text, responses, token IDs, generated token slices, top-k arrays, and state bytes out of committed artifacts.

**Non-Goals:**

- Do not run Family 3, mini graph, GraphWalks, noiseless evidence, server bridge, or broad benchmarks.
- Do not change the pinned model/backend route unless the full-visible guard forces a documented route-change stop.
- Do not claim general KV capsule correctness or GraphWalks correctness from this 5-case gate.
- Do not modify tracked Track 01 harness code.

## Research Question

Can a native direct C API session save and restore a compact structured prefix state capsule such that:

```text
restore(capsule(structured_prefix)) + append(query_tail)
```

is semantically equivalent to:

```text
structured_prefix + query_tail
```

without resending the structured prefix text in the tail request?

## Task Shape

Use 5 deterministic structured-retrieval cases. Each case will use fabricated names/keys/values and a compact prefix containing several facts, such as:

- multiple `key = value` rows
- a compact table with row identifiers and values
- at least one distractor value near the requested row or key

The tail asks for one exact value by key/row. The tail must not contain the answer value. Prompt-bearing text stays only in ignored raw artifacts. Committed summaries record case ids, prompt/content hashes, token counts, answer-contained booleans, exact-only booleans, output status, timings, state byte counts, and classifications.

## Controls

Run controls in this exact order across the same 5 deterministic cases:

| Control | Purpose | Advance condition |
| --- | --- | --- |
| `native_full_visible_prefix_plus_tail` | Positive guard that the native route can solve the visible structured prompt. | Must contain the expected value for all 5 cases. |
| `native_fresh_tail_only` | Negative leakage/scorer control. | Must contain 0/5 expected values; any contained answer stops or quarantines the run. |
| `native_live_append_tail_only` | Same-context prefix prefill, then tail-only append. | Must contain the expected value for all 5 cases before restored capsule can be interpreted. |
| `native_restored_capsule_append_tail_only` | Save prefix state, restore into a fresh context, append tail only. | Main Family 2 capsule result. |

## Metrics

Raw records under ignored paths should include full evidence needed to audit the run. Committed summaries retain only sanitized fields:

- case id, family, task shape, and control
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

- If `native_full_visible_prefix_plus_tail` fails any case, stop as `family2_full_visible_guard_failed`; do not interpret live append or restored capsule.
- If `native_fresh_tail_only` contains any expected answer, stop or quarantine as `family2_fresh_tail_leakage_or_scorer_issue`.
- If `native_live_append_tail_only` fails any case, stop as `family2_live_append_protocol_blocker`; do not interpret restored capsule as a semantic capsule failure.
- If live append passes and restored capsule fails, classify `family2_restored_capsule_structured_retrieval_failure` or a narrower save/restore blocker if telemetry supports it.
- If restored capsule passes, classify `family2_restored_capsule_structured_retrieval_passed` and stop before expansion.

## Artifact Layout

Prompt-bearing raw artifacts stay under ignored Track 01 paths:

```text
research/01-ssd-native-inference-current/benchmarks/kv-capsule-family2-structured-retrieval-gate-2026-06-04/raw/
```

Committed Track 02 summaries live under:

```text
research/02-quality-gated-stateful-kv-reuse/experiments/kv-capsule-family2-structured-retrieval-gate-2026-06-04/
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

If live append fails and restored capsule is not run, do not create a synthetic capsule contract. Record the missing restored-capsule contract in `summary.json` and `artifact-manifest.json`.

## Risks / Trade-offs

- Structured prompts may expose prompt-protocol weakness rather than capsule weakness. The full-visible guard handles this by stopping before capsule interpretation.
- Fresh-tail leakage would invalidate the task as a hidden-prefix retrieval probe. The fresh-tail control stops or quarantines that condition.
- Exact-only output may fail even when the semantic answer is present. Answer-contained is the semantic metric; exact-only remains a secondary output-discipline metric.
- The pinned GPT-OSS/b9493 route remains ABI-risk by nature of the Python `ctypes` direct API. Family 1 parity, token smoke, and the same canonical route reduce but do not remove that risk.

## Migration Plan

Create and validate this OpenSpec change, add ignore coverage for the raw benchmark path, adapt the ignored Family 1 native runner into a Family 2-only runner, run syntax and grep sanity checks locally, sync only the necessary ignored runner/worktree state to DushyantPC, run `--mode family2`, copy raw artifacts back, package sanitized Track 02 summaries, run OpenSpec validation, confirm raw ignored status, and commit locally without pushing.
