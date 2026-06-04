## 1. Define Probe Contract

- [x] 1.1 Create OpenSpec proposal, design, tasks, and spec deltas for KV capsule semantic continuation.
- [x] 1.2 Preserve the KV capsule experiment design doc as a committed Track 02 artifact.
- [x] 1.3 Validate the change with `openspec validate probe-kv-capsule-semantic-continuation --type change --strict`.

## 2. Run Feasibility Gate

- [x] 2.1 Confirm the Mac worktree and DushyantPC checkout can see the current Track 02 state.
- [x] 2.2 Inspect the pinned GPT-OSS llama.cpp installation for native C/C++ headers, libraries, build files, and state APIs.
- [x] 2.3 Inspect Python binding availability only if the native C/C++ route is blocked. No binding route was used because the direct C API route was feasible.
- [x] 2.4 Reject server-only routes unless they can prove tail tokens append to restored `n_past` without resending prefix text.
- [x] 2.5 Record feasibility commands, findings, runner/model hashes, and the selected route or blocker.

## 3. Build Lower-Level Harness If Feasible

- [x] 3.1 Add ignore coverage for `benchmarks/kv-capsule-semantic-continuation-*` prompt-bearing artifacts.
- [x] 3.2 Create an ignored local runner or native harness for deterministic gates.
- [x] 3.3 Implement `native_live_append_tail_only` before any capsule persistence claim.
- [x] 3.4 Implement `native_restored_capsule_append_tail_only` as a non-interpreted control, with no capsule persistence claim because native full-visible parity failed.
- [x] 3.5 Record known server controls as prior separate evidence; wrong/corrupt capsule controls were not run because the native full-visible positive control failed first.
- [x] 3.6 Run syntax, direct API smoke, token-smoke, and bounded GPU-backend checks practical for the selected harness.

## 4. Run Experimental Ladder

- [x] 4.1 Run the codeword gate until the native full-visible positive-control stop rule fired; accepted run is partial and uninterpretable for capsule semantics.
- [x] 4.2 Do not run the key-value gate because Family 1 stopped on failed native full-visible positive control.
- [x] 4.3 Do not run the mini graph gate because Family 1 stopped on failed native full-visible positive control.
- [x] 4.4 Do not run the six historical GraphWalks cases because Family 1 stopped on failed native full-visible positive control.
- [x] 4.5 Stop before any broad benchmark or noiseless-evidence rerun.

## 5. Record Track 02 Artifacts

- [x] 5.1 Write `README.md` with research question, controls run, result, stop rule, and interpretation.
- [x] 5.2 Write `summary.json` with aggregate scores, selected route, decision, and model/runner hashes.
- [x] 5.3 Write `case-metrics.json` and `failure-classifications.json`, superseding preliminary raw harness labels with stop-rule classifications.
- [x] 5.4 Write `capsule-contract.md` classifying contract fields as captured, inferred, unavailable, missing, or not exercised.
- [x] 5.5 Write `commands.md`, `model-info.json`, and `artifact-manifest.json`.
- [x] 5.6 Keep prompt-bearing raw artifacts ignored under Track 01 benchmark paths.

## 6. Validate And Land

- [x] 6.1 Run `openspec validate probe-kv-capsule-semantic-continuation --type change --strict`.
- [x] 6.2 Run `openspec validate --all --strict`.
- [x] 6.3 Confirm prompt-bearing artifacts remain ignored.
- [x] 6.4 Commit locally if coherent; do not push without explicit approval.
