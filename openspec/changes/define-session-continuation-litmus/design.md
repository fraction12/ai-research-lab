## Context

Track 02 has two completed focused GraphWalks ladders. The latest repair/mechanism ladder found that `live-tail` no-restore failed all six cases, matching restored `session-tail`. That result moved suspicion away from disk slot restore and toward tail-only live session semantics, but it does not yet prove the llama.cpp slot API is behaving like semantic append-continuation.

Before moving to same-backend stronger model controls or lower-level KV/layer repair, run a tiny litmus:

```text
full prompt:      remember secret -> ask for secret in one prompt
live tail:        prime remember secret -> ask for secret in same slot, no save/restore
restored tail:    prime remember secret -> save slot -> restore slot -> ask for secret
fresh tail:       ask for secret without priming, expected to fail
```

If live/restored tail cannot pass this easy memory-token task, the GraphWalks session-tail path is not a valid semantic continuation primitive for our purposes. If they pass, the GraphWalks failure is more likely task/prompt/model specific.

## Goals / Non-Goals

**Goals:**

- Verify whether same-slot and restored-slot tail-only llama.cpp calls can recall primed content.
- Use tiny deterministic prompts that do not require GraphWalks reasoning.
- Preserve exact prompt text, commands, raw outputs, parsed answers, model/runtime metadata, and pass/fail interpretation.
- Run on DushyantPC with the same local model/backend shape used for Track 02.

**Non-Goals:**

- No broad benchmark suite.
- No GraphWalks rerun.
- No stronger model control yet.
- No lower-level KV/layer recompute implementation yet.
- No claim that passing a tiny litmus proves GraphWalks-safe session reuse.

## Decisions

### Decision 1: Use synthetic secret-token cases

Use two or three tiny cases with unique secret tokens such as `ZXQ-7419-ALPHA`. The scorer passes when the extracted answer contains the exact secret token.

Rationale: the task should be far easier than GraphWalks so failure points at continuation semantics, protocol, or runtime behavior rather than graph reasoning.

### Decision 2: Compare four modes

The litmus records:

| Mode | Purpose |
| --- | --- |
| `full` | Positive control: model sees remember instruction and question together. |
| `live-tail` | Same-slot continuation with no save/restore. |
| `restored-tail` | Save/restore then tail-only continuation. |
| `fresh-tail` | Negative control: question without primed content. |

Rationale: if `fresh-tail` passes, the prompt is contaminated or too guessable. If `full` fails, the model/protocol cannot solve the litmus. If `live-tail` fails while `full` passes, tail-only continuation is not semantically valid for this harness. If `restored-tail` fails while `live-tail` passes, restore/position compatibility is implicated.

### Decision 3: Implement as a tiny standalone benchmark script

Add a small `benchmarks/flashcache_session_continuation_litmus.py` rather than overloading correctness-eval dataset scoring.

Rationale: this is a backend/session semantic litmus, not a dataset correctness task. A standalone script keeps it obvious and minimizes impact on existing correctness code.

### Decision 4: Keep prompt-bearing outputs local but commit summaries

Committed Track 02 files live under:

```text
research/02-quality-gated-stateful-kv-reuse/experiments/session-continuation-litmus-2026-06-03/
```

Expected committed files:

```text
README.md
commands.md
model-info.json
summary.json
continuation-interpretation.md
```

Raw prompt/output artifacts stay under ignored benchmark result paths:

```text
research/01-ssd-native-inference-current/benchmarks/session-continuation-litmus-results/session-continuation-litmus-2026-06-03/
```

## Risks / Trade-offs

- The model may paraphrase around the token -> use JSON answer protocol and exact token matching.
- A too-simple prompt could pass through pattern guessing -> include `fresh-tail` negative control with unique tokens.
- Passing this litmus does not make GraphWalks safe -> record it only as a necessary sanity check, not a sufficient correctness guarantee.
- llama.cpp endpoint behavior could depend on version or `cache_prompt` settings -> record exact backend version, command line, and mode payloads.

## Migration Plan

No migration is required. Implement the script, add focused unit tests with fake clients, run the litmus on DushyantPC, write Track 02 artifacts, and validate OpenSpec plus relevant tests.
