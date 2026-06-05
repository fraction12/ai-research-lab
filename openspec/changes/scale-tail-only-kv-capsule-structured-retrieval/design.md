# Family 2 Sequence-State Structured Retrieval Scale Design

## Prior Evidence

- `tail-only-kv-capsule-continuation-repair-2026-06-04`: Family 1 simple codeword passed `30/30` on full-visible, live append, and restored capsule using effective route `seq_file`; fresh-tail missed `30/30`.
- `kv-capsule-family2-structured-retrieval-gate-2026-06-04`: older small Family 2 gate passed `5/5`, but this change treats it as narrow prior evidence and reruns Family 2 using the repaired sequence-file route and deterministic parity metrics.

## Research Question

Can a restored native sequence-state capsule preserve a compact hidden structured lookup prefix so that tail-only lookup queries behave semantically like full visible `prefix + tail`, without resending the prefix text?

## Official Route Assumption

The strong contract is the lower-level llama.cpp C API sequence-state route:

- `llama_state_seq_save_file`
- `llama_state_seq_load_file`
- `llama_state_seq_get_size`
- `llama_state_seq_get_data`
- `llama_state_seq_set_data`

Server `cache_prompt` and slot save/restore remain diagnostic prompt-cache/full-prompt mechanisms and are not evidence for this gate unless they prove true tail-only continuation. This Family 2 gate stays on the native C API route.

## Task Family

Each case uses fabricated deterministic key-value facts:

- Prefix contains 6 to 8 compact `FACT` records with similar distractor values. Earlier 12-32 and 12-16 row variants hit the full-visible guard and are treated as invalid task difficulty, not capsule evidence.
- Each `FACT` line binds `item_id` and `region` to exactly one `owner_code`.
- Tail is a slot-completion query ending in `owner_code=` for one key/field.
- The answer string appears only in the prefix and never in the tail.
- Cases are seeded and synthetic; no private data.

The smoke gate uses 3 cases. The primary gate uses 30 cases.

## Controls

For each case, run controls in this exact order:

1. `native_full_visible_prefix_plus_tail`
2. `native_fresh_tail_only`
3. `native_live_append_tail_only`
4. `native_restored_capsule_append_tail_only`

Canonical token/position route:

- Full prompt and prefix prefill tokenize with `add_special=true`.
- Appended tail tokenizes with `add_special=false`.
- Prefix prefill starts at position `0`.
- Tail append starts at `len(prefix_tokens)`.
- Generation starts at `len(prefix_tokens) + len(tail_tokens)`.
- Sequence id is `0`.

## Metrics

Record raw metrics under ignored Track 01 paths and commit only sanitized summaries:

- Answer-contained and exact-match by control.
- Response and normalized response hashes.
- Full-vs-live and live-vs-restored hash parity per case.
- Prefix, tail, and full token counts plus token hashes.
- Generated token counts and hashes.
- First-token/top-k hashes if collected, but no token arrays or top-k arrays in committed artifacts.
- Capsule bytes, save/restore ms, state bytes saved/restored, restored token counts.
- Prefix/tail/generation positions.
- Requested/effective/internal route and sequence export availability.
- Model/backend hashes and process cleanup status.

## Stop Rules

- If full-visible is not `30/30`, classify task/model/scorer difficulty, repair the dataset/scorer or reduce difficulty, and rerun a valid gate before interpreting capsules.
- If fresh-tail is nonzero, classify contamination/leak/benchmark flaw and regenerate before interpreting capsules.
- If live append is below full-visible, classify harness/tokenization/position bug and repair before interpreting restored capsules.
- If restored capsule is below live append on `seq_file`, inspect route/position/state telemetry. If sequence memory APIs are available, run one controlled rerun with `--state-route seq-memory` on the same gate.
- If `seq_file` and `seq_memory` both fail while full-visible and live append pass, package a Family 2 no-go/failure report and stop.
- If restored semantic pass is `30/30` but live-vs-restored hashes differ, package as semantic pass with deterministic-parity warning.
- If restored semantic pass is `30/30` and live-vs-restored hashes match case-by-case, package as strong Family 2 sequence-state continuation positive.
- Do not run Family 3, GraphWalks, broad retrieval, or noiseless evidence in this change.

## Artifact Boundary

Ignored raw/cache:

```text
research/01-ssd-native-inference-current/benchmarks/tail-only-kv-capsule-family2-structured-retrieval-scale-2026-06-04/raw/
research/01-ssd-native-inference-current/benchmarks/tail-only-kv-capsule-family2-structured-retrieval-scale-2026-06-04/cache/
```

Committed sanitized package:

```text
research/02-quality-gated-stateful-kv-reuse/experiments/tail-only-kv-capsule-family2-structured-retrieval-scale-2026-06-04/
```

Committed artifacts must not contain raw prompts, raw responses, expected answer strings, token ID arrays/slices, generated token arrays/slices, top-k arrays, token piece previews, or state bytes.
