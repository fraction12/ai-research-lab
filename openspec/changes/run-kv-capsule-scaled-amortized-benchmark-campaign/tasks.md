## 1. OpenSpec Checkpoint

- [x] 1.1 Confirm the worktree is clean and based on `1a35780 Record KV capsule Family 3 gate`.
- [x] 1.2 Create proposal, design, task ledger, and spec delta for `run-kv-capsule-scaled-amortized-benchmark-campaign`.
- [x] 1.3 Validate the change with `openspec validate run-kv-capsule-scaled-amortized-benchmark-campaign --type change --strict` before model-bearing work.

## 2. Runner Preparation

- [x] 2.1 Add ignored raw path coverage for `kv-capsule-scaled-amortized-benchmark-campaign-2026-06-04`.
- [x] 2.2 Create a campaign-only native C API runner under the ignored Track 01 raw path.
- [x] 2.3 Ensure the only model-bearing CLI mode is the explicit campaign mode, with optional raw-only `smoke` and `token-smoke` modes.
- [x] 2.4 Remove or disable executable server, bridge, Family 1, Family 2, Family 3, GraphWalks, noiseless-evidence, and broad-benchmark paths from the campaign CLI.
- [x] 2.5 Run local `python3 -m py_compile` and stale-path grep checks before DushyantPC sync.
- [x] 2.6 Record local runner sanity evidence: mode choices, default raw path, output filenames, syntax check, and stale executable-path grep.

## 3. Phase 1 Scaled Structured Retrieval

- [x] 3.1 Generate deterministic reusable structured prefixes for row-count sizes 25, 100, and 250, plus 10 tail queries per size.
- [x] 3.2 Run `native_full_visible_prefix_plus_tail` for each size and stop that size unless it passes 10/10 answer-contained.
- [x] 3.3 Run `native_fresh_tail_only` for each full-visible-passing size and quarantine that size if any fresh tail contains the expected answer. No sizes passed the full-visible guard, so this was not run.
- [x] 3.4 Run `native_live_append_tail_only` for each passing size and stop restored-capsule interpretation unless it passes 10/10. No sizes passed the full-visible guard, so this was not run.
- [x] 3.5 Run `native_restored_capsule_append_tail_only` for each passing size using one reusable prefix capsule per size. No sizes passed the full-visible guard, so this was not run.
- [x] 3.6 Record one-time capsule build/save cost, per-query restore/tail/decode cost, capsule bytes, token counts, hashes, and stop-rule decisions. Capsule metrics are not present because restored controls did not run.

## 4. Phase 2 Reasoning Calibration

- [x] 4.1 Run full-visible-only calibration across tiny one-hop reasoning formats.
- [x] 4.2 Stop Phase 2 as `reasoning_full_visible_calibration_failed` if no template reaches 100% answer-contained.
- [x] 4.3 If a template calibrates, run ordered controls on that one-hop template only. No template calibrated, so this was not run.
- [x] 4.4 If one-hop restored capsule passes and two-hop full-visible calibrates, optionally run the tiny two-hop ordered controls. No template calibrated, so this was not run.
- [x] 4.5 Record Phase 2 prompt format decisions, stop rules, and classifications without importing GraphWalks.

## 5. Phase 3 Agent-Context Benchmark

- [x] 5.1 Run Phase 3 only if Phase 1 restored capsule quality passes for at least one scaled size.
- [x] 5.2 Build a reusable local-agent-like prefix from repo-local context with source file hashes and sanitized metadata. Not run because Phase 3 precondition failed.
- [x] 5.3 Run full-visible, fresh-tail, live-append, and restored-capsule controls in order on 8 to 10 deterministic tasks. Not run because Phase 3 precondition failed.
- [x] 5.4 Record quality retained, token/time avoided, capsule size, and amortized break-even for Phase 3 if restored capsule runs. Not applicable because Phase 3 did not run.

## 6. Packaging

- [x] 6.1 Copy ignored raw artifacts back from DushyantPC and preserve raw prompts, responses, logs, token arrays, and state bytes under ignored Track 01 paths.
- [x] 6.2 Package sanitized Track 02 artifacts: `README.md`, `summary.json`, `phase-results.json`, `case-metrics.json`, `amortization.json`, `failure-classifications.json`, `commands.md`, `model-info.json`, and `artifact-manifest.json`.
- [x] 6.3 Add `capsule-contract.md` or `capsule-contracts.json` only for phases where restored capsule actually ran. Omitted because no restored-capsule control ran.
- [x] 6.4 Include exact artifact paths, model/backend hashes, command lines, raw artifact hashes, and validity boundaries.
- [x] 6.5 Run sanitation grep and control-byte scan over committed campaign artifacts.

## 7. Validation and Landing

- [ ] 7.1 Validate `openspec validate run-kv-capsule-scaled-amortized-benchmark-campaign --type change --strict`.
- [ ] 7.2 Validate `openspec validate --all --strict`.
- [ ] 7.3 Confirm prompt-bearing raw artifacts are ignored and not staged.
- [ ] 7.4 Commit locally if coherent; do not push.
