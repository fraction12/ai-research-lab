# Session Continuation Litmus

Date: 2026-06-03

This experiment checks whether llama.cpp same-slot and restored-slot tail-only completions behave like semantic continuation for a tiny memory-token task.

## Scope

Three synthetic secret-token cases were run in four modes:

| Mode | Purpose |
| --- | --- |
| `full` | Positive control: remember instruction and question in one prompt. |
| `live-tail` | Prime stable prefix, then ask the tail in the same server/slot without save/restore. |
| `restored-tail` | Prime stable prefix, save slot, restore slot, then ask the tail. |
| `fresh-tail` | Ask the tail without priming; expected to fail. |

No broad benchmarks or GraphWalks reruns were run.

## Main Result

`full` passed 3/3 and `fresh-tail` failed 3/3, so the task and negative control were valid.

Both continuation modes failed 3/3:

| Mode | Pass rate |
| --- | ---: |
| `full` | 3/3 |
| `live-tail` | 0/3 |
| `restored-tail` | 0/3 |
| `fresh-tail` | 0/3 |

The tail-only modes returned valid JSON, but the parsed answer was always `I am a secret token` instead of the primed token.

## Interpretation

For this model/backend/protocol stack, tail-only `/completion` calls are not a reliable semantic continuation primitive, even before disk save/restore enters the picture. This supports treating the prior six-case GraphWalks `live-tail` and `session-tail` failures as a protocol/continuation-semantics problem rather than a broad runtime/storage failure.

## Artifacts

- `commands.md`: exact commands used locally and on DushyantPC.
- `model-info.json`: model, quantization, backend, machine, and run parameters.
- `summary.json`: committed aggregate and case-level results with raw artifact paths and hashes.
- `continuation-interpretation.md`: decision, taxonomy, and next-step implications.

Prompt-bearing raw JSON and llama.cpp logs/slot files are preserved under ignored Track 01 benchmark paths listed in `summary.json`.
