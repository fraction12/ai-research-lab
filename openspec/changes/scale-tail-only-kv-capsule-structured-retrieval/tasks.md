## 1. OpenSpec and Inventory

- [x] 1.1 Confirm worktree clean at/after `59c1122`.
- [x] 1.2 Create proposal, design, tasks, and spec delta for `scale-tail-only-kv-capsule-structured-retrieval`.
- [x] 1.3 Validate `openspec validate scale-tail-only-kv-capsule-structured-retrieval --type change --strict` before model-bearing work.

## 2. Raw Boundary and Runner Surface

- [x] 2.1 Add ignored raw/cache path coverage for `tail-only-kv-capsule-family2-structured-retrieval-scale-2026-06-04`.
- [x] 2.2 Create ignored Family 2 sequence-state runner under Track 01 raw path.
- [x] 2.3 Expose only explicit modes `smoke`, `token-smoke`, `family2-smoke`, and `family2-30`, plus `--state-route`.
- [x] 2.4 Implement deterministic structured lookup cases with answer-only-in-prefix guarantees.
- [x] 2.5 Add deterministic parity metrics for full-vs-live and live-vs-restored response hashes.
- [x] 2.6 Run local syntax/help/stale-path/raw-ignore checks before DushyantPC sync.

## 3. Remote Sanity

- [x] 3.1 Sync ignored runner/wrappers to DushyantPC.
- [x] 3.2 Verify remote HEAD/status, raw/cache ignored status, runner timestamp, compile/help, stale grep, sequence exports, and no stale python/llama process.
- [x] 3.3 Wait for launch clearance before model-bearing execution if orchestration requires a gate.

## 4. Family 2 Smoke

- [x] 4.1 Run `family2-smoke --state-route auto` foreground/held.
- [x] 4.2 Require full-visible `3/3`, fresh-tail `0/3`, live append `3/3`, and restored capsule `3/3` before expanding.
- [x] 4.3 Classify or repair by stop rule if smoke fails; earlier table variants failed full-visible and were repaired to 6-8 FACT records before the accepted smoke.

## 5. Family 2 Primary Gate

- [x] 5.1 Run `family2-30 --state-route auto` foreground/held if smoke passes.
- [x] 5.2 Require full-visible `30/30` and fresh-tail `0/30`.
- [x] 5.3 Require native live append `30/30` before restored capsule interpretation.
- [x] 5.4 Require restored capsule `30/30` for semantic pass.
- [x] 5.5 Classify live-vs-restored hash parity as strong deterministic parity or semantic-pass warning.
- [x] 5.6 If `seq_file` restored fails after guards pass, run one controlled `seq-memory` rerun if available; otherwise package the route failure.

Current result: copied-back primary artifacts show `family2-30` completed with full-visible `30/30`, fresh-tail `0/30`, live append `30/30`, and restored capsule `30/30` on effective route `seq_file`. Deterministic hash parity was partial (`12/30` full-vs-live and `12/30` live-vs-restored), so the result is packaged as a semantic pass with hash-parity warning.

## 6. Packaging

- [x] 6.1 Copy ignored raw/cache artifacts back from DushyantPC.
- [x] 6.2 Package sanitized Track 02 artifacts under the experiment directory.
- [x] 6.3 Include `capsule-contract.md` when restored capsule runs.
- [x] 6.4 Include failure/no-go fields if the gate fails.
- [x] 6.5 Run leak and control-byte scans.

## 7. Validation and Landing

- [x] 7.1 Validate `openspec validate scale-tail-only-kv-capsule-structured-retrieval --type change --strict`.
- [x] 7.2 Validate `openspec validate --all --strict`.
- [x] 7.3 Confirm raw artifacts are ignored and not staged.
- [x] 7.4 Commit locally if coherent; do not push. Completed by this local landing commit.
