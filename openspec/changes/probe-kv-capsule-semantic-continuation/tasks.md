## 1. Define Probe Contract

- [x] 1.1 Create OpenSpec proposal, design, tasks, and spec deltas for KV capsule semantic continuation.
- [x] 1.2 Preserve the KV capsule experiment design doc as a committed Track 02 artifact.
- [x] 1.3 Validate the change with `openspec validate probe-kv-capsule-semantic-continuation --type change --strict`.

## 2. Run Feasibility Gate

- [ ] 2.1 Confirm the Mac worktree and DushyantPC checkout can see the current Track 02 state.
- [ ] 2.2 Inspect the pinned GPT-OSS llama.cpp installation for native C/C++ headers, libraries, build files, and state APIs.
- [ ] 2.3 Inspect Python binding availability only if the native C/C++ route is blocked.
- [ ] 2.4 Reject server-only routes unless they can prove tail tokens append to restored `n_past` without resending prefix text.
- [ ] 2.5 Record feasibility commands, findings, runner/model hashes, and the selected route or blocker.

## 3. Build Lower-Level Harness If Feasible

- [x] 3.1 Add ignore coverage for `benchmarks/kv-capsule-semantic-continuation-*` prompt-bearing artifacts.
- [ ] 3.2 Create an ignored local runner or native harness for deterministic gates.
- [ ] 3.3 Implement `native_live_append_tail_only` before any capsule persistence claim.
- [ ] 3.4 Implement `native_restored_capsule_append_tail_only` only after live append is valid.
- [ ] 3.5 Implement known server controls and negative capsule/position controls when technically possible.
- [ ] 3.6 Run syntax, build, or unit checks practical for the selected harness.

## 4. Run Experimental Ladder

- [ ] 4.1 Run the 10-variant codeword gate and apply stop rules.
- [ ] 4.2 Run the 10-variant key-value gate only if the codeword gate is positive and interpretable.
- [ ] 4.3 Run the mini graph gate only if the key-value gate is positive and interpretable.
- [ ] 4.4 Run the six historical GraphWalks cases only if the simple gates justify structured-task interpretation.
- [ ] 4.5 Stop before any broad benchmark or noiseless-evidence rerun.

## 5. Record Track 02 Artifacts

- [ ] 5.1 Write `README.md` with research question, controls run, result, stop rule, and interpretation.
- [ ] 5.2 Write `summary.json` with aggregate scores, selected route, decision, and model/runner hashes.
- [ ] 5.3 Write `case-metrics.json` and `failure-classifications.json`.
- [ ] 5.4 Write `capsule-contract.md` classifying contract fields as captured, inferred, unavailable, missing, or not exercised.
- [ ] 5.5 Write `commands.md`, `model-info.json`, and `artifact-manifest.json`.
- [ ] 5.6 Keep prompt-bearing raw artifacts ignored under Track 01 benchmark paths.

## 6. Validate And Land

- [ ] 6.1 Run `openspec validate probe-kv-capsule-semantic-continuation --type change --strict`.
- [ ] 6.2 Run `openspec validate --all --strict`.
- [ ] 6.3 Confirm prompt-bearing artifacts remain ignored.
- [ ] 6.4 Commit locally if coherent; do not push without explicit approval.
