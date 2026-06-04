## 1. Define Family 3 Gate

- [x] 1.1 Create proposal, design, tasks, and spec deltas for the reviewed Family 3 mini-graph capsule gate.
- [x] 1.2 State the research question, controls, metrics, stop rules, artifact boundary, and validity boundary before model-bearing execution.
- [x] 1.3 Validate `run-kv-capsule-family3-mini-graph-gate` with OpenSpec strict validation before model-bearing execution.

## 2. Prepare Runner And Sync

- [x] 2.1 Add ignore coverage for `benchmarks/kv-capsule-family3-mini-graph-gate-*` prompt-bearing artifacts if needed.
- [x] 2.2 Adapt the ignored Family 2 native direct C API runner into a Family 3-only raw runner under the new raw path.
- [x] 2.3 Ensure the only model-bearing CLI mode is `family3`, with no executable server, bridge, Family 1, Family 2, GraphWalks, or broad benchmark path.
- [x] 2.4 Run local syntax checks and grep sanity checks before DushyantPC sync.
- [x] 2.5 Report local sanity evidence before DushyantPC sync/model execution.
- [x] 2.6 Sync DushyantPC safely without destructive commands and preserve exact commands.

## 3. Run Stage A One-Hop Controls

- [x] 3.1 Run `native_full_visible_prefix_plus_tail` on 3 deterministic Stage A one-hop mini-graph cases using canonical `add_special=true` full-prompt route.
- [x] 3.2 Stop if Stage A full-visible guard fails; Stage A full-visible scored 2/3, so the run stopped as `family3_stage_a_full_visible_guard_failed`.
- [x] 3.3 Stage A `native_fresh_tail_only` was not run by stop rule after Stage A full-visible failed.
- [x] 3.4 Stage A `native_live_append_tail_only` was not run by stop rule after Stage A full-visible failed.
- [x] 3.5 Stage A `native_restored_capsule_append_tail_only` was not run by stop rule after Stage A full-visible failed.

## 4. Run Stage B Two-Hop Controls

- [x] 4.1 Stage B was not run because Stage A restored capsule did not run or pass.
- [x] 4.2 Stage B `native_full_visible_prefix_plus_tail` was not run by Stage A stop rule.
- [x] 4.3 Stage B full-visible stop condition was not reached because Stage B was not run.
- [x] 4.4 Stage B `native_fresh_tail_only` was not run by Stage A stop rule.
- [x] 4.5 Stage B `native_live_append_tail_only` was not run by Stage A stop rule.
- [x] 4.6 Stage B `native_restored_capsule_append_tail_only` was not run by Stage A stop rule.
- [x] 4.7 Do not run GraphWalks, noiseless evidence, server bridge, Family 4, or broad benchmarks.

## 5. Package Artifacts

- [x] 5.1 Write `README.md` with outcome, stage progression, stop rule, and narrow interpretation.
- [x] 5.2 Write `summary.json` with aggregate pass/fail, selected route, decision, timings, stage summaries, and state byte counts/hashes.
- [x] 5.3 Write sanitized `case-metrics.json` with no raw prompts, raw responses, expected answer strings, token ID arrays, generated token arrays, top-k arrays, or state bytes.
- [x] 5.4 Write `failure-classifications.json`, `commands.md`, `model-info.json`, and `artifact-manifest.json`.
- [x] 5.5 Omit `capsule-contract.md` because restored capsule did not run.
- [x] 5.6 Run sanitation grep and confirm raw prompt-bearing artifacts remain ignored.

## 6. Validate And Land

- [x] 6.1 Run `openspec validate run-kv-capsule-family3-mini-graph-gate --type change --strict`.
- [x] 6.2 Run `openspec validate --all --strict`.
- [x] 6.3 Commit locally if coherent; do not push without explicit approval.
