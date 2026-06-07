# PTI v3 Schema-Repair Behavior Smoke - 2026-06-07

## Purpose

Verify that the PTI v3 schema-only validator is wired into the active BFCL model-loop repair gate, then run the same targeted restored-KV smoke on DushyantPC.

This is not a full BFCL score and not a leaderboard submission.

## Change Under Test

- Commit: `65d064e Wire BFCL PTI schema repair gate`
- OpenSpec change: `upgrade-bfcl-pti-runtime-v3`
- Repair gate: `bfcl_schema_only_active_repair_gate_v1`

The old BFCL scorer-triggered repair path was disabled for model repair. BFCL repair now fires from visible-schema validation errors, not expected-call scoring failures.

Allowed repair inputs:

- source user request
- visible BFCL function catalog/schema
- model output
- parser/decoder errors
- schema-validator errors

Disallowed repair inputs:

- `possible_answer`
- `expected_answer`
- `expected_calls`
- `ground_truth`
- official expected calls

## Validation

Local:

- BFCL adapter + official runner tests: `35/35`
- Python compile: passed
- OpenSpec change validation: passed
- OpenSpec strict all: `43 passed, 0 failed`

DushyantPC:

- Fresh smoke checkout: `C:\ai\bfcl-pti-v3-repair-smoke`
- DushyantPC unit tests: `35/35`
- DushyantPC compile check: passed
- Targeted model records: `15`
- Runner exit: `0`
- Export: `5` BFCL result files
- Official partial evaluator: completed

## Official Partial Evaluator Result

| Category | Score |
|---|---:|
| `irrelevance` | `3/3` |
| `parallel` | `2/3` |
| `simple_javascript` | `2/3` |
| `simple_java` | `1/3` |
| `parallel_multiple` | `1/3` |

The aggregate non-live partial score was `33.33%` over this deliberately hard 15-case subset. It is not comparable to the full non-live score.

## Repair Telemetry

- Records: `15`
- Rows with `repair_count = 1`: `9`
- Rows with `repair_count = 0`: `6`

Rows repaired:

- `irrelevance_0`, `irrelevance_1`, `irrelevance_2`: all passed after one repair turn.
- `parallel_0`: failed after one repair turn.
- `parallel_multiple_0`, `parallel_multiple_2`: failed after one repair turn.
- `java_1`, `java_2`: failed after one repair turn.
- `javascript_2`: failed after one repair turn.

## Interpretation

The implementation goal passed: schema-only repair is now active in the model loop and the old scorer-derived BFCL repair trigger is removed.

The behavior signal is mixed:

- The gate helped enough for `parallel_multiple` to move from `0/3` in the prior v3 smoke to `1/3`.
- `irrelevance` stayed strong at `3/3`.
- `parallel` dropped from `3/3` to `2/3`, likely because repair introduced an extra chance to drift on one row.
- Java remains weak at `1/3`.

This is not yet good enough to justify a full 1,390-case PTI v3 rerun. The next clean step is to make the repair gate more selective and structured: allow schema-only repair for missing/invalid calls, but avoid needless repair on rows where `[]` is already a valid abstention candidate or where the schema validator is flagging harmless argument-shape noise.
