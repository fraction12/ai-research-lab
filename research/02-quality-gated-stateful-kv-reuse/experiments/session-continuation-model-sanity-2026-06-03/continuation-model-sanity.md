# Continuation Model Sanity

Date: 2026-06-03

## Decision

Option 2 did not rescue tail-only raw `/completion`.

`vault-mind-q5_k_m.gguf` loaded under the same DushyantPC llama.cpp portable Vulkan backend and passed the positive-control full prompts, but both same-slot `live-tail` and save/restore `restored-tail` still failed across default and transcript-format case sets.

| Case set | Full | Live-tail | Restored-tail | Fresh-tail |
| --- | ---: | ---: | ---: | ---: |
| `default` | 3/3 | 0/3 | 0/3 | 0/3 |
| `transcript-format` | 3/3 | 0/3 | 0/3 | 0/3 |

## What Changed Versus Option 1

The model changed from repo-local `gpt-oss-20b-mxfp4.gguf` to local `vault-mind-q5_k_m.gguf`.

The prompt format also changed for the transcript-format case set:

```text
System: ...
User: Store this exact secret token for the next turn: TOKEN
Assistant: I have stored the exact secret token TOKEN for the next turn.
```

The tail still ran as a tail-only raw `/completion` call, because that is the primitive under evaluation.

## Result Details

Default cases:

- Full prompts returned the exact tokens.
- Live-tail, restored-tail, and fresh-tail all returned the same malformed JSON-like prefix: `{"answer": "wv923fj293rj293rj293rj293rj2`.
- The repeated wrong tail/fresh pattern indicates the tail prompt is behaving independently of the primed prefix.

Transcript-format cases:

- Full prompts returned the exact tokens.
- Live-tail, restored-tail, and fresh-tail all returned `1234567890`.
- Explicit transcript scaffolding did not make tail-only raw `/completion` act like a semantic continuation.

## Restore Sanity

Slot save/restore happened on the valid short-cache reruns:

| Case set | Case | Saved | Restored |
| --- | --- | ---: | ---: |
| `default` | `secret-alpha` | 39 | 39 |
| `default` | `secret-bravo` | 39 | 39 |
| `default` | `secret-charlie` | 40 | 40 |
| `transcript-format` | `transcript-alpha` | 71 | 71 |
| `transcript-format` | `transcript-bravo` | 73 | 73 |
| `transcript-format` | `transcript-charlie` | 73 | 73 |

A first default run with the long cache path produced Windows log-file path errors and was preserved as raw evidence. The valid rerun used short cache path `benchmarks\session-continuation-litmus-cache\scms-vd`.

## Failure Taxonomy

| Category | Classification | Evidence |
| --- | --- | --- |
| Model weakness | Unlikely primary cause for this litmus | Vault full-prompt controls passed 6/6 across default and transcript-format cases. |
| Prompt protocol issue | Strongly implicated | Tail-only outputs matched fresh-tail behavior in both case sets. |
| Scorer/parser brittleness | Not primary | Default tail outputs had parse errors, but transcript-format tail outputs parsed cleanly as wrong answer `1234567890`. |
| Session/cache semantic issue | Strongly implicated at endpoint/protocol level | Same-slot live-tail failed 0/6 across case sets with no disk restore. |
| Position/compatibility issue | Not isolated | Restored-tail failed, but live-tail also failed. |
| Runtime/storage issue | Mixed but not primary after rerun | Long path caused a preserved failed attempt; short-path reruns saved/restored matching token counts. |

## Option 3 Handoff

We should stop spending mainline effort on tail-only raw `/completion` as a semantic primitive.

Option 3 should get closer to the metal. The useful next probes are things like:

- resend full prompt after priming and measure whether llama.cpp reuses cached prefix tokens correctly;
- inspect slot/KV behavior through lower-level prompt-token alignment rather than only answer quality;
- design a repair path where reusable state is validated as prefix-cache reuse, not assumed as hidden conversational memory;
- if needed, move from raw endpoint behavior toward an explicit append/continue primitive or a wrapper-level state machine that sends the correct prefix while measuring saved prefill.
