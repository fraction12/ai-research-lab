# Gemma 4 12B Replication Prep Design

## Research Question

Can the same official llama.cpp sequence-file state route preserve tail-only semantic continuation for Gemma 4 12B on the already-gated Family 1 and Family 2 tasks?

## Baseline And Controls

For each approved gate, run controls in order:

1. `native_full_visible_prefix_plus_tail`
2. `native_fresh_tail_only`
3. `native_live_append_tail_only`
4. `native_restored_capsule_append_tail_only`

The restored control is interpretable only if full-visible passes, fresh-tail does not leak, and live append passes.

## Model Profile Requirements

Gemma 4 12B must be selected through an explicit profile/config rather than implicit CLI edits. The profile must record:

- model family/name and local model path,
- GGUF/hash/size metadata,
- tokenizer/template assumptions,
- context size and decode budget,
- llama.cpp bundle/backend,
- sequence-state export availability,
- route requested/effective/internal labels,
- any model-specific sampler/template notes.

The GPT-OSS profile must remain available and unchanged.

## Runtime Assumptions

- Orchestration owns DushyantPC SSH and model execution.
- Repo work may prepare docs or profile scaffolding only.
- No Gemma run is evidence until raw/cache paths are ignored and local/remote syntax/help/stale-grep checks pass.
- `--state-route auto` should resolve to `seq_file` when sequence file exports are available; `whole-context` may only be labeled fallback/diagnostic and cannot count as success.

## Smoke Ladder

1. Gemma profile dry-run/help check.
2. Raw-only smoke or token-smoke if orchestration approves.
3. Family 1 3-case smoke.
4. Family 1 30-case gate if smoke passes.
5. Family 2 smoke only after Family 1 passes.
6. Family 2 primary only after Family 2 smoke passes.

Do not run beyond these gates without new orchestration clearance.

## Metrics

Record the same metrics as GPT-OSS:

- answer-contained and exact match,
- response/normalized/generated hashes,
- full-vs-live and live-vs-restored hash parity,
- prefix/tail/full token counts and hashes,
- capsule byte counts and save/restore timings,
- sequence positions and sequence id,
- model/backend/build metadata,
- process cleanup status.

## Artifact Boundary

Prompt-bearing raw artifacts must remain ignored under Track 01 benchmark paths. Committed Track 02 artifacts may include hashes, counts, booleans, routes, timings, failure classes, and model metadata. Do not commit raw prompts, raw responses, expected answer strings, token arrays/slices, generated token arrays/slices, top-k arrays, token piece previews, or state bytes.

## Stop Rules

- Stop before model work if OpenSpec validation fails, raw/cache paths are not ignored, stale GPT-OSS-only assumptions are reachable, or DushyantPC sanity fails.
- If Gemma full-visible fails, classify model/task/template/scorer difficulty and do not interpret capsule.
- If fresh tail passes, classify leakage/benchmark flaw.
- If live append fails, classify harness/tokenization/position/template route blocker.
- If restored capsule fails after full/live pass, inspect sequence route telemetry and package the narrowest route/model blocker.
- If semantic pass occurs but hash parity differs, package semantic pass with deterministic-parity warning.
