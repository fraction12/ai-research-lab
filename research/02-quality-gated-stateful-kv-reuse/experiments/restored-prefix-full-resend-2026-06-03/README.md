# Restored-Prefix Full-Resend Probe

Date: 2026-06-03

This experiment tests Option 3 for Track 02: restore a saved llama.cpp prefix slot, resend the full visible prompt, and ask whether this is correctness-safe and measurably faster than a cold full-prompt run.

## Scope

Model under test:

```text
C:\Users\Dushyant\Projects\ai-research-lab\research\01-ssd-native-inference-current\benchmarks\models\gpt-oss-20b-mxfp4.gguf
```

No broad benchmarks were run. The six selected GraphWalks cases were not run.

## Main Result

The restored-prefix full-resend path was correctness-safe on tiny synthetic exact-token controls, but it did not show useful acceleration evidence.

| Mode | Pass rate | Mean prompt ms | Mean prompt tokens |
| --- | ---: | ---: | ---: |
| `cold-full` | 3/3 | 659.674 | 79.667 |
| `restored-full` | 3/3 | 687.327 | 79.667 |
| `perturbed-full` | 3/3 | 710.755 | 79.667 |
| `wrong-slot-full` | 3/3 | 648.801 | 79.667 |

All scored modes had zero parser errors. Perturbed and wrong-slot controls answered the visible full prompt, not the restored slot token.

## Gate Decision

Decision: `correctness_safe_without_useful_acceleration_evidence`.

The GraphWalks follow-up gate did not open because restored-full had the same prompt token count as cold-full and worse mean prompt time by 27.653 ms. One case had a small prompt-ms win, but the aggregate and token accounting do not support a useful reuse claim.

## Interpretation

This supports the conservative correctness part of the direction: full visible prompts avoid the tail-only semantic-continuation failure and did not leak restored state in the tiny controls.

It does not yet support the performance mechanism. At this layer, restoring a slot and resending the full prompt did not reduce the prompt work reported by llama.cpp. The next step should get closer to the metal: inspect llama.cpp prefix matching, slot restore semantics, cache-prompt accounting, and lower-level KV reuse behavior before spending runs on GraphWalks.

## Artifacts

- `summary.json`: committed aggregate result, case-level timing, raw paths, hashes, and gate decision.
- `model-info.json`: exact model, backend, machine, command line, and run metadata.
- `commands.md`: exact commands used locally and on DushyantPC.
- `mechanism-decision.md`: mechanism interpretation and stop rule.
- `failure-classifications.json`: taxonomy classification for the run.
- `artifact-manifest.json`: committed and ignored artifact inventory.

Prompt-bearing raw JSON, llama.cpp logs, and slot files are preserved under ignored Track 01 benchmark paths listed in `summary.json`.
