# llama.cpp Prefix-Reuse Audit

Date: 2026-06-04

This experiment tests whether direct llama.cpp `/completion` calls can show prompt-work reduction for exact-prefix reuse, and where that reduction disappears.

## Scope

Model under test:

```text
C:\Users\Dushyant\Projects\ai-research-lab\research\01-ssd-native-inference-current\benchmarks\models\gpt-oss-20b-mxfp4.gguf
```

No GraphWalks, broad benchmarks, or alternate models were run.

## Main Result

Same-server reuse works. Fresh-server persistent slot restore does not reduce prompt work.

| Mode | Pass rate | Prompt ms | Prompt tokens | Reuse classification |
| --- | ---: | ---: | ---: | --- |
| `cold-full` | 1/1 | 5971.621 | 7784 | `baseline_passed` |
| `same-server-exact-repeat` | 1/1 | 46.572 | 1 | `exact_repeat_reuse_observed` |
| `same-server-restore-full` | 1/1 | 305.354 | 46 | `restore_reuse_observed` |
| `fresh-server-restore-full` | 1/1 | 5943.286 | 7784 | `restore_no_reuse` |

Slot telemetry showed `n_saved=7743` and `n_restored=7743` for both restore controls, so the fresh-server failure is not simply "slot did not restore." The restored state exists, but the fresh server does not reuse the restored prefix when the full prompt is resent.

## Decision

Decision: `same_server_restore_reuse_only`.

The next mechanism step is not GraphWalks. It is a persistent-session or fresh-server restore investigation:

- same-server exact repeat proves `cache_prompt` can reduce prompt work;
- same-server restore/full-resend proves slot restore can reduce prompt work while the server process remains alive;
- fresh-server restore/full-resend fails to reduce prompt work even with matching saved/restored token counts.

## Artifacts

- `summary.json`: aggregate result, timing, token, slot, and gate summary.
- `model-info.json`: exact model, backend, machine, command-line, and run metadata.
- `commands.md`: exact commands.
- `mechanism-decision.md`: interpretation and next-step gate.
- `failure-classifications.json`: taxonomy mapping.
- `artifact-manifest.json`: raw and committed artifact inventory.

Prompt-bearing raw JSON, server logs, and slot files are preserved under ignored Track 01 benchmark paths listed in `summary.json`.
