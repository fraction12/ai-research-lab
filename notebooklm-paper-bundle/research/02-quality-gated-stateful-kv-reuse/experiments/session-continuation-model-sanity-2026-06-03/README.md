# Session Continuation Model Sanity

Date: 2026-06-03

This experiment is the bounded Option 2 sanity check after the first session-continuation litmus. It tests whether tail-only raw `/completion` failure changes with an alternate local GGUF or a more explicit conversation-transcript prompt format.

## Scope

Model under test:

```text
C:\Users\Dushyant\Documents\vault-mind\vault-mind-q5_k_m.gguf
```

The model loaded under the same DushyantPC llama.cpp portable Vulkan backend and passed the default full-prompt probe 3/3.

No broad benchmarks or GraphWalks reruns were run.

## Main Result

The alternate model did not rescue tail-only continuation.

| Case set | `full` | `live-tail` | `restored-tail` | `fresh-tail` |
| --- | ---: | ---: | ---: | ---: |
| `default` | 3/3 | 0/3 | 0/3 | 0/3 |
| `transcript-format` | 3/3 | 0/3 | 0/3 | 0/3 |

In the default case set, all tail-only and fresh-tail modes produced the same malformed JSON-like response prefix instead of the secret token. In the transcript-format case set, all tail-only and fresh-tail modes produced `1234567890`.

## Interpretation

This sanity check makes the tail-only `/completion` issue less likely to be a single `gpt-oss-20b-mxfp4.gguf` artifact or a plain-prompt formatting artifact.

The next Track 02 work should move to Option 3: a lower-level/protocol repair probe that gets closer to actual KV/session mechanics rather than expecting a second raw `/completion` call with only the tail prompt to behave like semantic append-continuation.

## Artifacts

- `commands.md`: exact commands used locally and on DushyantPC.
- `model-info.json`: model, backend, machine, and run parameters.
- `summary.json`: committed aggregate and case-level results with raw artifact paths and hashes.
- `continuation-model-sanity.md`: interpretation, failure taxonomy, and Option 3 handoff.
- `transcript-format-cases.jsonl`: exact transcript-format synthetic prompts.

Prompt-bearing raw JSON and llama.cpp logs/slot files are preserved under ignored Track 01 benchmark paths listed in `summary.json`.
