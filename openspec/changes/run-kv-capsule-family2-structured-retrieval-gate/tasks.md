## 1. Define Family 2 Gate

- [x] 1.1 Create proposal, design, tasks, and spec deltas for the reviewed Family 2 structured-retrieval capsule gate.
- [x] 1.2 State the research question, controls, metrics, stop rules, artifact boundary, and validity boundary before model-bearing execution.
- [x] 1.3 Validate `run-kv-capsule-family2-structured-retrieval-gate` with OpenSpec strict validation before model-bearing execution.

## 2. Prepare Runner And Sync

- [x] 2.1 Add ignore coverage for `benchmarks/kv-capsule-family2-structured-retrieval-gate-*` prompt-bearing artifacts if needed.
- [x] 2.2 Adapt the ignored Family 1 native direct C API runner into a Family 2-only raw runner under the new raw path.
- [x] 2.3 Ensure the only model-bearing CLI mode is `family2`, with no executable server, bridge, GraphWalks, or broad benchmark path.
- [x] 2.4 Run local syntax checks and grep sanity checks before DushyantPC sync.
- [ ] 2.5 Sync DushyantPC safely without destructive commands and preserve exact commands.

## 3. Run Family 2 Controls

- [ ] 3.1 Run `native_full_visible_prefix_plus_tail` on 5 deterministic structured-retrieval cases using canonical `add_special=true` full-prompt route.
- [ ] 3.2 Stop if full-visible guard fails; otherwise advance only if all 5 answer-contained scores pass.
- [ ] 3.3 Run `native_fresh_tail_only` and stop/quarantine if any case unexpectedly contains the answer.
- [ ] 3.4 Run `native_live_append_tail_only` and stop before restored capsule interpretation if any case fails.
- [ ] 3.5 Run `native_restored_capsule_append_tail_only` only if live append passes all 5 cases.
- [ ] 3.6 Do not run Family 3, mini graph, GraphWalks, noiseless evidence, server bridge, or broad benchmarks.

## 4. Package Artifacts

- [ ] 4.1 Write `README.md` with outcome, stop rule, and narrow interpretation.
- [ ] 4.2 Write `summary.json` with aggregate pass/fail, selected route, decision, timings, and state byte counts/hashes.
- [ ] 4.3 Write sanitized `case-metrics.json` with no raw prompts, raw responses, expected answer strings, token ID arrays, generated token arrays, top-k arrays, or state bytes.
- [ ] 4.4 Write `failure-classifications.json`, `commands.md`, `model-info.json`, and `artifact-manifest.json`.
- [ ] 4.5 Write `capsule-contract.md` only if restored capsule actually runs.
- [ ] 4.6 Run sanitation grep and confirm raw prompt-bearing artifacts remain ignored.

## 5. Validate And Land

- [ ] 5.1 Run `openspec validate run-kv-capsule-family2-structured-retrieval-gate --type change --strict`.
- [ ] 5.2 Run `openspec validate --all --strict`.
- [ ] 5.3 Commit locally if coherent; do not push without explicit approval.
