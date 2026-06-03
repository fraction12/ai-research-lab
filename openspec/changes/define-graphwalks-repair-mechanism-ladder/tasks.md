## 1. Confirm Control Feasibility

- [x] 1.1 Verify the existing correctness runner support for `full`, `session-tail`, scoring, JSON answer protocol, cache telemetry, and local derived case files.
- [x] 1.2 Determine whether a true live no-restore control can be run through an existing lower-level wrapper or requires a minimal new correctness runner mode.
- [x] 1.3 Determine which anchor-span recompute controls can be represented by deterministic local case composition.
- [x] 1.4 Write `research/02-quality-gated-stateful-kv-reuse/experiments/graphwalks-repair-mechanism-ladder-2026-06-03/control-feasibility.md`.

## 2. Materialize Focused Inputs

- [x] 2.1 Reuse or recreate the six selected GraphWalks cases under `research/01-ssd-native-inference-current/benchmarks/correctness-eval-inputs/graphwalks-repair-mechanism-ladder-2026-06-03/`.
- [x] 2.2 Verify the fixed case ids are exactly `graphwalks-6`, `graphwalks-9`, `graphwalks-11`, `graphwalks-13`, `graphwalks-16`, and `graphwalks-19`.
- [x] 2.3 Create deterministic derived case files for anchor-span recompute controls.
- [x] 2.4 Create deterministic derived case files for prompt visibility controls.
- [x] 2.5 Write or update `artifact-manifest.json` with input paths, prompt hashes, prompt byte counts, source evidence paths, and derived construction rules.

## 3. Implement Minimal Missing Control Surface If Required

- [x] 3.1 Add a minimal live no-restore correctness runner mode only if no existing command can express the control.
- [x] 3.2 Ensure the new mode records mode id, prompt hashes, timing, session setup telemetry, and raw model output in the existing response JSONL shape.
- [x] 3.3 Add focused Track 01 tests for any new mode or helper.
- [x] 3.4 Run relevant Track 01 tests if any Track 01 harness code changes are made.

## 4. Execute Focused Repair Controls After Approval

- [x] 4.1 Run live no-restore control for the fixed six cases and record raw responses, scores, timing, command lines, and model metadata.
- [x] 4.2 Run restored session-tail baseline in the new artifact directory for comparison if needed.
- [x] 4.3 Run anchor-span recompute controls for the fixed six cases and record raw responses, scores, timing, cache telemetry, and derived prompt metadata.
- [x] 4.4 Run prompt visibility controls for the fixed six cases and record raw responses, scores, timing, and derived prompt metadata.
- [x] 4.5 Run position and compatibility probes using recorded metadata, prompt hashes, token counts, context size, answer protocol, backend version, and restore telemetry.

## 5. Summarize Mechanism, Repair, And Fallback

- [x] 5.1 Write `commands.md` with exact commands that were run on DushyantPC.
- [x] 5.2 Write `model-info.json` with exact machine, model, quantization, backend, context size, and command-line metadata.
- [x] 5.3 Write `prior-art-mechanism-map.md` mapping repo-local paper harvest evidence to the repair mechanisms and novelty boundary.
- [x] 5.4 Write `summary.json` with aggregate control results, timings, artifact hashes, and main findings.
- [x] 5.5 Write `repair-outcomes.json` with one row per case and repair control.
- [x] 5.6 Write `failure-classifications.json` with updated per-case mechanism classifications.
- [x] 5.7 Write `fallback-policy.md` with one conservative policy decision per fixed case.

## 6. Validate

- [x] 6.1 Run `npx --yes @fission-ai/openspec@latest validate --all --strict`.
- [x] 6.2 Confirm no broad benchmarks were run for this change.
- [x] 6.3 Confirm raw prompt-bearing and model-output artifacts remain ignored while committed summaries preserve paths and hashes.
