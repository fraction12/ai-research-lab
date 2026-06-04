## Context

Track 02 has ruled out tail-only raw `/completion` as a useful semantic continuation primitive for the current local-agent path. The restored-prefix full-resend probe then showed a better correctness story: full visible prompts passed synthetic exact-token controls and did not leak restored slot state. But that probe did not show useful acceleration; restored-full reported the same prompt token count as cold-full and worse mean prompt time.

The next useful question is narrower and lower-level: can the configured llama.cpp backend show prompt-work reduction for any exact-prefix reuse pattern through `/completion`, and if so where does the reduction disappear?

## Goals / Non-Goals

**Goals:**

- Prove whether same-server exact-repeat `/completion` calls show prompt-work reduction with `cache_prompt=true`.
- Compare same-server slot restore/full-resend versus fresh-server slot restore/full-resend.
- Amplify the signal with a longer synthetic prefix so useful reuse should be obvious if active.
- Preserve exact model, backend, command lines, prompt hashes, raw outputs, timings, token counts, slot telemetry, log paths, and classifications.
- Produce a Track 02 decision on whether to inspect llama.cpp flags/accounting, persistent sessions, or lower-level KV mechanics next.

**Non-Goals:**

- No GraphWalks runs.
- No broad correctness benchmark.
- No alternate or experimental fine-tuned model.
- No wrapper API refactor unless the audit proves the current abstraction cannot expose the needed signal.

## Decisions

### Direct llama.cpp probe, not wrapper probe

Use `ManagedLlamaServer` and `LlamaClient.completion` directly. The wrapper is useful for agent-facing telemetry, but this audit is about isolating llama.cpp behavior. A wrapper-level test would add cache-key, server lifecycle, and chat-format confounders before we know whether direct `/completion` reuse works.

### Four controls, run in a fixed ladder

1. `same-server-exact-repeat`: send a long full prompt twice to one live server with `cache_prompt=true`.
2. `same-server-restore-full`: prime/save a prefix, restore it in the same server, then resend the full prompt.
3. `fresh-server-restore-full`: prime/save in server A, restore in server B, then resend the full prompt.
4. `cold-full`: baseline fresh-server full prompt with no restored slot.

The main gate is not correctness; the prompt is synthetic and answer checking is still exact-token JSON. The main gate is prompt-work reduction in prompt timing or token accounting.

### Use long synthetic prefixes

The previous exact-token prefix was too small for robust timing interpretation. The audit should default to a long repeated synthetic prefix sized by repeat count, while keeping prompts deterministic and hashable.

### Strict acceleration classification

The audit should classify outcomes as:

- `exact_repeat_reuse_observed`
- `exact_repeat_no_reuse`
- `restore_reuse_observed`
- `restore_no_reuse`
- `correctness_failure`
- `runtime_storage_issue`

Single-case timing noise is not enough. Useful acceleration requires either lower prompt token accounting or a clear mean prompt-time reduction across the selected runs.

## Risks / Trade-offs

- [Risk] llama.cpp timing fields may count cached tokens as prompt tokens even when work is reduced. -> Mitigation: record prompt_ms, prompt_n, wall_ms, and raw logs rather than relying on one metric.
- [Risk] Long prefixes make every mistake expensive. -> Mitigation: run one synthetic case first, not a suite.
- [Risk] Windows path length can break logs and slot paths. -> Mitigation: use short `lcpr-*` result/cache directories and hashed log labels.
- [Risk] Exact-repeat cache behavior can be server-version-specific. -> Mitigation: preserve llama.cpp `--version`, command line, model bytes, and machine metadata.
