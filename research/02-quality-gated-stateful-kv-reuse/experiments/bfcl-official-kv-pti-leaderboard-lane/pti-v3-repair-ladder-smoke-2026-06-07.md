# PTI v3 Repair Ladder Smoke - 2026-06-07

## Purpose

Evaluate a step-by-step BFCL PTI repair ladder after the selective schema-repair smoke showed stability but no score gain.

The target was not to use answer keys or category labels. The repair loop remains limited to:

- user request
- visible function catalog and schema
- prior model output
- parsed call plan
- schema-only validator diagnostics

## Changes Under Test

- Parser tolerance for recoverable wrapper dialects before model repair.
- Literal-preservation candidate ordering that prefers exact callback/function identifiers over unrelated path-like tokens.
- Class-targeted repair prompt profiles for missing-call, extra-call, function-selection, literal-preservation, and argument-schema issues.
- Repair prompt boundary handling that closes an unfinished model-authored code fence before appending the host repair prompt.
- BFCL generation stop gating that avoids stopping on unclosed code fences, trailing commas, or unbalanced JSON fragments.

## Validation

- Local BFCL adapter and official-runner tests: `42 passed`.
- Local compile of touched benchmark modules: passed.
- DushyantPC core BFCL adapter smoke after final sync: `40 passed`.

## DushyantPC Micro-Smokes

Run root:

`C:\ai\bfcl-pti-repair-ladder-runs`

Common mode:

- control: `code_mode_restored_kv_capsule`
- model profile: `gemma4-12b`
- prediction budget: `128`
- max steps: `5`
- max schema repairs: `1`
- state route: `seq-file`

Results:

- `micro-simple-java-v1`: `2/3`, repairs `1`
- `micro-simple-javascript-v4`: `2/3`, repairs `1`
- `micro-parallel-v3`: `2/3`, repairs `1`
- `micro-parallel-multiple-v1`: `2/3`, repairs `1`

Read:

- Java improved from the previous mixed-smoke `1/3` to `2/3`.
- Parallel-multiple improved from the previous mixed-smoke `1/3` to `2/3`.
- JavaScript literal diagnostics now target `processFunction`, but the repair turn still does not reliably produce a corrected call.
- Parallel no longer fails from prematurely harvested incomplete JSON on the earlier one-call case; the remaining failure is a harder semantic/repair-output issue.

## Final Mixed Smoke

Lane:

`C:\ai\bfcl-pti-repair-ladder-runs\final-mixed-15-v1`

Run label:

`bfcl-pti-repair-ladder-final-mixed-15-v1`

Result:

- records: `15/15`
- total score: `11/15`
- repairs fired: `4`
- `irrelevance`: `3/3`, repairs `0`
- `parallel`: `2/3`, repairs `1`
- `parallel_multiple`: `2/3`, repairs `1`
- `simple_java`: `2/3`, repairs `1`
- `simple_javascript`: `2/3`, repairs `1`

Previous selective v3 mixed smoke:

- total score: `9/15`
- repairs fired: `6`
- `irrelevance`: `3/3`
- `parallel`: `2/3`
- `parallel_multiple`: `1/3`
- `simple_java`: `1/3`
- `simple_javascript`: `2/3`

Net:

- `+2/15` score improvement.
- Repairs reduced from `6` to `4`.
- Abstention stayed clean at `3/3`.

## Remaining Failures

- `bfcl:parallel:parallel_2`: parsed `2`, matched `1`; repair turn returned empty.
- `bfcl:parallel_multiple:parallel_multiple_0`: parsed `2`, matched `1`; schema-valid but semantically wrong remaining call.
- `bfcl:simple_java:java_1`: parsed `1`, matched `0`; semantic/function-selection miss.
- `bfcl:simple_javascript:javascript_2`: parsed `0`, matched `0`; literal repair target is now better, but the repair turn returned empty.

## Decision

This is a real improvement, but not enough to justify a full 1,390-case rerun yet.

The next repair work should focus on:

- making empty repair turns retryable without answer keys,
- strengthening literal-value replacement for callback/function identifiers,
- adding schema-only semantic function-selection hints from function names and descriptions,
- preserving already-valid calls while repairing only the failed call slot.
