# PTI v3 Targeted Behavior Smoke - 2026-06-07

## Purpose

Run a small restored-KV/PTI v3 smoke on DushyantPC after adding the schema-only compiler/validator/repair substrate. This is a behavior and integration smoke, not a full BFCL score and not a leaderboard submission.

## Change Under Test

- OpenSpec change: `upgrade-bfcl-pti-runtime-v3`
- Commit: `8d7fa9b Add BFCL PTI runtime v3`
- No-cheat boundary: validation and repair prompt generation use only the user request, visible schema/catalog, model output, parser/decoder errors, and schema-validator diagnostics. No `possible_answer`, expected calls, or answer-key repair is used.

## Local Validation

- BFCL adapter + official runner unit tests: `33/33`
- Python compile check: passed
- OpenSpec change validation: passed
- OpenSpec strict all: `43 passed, 0 failed`

## DushyantPC Validation

- Fresh smoke checkout: `C:\ai\bfcl-pti-v3-smoke`
- Output lane: `C:\ai\bfcl-pti-v3-smoke\bfcl-pti-v3-smoke-lane`
- Data source: `C:\ai\bfcl-official-data-full-normalized`
- Control: `code_mode_restored_kv_capsule`
- State route: `seq-file`
- Run label: `bfcl-pti-v3-targeted-behavior-smoke-v1`
- DushyantPC unit tests: `33/33`
- DushyantPC compile check: passed
- Materialization: `15` cases, `105` control records
- Model records: `15`
- Runner exit: `0`
- Export: `5` BFCL result files
- GPU after run: idle, `318 / 12288 MiB`

Note: OpenSpec CLI was not installed on DushyantPC, so OpenSpec validation remains local-verified.

## Official Partial Evaluator Result

The partial BFCL evaluator was run against the 15 exported records. The evaluator model key was the existing local registered key `gemma4-kv-capsule-pti`; result artifacts came from the PTI v3 smoke export.

| Category | PTI v3 smoke score |
|---|---:|
| `irrelevance` | `3/3` |
| `parallel` | `3/3` |
| `simple_javascript` | `2/3` |
| `simple_java` | `1/3` |
| `parallel_multiple` | `0/3` |

The aggregate non-live partial score was `33.33%` over this deliberately hard 15-case subset. It is not comparable to the full non-live score.

## Interpretation

The implementation smoke passed: v3 packets, validator metadata, restored-KV model execution, export, and partial official evaluation all work end to end.

The behavior signal is mixed and does not justify a full PTI v3 BFCL rerun yet:

- Abstention remained strong in the targeted sample: `irrelevance` passed `3/3`.
- Parallel single-function multi-call behavior passed `3/3` in this sample.
- JavaScript stayed acceptable at `2/3`.
- Java regressed in the tiny sample to `1/3`.
- `parallel_multiple` remains the clearest weak spot at `0/3`; the current v3 substrate defines diagnostics/repair prompts but does not yet force an actual schema-only repair loop over missing independent calls.

Recommended next step: wire the schema-only validator into the model loop as an active repair gate before final export, then rerun this same 15-case smoke. Do not launch the full 1,390-case run until Java and `parallel_multiple` recover in the targeted smoke.
