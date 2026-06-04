## Context

Fixed prior result:

```text
commit: c8a96d9 Record native server parity bridge
decision: native_full_visible_parity_passed_family1_capsule_gate_not_run_in_this_script
prompt shape: prior_known_good_simple_codeword
```

The bridge showed:

- server full-visible simple codeword baseline contained the answer `3/3`
- native full-visible contained the answer `3/3` for both `add_special=true` and `add_special=false`
- server `/tokenize` payload shape `content` matched native token hashes
- server `/tokenize` payload shape `prompt` returned 0 tokens and must not be used for semantics

Because both native `add_special` routes matched on the bridge, this gate will choose `add_special=true` as the canonical route for `full_visible_prefix_plus_tail` and prefix prefill. The bridge showed it has the same token hash as `add_special=false` for the selected prompt shape, while `add_special=true` preserves the conventional “start of prompt may include special token if the tokenizer needs it” contract. Tail-only append uses `add_special=false` because the tail is not a new prompt start.

## Research Question

Can native direct C API state save/restore create a prefix capsule such that:

```text
restore(capsule(prefix)) + append(tail)
```

is semantically equivalent to:

```text
prefix + tail
```

without resending the prefix text in the tail step?

## Controls

Run controls in order for the same 3 deterministic simple codeword cases:

| Control | Purpose | Advance condition |
| --- | --- | --- |
| `native_full_visible_prefix_plus_tail` | Positive guard using the parity-proven full visible route. | Must contain the expected codeword for all 3 cases. |
| `native_fresh_tail_only` | Negative leakage/scorer control. | Should not contain the expected codeword. |
| `native_live_append_tail_only` | Same-context prefix prefill, then tail-only append. | Must contain the expected codeword before restored capsule can be interpreted. |
| `native_restored_capsule_append_tail_only` | Save prefix state, restore into a fresh context, append tail only. | Main capsule result. |

## Metrics

Each raw record should include prompt-bearing details under ignored paths. Committed summaries retain only sanitized fields:

- case id
- control and route
- exact match and answer-contained booleans
- output status and failure class
- prompt/prefix/tail/response hashes
- token counts, not token ID arrays
- prompt/decode/total timing
- `n_past_before_tail_append`
- `generation_start_pos`
- capsule/state byte counts
- capsule save/restore time
- model, runner, lib, backend, source, and hardware hashes or metadata

Committed artifacts must not include raw prompt text, raw responses, token ID slices, generated token slices, top-k arrays, or state bytes.

## Stop Rules

- If `native_full_visible_prefix_plus_tail` fails, stop as `native_full_visible_guard_failed`.
- If `native_fresh_tail_only` unexpectedly contains the answer, stop or quarantine as `fresh_tail_leakage_or_scorer_issue`.
- If `native_live_append_tail_only` fails, stop as `native_live_append_protocol_blocker` and do not interpret restored capsule.
- If live append passes but restored capsule fails, classify `restored_capsule_semantic_failure` or a narrower save/restore blocker if telemetry supports it.
- If restored capsule passes, classify `family1_restored_capsule_semantic_passed`, but do not expand to Family 2, GraphWalks, noiseless evidence, or broad benchmarks.

## Artifact Layout

Prompt-bearing raw artifacts stay under ignored Track 01 paths:

```text
research/01-ssd-native-inference-current/benchmarks/kv-capsule-family1-semantic-gate-2026-06-04/raw/
```

Committed Track 02 summaries live under:

```text
research/02-quality-gated-stateful-kv-reuse/experiments/kv-capsule-family1-semantic-gate-2026-06-04/
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

If live append fails and restored capsule is not run, do not create a synthetic capsule contract. Record the missing restored-capsule contract in `summary.json` and `artifact-manifest.json` instead.

## Migration Plan

Create and validate this OpenSpec change, add ignore coverage for the raw benchmark path if needed, sync DushyantPC to the current commit, copy an ignored native runner to the raw path, run syntax checks, run only the 3-case Family 1 gate, package sanitized summaries, validate, and commit locally without pushing.
