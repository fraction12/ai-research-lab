# Scale Tail-Only KV Capsule Structured Retrieval

## Why

The previous repair gate at commit `59c1122` proved a narrow but real mechanism: on Family 1 simple codeword cases, the pinned GPT-OSS/native CUDA stack passed `30/30` full-visible, `0/30` fresh-tail, `30/30` live-append, and `30/30` restored-capsule controls using the official llama.cpp sequence-file route (`llama_state_seq_save_file` / `llama_state_seq_load_file`).

That is a mechanism proof, not a broad research result. The next question is whether the same true tail-only restored sequence-state path preserves a richer hidden prefix: fabricated structured retrieval with multiple key-value records and distractors.

## What

Run a narrowly scoped Family 2 structured retrieval scale gate on the same native C API route:

- Create deterministic fabricated structured lookup cases with compact multi-row prefixes.
- Calibrate the task by stop rule: use 30 cases with 6-8 FACT records per prefix after larger table variants failed the full-visible guard.
- Run 3-case smoke and 30-case primary gates.
- Use `--state-route auto`, expected to resolve to `seq_file`.
- Preserve explicit fallback labels for `seq-memory` and `whole-context`, but do not count whole-context fallback as strong sequence-state success.
- Record semantic scoring, deterministic output hash parity, token/count/timing metrics, route telemetry, and capsule state metrics.
- Package sanitized Track 02 artifacts and keep prompt-bearing raw artifacts ignored under Track 01.

## Scope

In scope:

- Family 2 structured retrieval only.
- Native direct C API route only.
- Official sequence-file state route as the primary path.
- Optional controlled rerun with `seq-memory` only if `seq_file` fails after full-visible and live-append pass.

Out of scope:

- GraphWalks, Family 3, agent-context tasks, broad retrieval benchmarks, noiseless evidence, and server prompt-cache claims.
- Claiming general KV capsule correctness beyond this task family.

## Success

The gate succeeds only if:

- Full visible passes `30/30`.
- Fresh tail passes `0/30`.
- Native live append passes `30/30`.
- Native restored capsule append passes `30/30` on `seq_file`.
- Live-vs-restored response hashes match case-by-case for deterministic parity, or the result is explicitly packaged as a semantic pass with deterministic-parity warning.

## Risks

- GPT-OSS may be weak on larger structured lookup even with full-visible context.
- The task/scorer may leak answers or become brittle.
- Sequence-file restore may pass semantic scoring but diverge in deterministic output hashes because of sampler/logit path differences.
- Whole-context fallback must not be allowed to masquerade as sequence-state success.
