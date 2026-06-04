## 1. OpenSpec Checkpoint

- [x] 1.1 Confirm the worktree is based on `f3862b9 Record scaled KV capsule benchmark campaign`.
- [x] 1.2 Create proposal, design, task ledger, and spec delta for `run-kv-capsule-calibrated-a-to-e-campaign`.
- [x] 1.3 Validate the change with `openspec validate run-kv-capsule-calibrated-a-to-e-campaign --type change --strict` before model-bearing work.

## 2. Runner Preparation

- [x] 2.1 Add ignored raw path coverage for `kv-capsule-calibrated-a-to-e-campaign-2026-06-04`.
- [x] 2.2 Create an ignored native C API runner under the Track 01 raw path.
- [x] 2.3 Ensure the only model-bearing CLI mode is the explicit calibrated campaign mode, with optional raw-only `smoke` and `token-smoke` modes.
- [x] 2.4 Remove or disable executable server, bridge, Family 1, Family 2, Family 3, GraphWalks, noiseless-evidence, and broad-benchmark paths from the campaign CLI.
- [x] 2.5 Implement chunked native prefill/decode around `n_batch=512`.
- [x] 2.6 Implement Phase A calibration variants and promotion/freeze bookkeeping.
- [x] 2.7 Implement Phase B/C promoted retrieval controls, one-capsule-many-restores semantics, and scale boundary recording.
- [x] 2.8 Implement Phase D amortization curves for restored-capsule-passing units.
- [x] 2.9 Implement Phase E agent-context calibration/evidence, gated on at least one retrieval restored-capsule pass.
- [x] 2.10 Run local `python3 -m py_compile`, help/mode checks, stale-path grep, and ignored raw-path checks before DushyantPC sync.

## 3. Phase A Visible-Baseline Calibration

- [x] 3.1 Run systematic structured-retrieval calibration variants at 10 rows first.
- [x] 3.2 Enforce promotion only for variants with full-visible answer-contained 10/10 and exact/normalized scoring high enough for evidence; no variants qualified.
- [x] 3.3 Preserve failed calibration attempts as sanitized summaries with variant ids, hashes, counts, and failure classes.
- [x] 3.4 If all reasonable variants fail at 10 rows, package the benchmarkability result and stop for orchestration review.

## 4. Phase B Semantic Capsule Ladder

- [x] 4.1 For each promoted retrieval unit, rerun frozen `native_full_visible_prefix_plus_tail` and require 10/10. Not run by stop rule because Phase A promoted no retrieval unit.
- [x] 4.2 Run `native_fresh_tail_only` and quarantine any leakage/scorer issue. Not run by stop rule because Phase A promoted no retrieval unit.
- [x] 4.3 Run `native_live_append_tail_only` and require 10/10 before restored-capsule interpretation. Not run by stop rule because Phase A promoted no retrieval unit.
- [x] 4.4 Run `native_restored_capsule_append_tail_only` with one reusable prefix capsule restored for each tail query. Not run by stop rule because Phase A promoted no retrieval unit.
- [x] 4.5 Classify failed promoted units without mutating their evidence prompts. No promoted evidence unit existed; calibration failures were classified instead.

Phase B was not run because Phase A promoted no retrieval unit.

## 5. Phase C Scale Ladder and Boundary Search

- [x] 5.1 Push promoted retrieval units through 10, 25, 50, and 100 rows where feasible. Not run by stop rule because no 10-row unit was promoted.
- [x] 5.2 Attempt 250 rows only if runtime/context behavior remains practical after lower scales. Not run by stop rule because lower scales did not promote.
- [x] 5.3 Record highest reliable full-visible, live-append, and restored-capsule scales as null/not established due the Phase A stop rule.

Phase C scale pushes were not run because the smallest 10-row scale failed all calibration variants.

## 6. Phase D Amortization and Economics

- [x] 6.1 Measure one-time prefix prefill/save/build cost and per-query restore/tail/decode cost. Not applicable because no restored-capsule unit ran.
- [x] 6.2 Calculate break-even curves for N = 1, 2, 5, 10, 20, 50, and 100. Not interpretable because no restored-capsule unit ran.
- [x] 6.3 Report amortization as not interpretable because no restored-capsule quality-passing unit existed.

Phase D measurements were not run because no restored-capsule controls were eligible.

## 7. Phase E Agent-Context Benchmark

- [x] 7.1 Run Phase E only after at least one retrieval restored-capsule ladder passes.
- [x] 7.2 Build and calibrate a repo-local agent-context prefix and 8 to 10 deterministic tail tasks. Not run because the retrieval restored-capsule precondition failed.
- [x] 7.3 Promote/freeze the agent-context unit only after full-visible quality passes. Not run because the retrieval restored-capsule precondition failed.
- [x] 7.4 Run full-visible, fresh-tail, live-append, and restored-capsule controls in order. Not run because the retrieval restored-capsule precondition failed.
- [x] 7.5 Record Phase E as not run because the retrieval restored-capsule precondition failed.

Phase E was not run because Phase A/B produced no retrieval restored-capsule pass.

## 8. Packaging

- [x] 8.1 Copy ignored raw artifacts back from DushyantPC and preserve raw prompts, responses, logs, token arrays, and state bytes under ignored Track 01 paths.
- [x] 8.2 Package sanitized Track 02 artifacts: `README.md`, `summary.json`, `phase-results.json`, `calibration-results.json`, `case-metrics.json`, `amortization.json`, `failure-classifications.json`, `commands.md`, `model-info.json`, and `artifact-manifest.json`.
- [x] 8.3 Add `capsule-contract.md` or `capsule-contracts.json` only for units where restored capsule actually runs; no capsule contract was created because restored capsule did not run.
- [x] 8.4 Include exact artifact paths, model/backend hashes, command lines, raw artifact hashes, validity boundaries, and highest reliable scales.
- [x] 8.5 Run sanitation grep and non-tab/newline control-byte scan over committed campaign artifacts.

## 9. Validation and Landing

- [x] 9.1 Validate `openspec validate run-kv-capsule-calibrated-a-to-e-campaign --type change --strict`.
- [x] 9.2 Validate `openspec validate --all --strict`.
- [x] 9.3 Confirm prompt-bearing raw artifacts are ignored and not staged.
- [x] 9.4 Commit locally if coherent; do not push.
