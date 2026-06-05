## 1. OpenSpec and Inventory

- [x] 1.1 Confirm current HEAD/status and prior Track 02 evidence artifacts.
- [x] 1.2 Create proposal, design, tasks, and spec delta for `repair-tail-only-kv-capsule-continuation`.
- [x] 1.3 Refresh official llama.cpp server/C API route notes and preserve citations in design/docs.
- [x] 1.4 Validate `openspec validate repair-tail-only-kv-capsule-continuation --type change --strict` before model-bearing work.

## 2. Raw Boundary and Runner Surface

- [x] 2.1 Add ignored raw/cache path coverage for `tail-only-kv-capsule-continuation-repair-2026-06-04`.
- [x] 2.2 Create ignored runner/bridge artifacts under Track 01 raw path.
- [x] 2.3 Expose only explicit modes for approved route gates; no GraphWalks, broad benchmark, or noiseless-evidence path.
- [x] 2.4 Run local syntax/build/help/stale-path checks before DushyantPC sync.

## 3. Environment and Official Server Diagnostics

- [x] 3.1 Verify DushyantPC checkout, GPU/backend availability, model path, runner hashes, and no stale Python/llama processes.
- [ ] 3.2 Run server full-visible Family 1 diagnostic on the accepted simple codeword shape. Not re-run in this gate; prior server artifacts remain diagnostic only.
- [ ] 3.3 Run server `cache_prompt: true` full-prompt resend diagnostic with explicit slot. Not re-run in this gate; prior documented-cache artifacts remain separate.
- [ ] 3.4 Run server slot save/restore diagnostic with `--slot-save-path` and record cache telemetry. Not re-run in this gate.
- [ ] 3.5 Classify server diagnostics as full-prompt cache telemetry, not tail-only success unless tail-only append is actually proven. Preserved in design/artifacts; no new server diagnostic records were produced.

## 4. Family 1 Native Live Append

- [x] 4.1 Run 3-case smoke using parity-proven prompt/token/generation route.
- [x] 4.2 Expand to 30 deterministic codeword cases if smoke passes.
- [x] 4.3 Require full-visible `30/30` and fresh-tail `0/30`.
- [x] 4.4 Require native live append `30/30` before restored capsule interpretation.
- [x] 4.5 Repair tokenization/template/position/seq/logits/sampler issues if live append fails. Not needed; live append passed `30/30`.

## 5. Family 1 Restored Capsule

- [x] 5.1 Probe official sequence-state API exports and ABI/header compatibility.
- [x] 5.2 Prefer `llama_state_seq_save_file/load_file`; otherwise use sequence memory APIs; label whole-context state fallback if used.
- [x] 5.3 Run restored capsule tail-only append on 30 Family 1 cases.
- [x] 5.4 Record capsule contract fields, timings, hashes, byte counts, seq ids, and positions.
- [x] 5.5 Classify pass only if restored capsule reaches `30/30` with valid guards.

## 6. C/C++ Bridge Escalation

- [x] 6.1 If Python `ctypes` is insufficient, inspect exact headers/source/build feasibility on DushyantPC. N/A: Python `ctypes` route reached official sequence-file APIs and passed the gate.
- [x] 6.2 Build a tiny C/C++ bridge against exact headers/libs if practical. N/A: bridge escalation was not required.
- [x] 6.3 Run the same Family 1 gate through the bridge, or document exact bridge blocker. N/A: sequence-file route passed without bridge escalation.

## 7. Conditional Expansion

- [ ] 7.1 If Family 1 `30/30` restored capsule passes, propose or run approved Family 2 scale gate. Deferred to orchestration after this package.
- [ ] 7.2 If Family 2 scale passes, redesign Family 3 full-visible guard before capsule testing. Not reached in this change.
- [x] 7.3 Do not run GraphWalks/noiseless/broad benchmarks in this change without orchestration approval.

## 8. Packaging

- [x] 8.1 Copy ignored raw artifacts back from DushyantPC.
- [x] 8.2 Package sanitized Track 02 artifacts under the experiment directory.
- [x] 8.3 Include `capsule-contract.md` if restored capsule runs.
- [x] 8.4 Include no-go report fields if no viable route remains. N/A: viable sequence-file route passed; failure taxonomy still included.
- [x] 8.5 Run leak/control-byte scans.

## 9. Validation and Landing

- [x] 9.1 Validate `openspec validate repair-tail-only-kv-capsule-continuation --type change --strict`.
- [x] 9.2 Validate `openspec validate --all --strict`.
- [x] 9.3 Confirm raw artifacts are ignored and not staged.
- [x] 9.4 Commit locally if coherent; do not push. Completed by the local landing commit for this package.
