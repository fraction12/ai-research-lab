## 1. Define Bridge Contract

- [x] 1.1 Create OpenSpec proposal, design, tasks, and spec deltas for native/server parity.
- [x] 1.2 Preserve prior KV-capsule artifacts as prior evidence; do not rewrite their result.
- [x] 1.3 Validate the change with `openspec validate bridge-native-server-parity-for-kv-capsule --type change --strict`.

## 2. Prepare Harness And Artifact Boundaries

- [x] 2.1 Add ignore coverage for `benchmarks/native-server-parity-bridge-*` prompt-bearing artifacts if not already covered.
- [x] 2.2 Confirm Mac worktree and DushyantPC checkout can see commit `e5a7f3e` plus this change before remote runs.
- [x] 2.3 Reuse or extend the ignored direct C API runner only under the ignored raw path, with no CLI path that can run capsule controls before native full-visible parity passes.
- [x] 2.4 Run syntax/smoke checks for modified harness scripts before model calls.
- [x] 2.5 Record exact model, server, libllama, backend, source, GPU, and command-line hashes.

## 3. Run Server And Tokenization Parity Ladder

- [x] 3.1 Run refreshed 3-variant server full-visible codeword baseline.
- [x] 3.2 Capture server request payload shape, sampler params, response hashes, answer-contained scores, timings, and token counts if returned.
- [x] 3.3 Capture server tokenization for exact prompt bytes if an endpoint is available; otherwise record the limitation.
- [x] 3.4 Compare native tokenization with `add_special=true` and `add_special=false`.
- [x] 3.5 Select the most plausible special-token/template route or stop with a tokenization/protocol blocker.

## 4. Run Native Prompt And Sampler Parity Ladder

- [x] 4.1 Test raw completion prompt versus selected template/BOS route.
- [x] 4.2 Inspect logits index, first-token/top-k behavior, token-to-piece conversion, and sampler loop enough to explain or rule out repeated newline generation.
- [x] 4.3 Run native full-visible parity gate only after selecting the best prompt/sampler route.
- [x] 4.4 Native full-visible parity passed, so no blocker was packaged.

## 5. Rerun Capsule Gate Only If Parity Passes

- [x] 5.1 Do not run Family 1 codeword capsule controls in this assignment; parity passed and the script stopped for review.
- [x] 5.2 Do not interpret `native_live_append_tail_only`; not run by review stop after parity pass.
- [x] 5.3 Do not interpret `native_restored_capsule_append_tail_only`; not run by review stop after parity pass.
- [x] 5.4 No capsule telemetry was produced because capsule controls were not run.
- [x] 5.5 Do not run Family 2, mini graph, GraphWalks, broad benchmarks, or noiseless evidence unless explicitly approved after Family 1.

## 6. Record Track 02 Artifacts

- [x] 6.1 Write `README.md` with research question, ladder stage reached, result, stop rule, and interpretation.
- [x] 6.2 Write `summary.json` with aggregate scores, selected route, decision, and hashes.
- [x] 6.3 Write `case-metrics.json` and `failure-classifications.json`.
- [x] 6.4 Write `commands.md`, `model-info.json`, and `artifact-manifest.json`.
- [x] 6.5 Do not write `capsule-contract.md` because KV capsule gates were not rerun.
- [x] 6.6 Keep prompt-bearing raw artifacts ignored under Track 01 benchmark paths.

## 7. Validate And Land

- [ ] 7.1 Run `openspec validate bridge-native-server-parity-for-kv-capsule --type change --strict`.
- [ ] 7.2 Run `openspec validate --all --strict`.
- [ ] 7.3 Confirm prompt-bearing artifacts remain ignored with `git status --ignored`.
- [ ] 7.4 Commit locally if coherent; do not push without explicit approval.
