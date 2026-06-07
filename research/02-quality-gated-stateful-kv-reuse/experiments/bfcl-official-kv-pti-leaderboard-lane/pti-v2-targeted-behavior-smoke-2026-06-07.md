# PTI v2 Targeted Behavior Smoke - 2026-06-07

## Purpose

Before launching another full BFCL non-live model generation run, run a small restored-KV/PTI v2 behavior smoke on DushyantPC. This checks whether the PTI v2 prompt/validator changes affect model behavior, rather than only improving export formatting over old records.

This is not a leaderboard score and not a replacement for the full 1,390-case official evaluation.

## Run

- Machine: DushyantPC
- Checkout: `C:\ai\bfcl-pti-v2-targeted-smoke`
- Output lane: `C:\ai\bfcl-pti-v2-targeted-smoke-run`
- Windows task: `BFCLPTIv2TargetedSmokeV1`
- Run label: `bfcl-pti-v2-targeted-behavior-smoke-v1`
- Commit/files: clean smoke checkout based on prior BFCL lane, patched with PTI v2 runner files from `7488196`
- Control: `code_mode_restored_kv_capsule`
- State route: `seq-file`
- Cases: 15 total, 3 per category
- Categories:
  - `simple_java`
  - `simple_javascript`
  - `parallel`
  - `parallel_multiple`
  - `irrelevance`
- Task result: exit `0`
- Runtime: 2026-06-07T12:51:30-04:00 to 2026-06-07T12:55:36-04:00
- GPU returned idle after completion.

## Official Partial Evaluator Result

BFCL official evaluator was run with `--partial-eval` against the 15 exported records.

| Category | Smoke score |
|---|---:|
| `irrelevance` | 3/3 |
| `simple_java` | 2/3 |
| `simple_javascript` | 2/3 |
| `parallel` | 2/3 |
| `parallel_multiple` | 1/3 |

The aggregate `data_non_live.csv` value is not comparable to the full non-live score because this was a partial subset across five categories.

## Failure Notes

- `parallel_1`: emitted one `calculate_em_force` call but missed the second requested call.
- `parallel_multiple_0`: emitted only `math_toolkit.sum_of_multiples`; missed `math_toolkit.product_of_primes`. The emitted `multiples` value also used `[3, 5]` where the official scorer expected the nested value shape.
- `parallel_multiple_1`: emitted only `area_rectangle.calculate`; missed `area_circle.calculate`.
- `java_1`: failed to produce a parseable final call. The raw generation drifted to a malformed JSON-ish tool-call form and misspelled `makeProposalsFromObject`.
- `javascript_2`: selected `extractLastTransactionId` and most arguments correctly, but used `"processing function"` instead of the literal expected callback name `"processFunction"`.

## Interpretation

This smoke is good enough to proceed to a full PTI v2 model run, but it also confirms the next score ceiling:

- Abstention behavior looks promising in this small targeted set: `irrelevance` passed 3/3.
- Java/JavaScript export and syntax changes are holding under model-generated records.
- Multi-call completeness remains the biggest open PTI behavior gap.
- The PTI v2 model contract still needs stronger handling for exact callback/string literals, exact function names, and emitting all independent calls.

Recommended next step: run the full BFCL non-live generation with PTI v2, then score with the official evaluator. If the full score stalls, build PTI v3 around multi-call planning and schema-guided repair.
