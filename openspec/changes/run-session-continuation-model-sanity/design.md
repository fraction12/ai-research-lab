## Context

Option 1 established a sharp failure on `gpt-oss-20b-mxfp4.gguf`: full prompt passed 3/3, fresh-tail failed 3/3, and both live-tail and restored-tail failed 3/3 on a tiny secret-token continuation litmus. That result strongly suggests tail-only raw `/completion` is not semantic append-continuation for the current protocol, but it is still worth one bounded sanity check against a second local GGUF and a more explicit prompt format before moving lower-level.

DushyantPC has an alternate local GGUF outside the repo:

```text
C:\Users\Dushyant\Documents\vault-mind\vault-mind-q5_k_m.gguf
```

PowerShell reported size `5444831136` bytes on 2026-06-03. The model identity and architecture are not yet proven compatible with the current llama.cpp build, so the first live step is a bounded load/full-mode probe.

## Goals / Non-Goals

**Goals:**

- Test whether a second local GGUF can pass the same tiny session-continuation litmus.
- Test whether an explicit conversation-transcript prompt format changes tail-only behavior under raw `/completion`.
- Preserve exact model path, model bytes, backend, commands, prompts, raw outputs, parsed answers, hashes, timings, and failure classifications.
- Keep the result framed as a sanity check before Option 3, not as a new main mechanism path.

**Non-Goals:**

- No broad benchmark suite.
- No GraphWalks rerun.
- No new model download.
- No migration from `/completion` to `/v1/chat/completions`.
- No lower-level KV/session repair implementation in this change.

## Decisions

### Decision 1: Use the existing litmus runner

Reuse `benchmarks/flashcache_session_continuation_litmus.py`.

Rationale: Option 2 should change model/format, not the harness. If the existing runner cannot express a necessary format control through `--cases`, stop and record the limitation rather than refactoring.

### Decision 2: Run two tiny case sets when practical

Run:

| Case set | Purpose |
| --- | --- |
| `default` | Exact apples-to-apples comparison with Option 1. |
| `transcript-format` | Explicit `System/User/Assistant` transcript text in prefix and tail while still using raw `/completion`. |

Rationale: if the alternate model passes default tail-only continuation, the prior failure may be model/format specific. If only transcript-format passes, prompt protocol is implicated. If both fail with valid full/fresh controls, tail-only raw completion remains the wrong abstraction.

### Decision 3: Bound failed-load behavior

First run one full-mode probe on the alternate model. If the model cannot load or full prompt cannot pass, record Option 2 as inconclusive for model generalization and do not run the remaining modes.

Rationale: a failed model-load control should not waste machine time or be confused with continuation evidence.

### Decision 4: Commit summaries and case prompts; keep raw outputs ignored

Committed Track 02 files live under:

```text
research/02-quality-gated-stateful-kv-reuse/experiments/session-continuation-model-sanity-2026-06-03/
```

Expected committed files:

```text
README.md
commands.md
model-info.json
summary.json
continuation-model-sanity.md
transcript-format-cases.jsonl
```

Raw prompt/output artifacts stay under ignored Track 01 benchmark paths:

```text
research/01-ssd-native-inference-current/benchmarks/session-continuation-litmus-results/session-continuation-model-sanity-2026-06-03/
research/01-ssd-native-inference-current/benchmarks/session-continuation-litmus-cache/session-continuation-model-sanity-2026-06-03/
```

## Risks / Trade-offs

- [Risk] The alternate GGUF may be unsupported by the current llama.cpp build. -> Mitigation: run a bounded full-mode probe first and classify the result as load/probe failure if needed.
- [Risk] Transcript-format full prompt may pass only because the token is visibly repeated in prior assistant text. -> Mitigation: require fresh-tail to fail and interpret success only as raw-completion format tolerance, not as GraphWalks-safe reuse.
- [Risk] A passing alternate model would not rescue the current gpt-oss protocol. -> Mitigation: keep Option 3 as the next main lane and treat Option 2 as a sanity check.
- [Risk] Raw prompt outputs contain exact prompts. -> Mitigation: keep raw JSON ignored but commit synthetic transcript cases because they are deliberately non-sensitive.
