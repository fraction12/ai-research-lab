## 1. Materialize Focused Inputs

- [x] 1.1 Recreate a local prompt-bearing GraphWalks candidate file under `research/01-ssd-native-inference-current/benchmarks/correctness-eval-inputs/graphwalks-six-case-ladder-2026-06-03/`.
- [x] 1.2 Filter and verify exactly `graphwalks-6`, `graphwalks-9`, `graphwalks-11`, `graphwalks-13`, `graphwalks-16`, and `graphwalks-19`.
- [x] 1.3 Write an initial artifact manifest with case ids, source ids, prompt hashes, prompt byte counts, source evidence paths, and local prompt-bearing input paths.

## 2. Check Existing Control Coverage

- [x] 2.1 Confirm whether existing `flashcache_correctness_eval.py run` and `score` commands can run full-prompt replay variance, session-tail replay, reset/restore sanity, and scorer/parser brittleness checks without code changes.
- [x] 2.2 Determine whether visible-prefix/session-formatted control can be represented by local case composition without modifying Track 01 harness code.
- [x] 2.3 Determine whether stronger tail instructions or answer hints can be represented by local case composition without modifying Track 01 harness code.
- [x] 2.4 If a required control cannot be expressed, document the missing control surface before making any Track 01 harness change.

## 3. Implement Minimal Missing Control Surfaces If Needed

- [x] 3.1 Add only the smallest CLI or case-construction support needed for visible-prefix/session-formatted control, if local composition is insufficient.
- [x] 3.2 Add only the smallest CLI or case-construction support needed for stronger tail hints, if local composition is insufficient.
- [x] 3.3 Add focused unit tests for any Track 01 harness changes.
- [x] 3.4 Run `cd research/01-ssd-native-inference-current && python3 -m unittest discover -s tests` if Track 01 code changes are made.

## 4. Execute Focused Controls After Approval

- [x] 4.1 Run full-prompt replay variance on the six selected cases and record raw responses, scores, commands, timing, and model metadata.
- [x] 4.2 Run visible-prefix/session-formatted control and record raw responses, scores, commands, timing, and model metadata.
- [x] 4.3 Run stronger tail instructions or answer hints and record raw responses, scores, commands, timing, and model metadata.
- [x] 4.4 Run reset/restore sanity checks and record slot/cache telemetry, raw responses, scores, commands, timing, and model metadata.
- [x] 4.5 Run scorer/parser brittleness checks and record raw output, extracted answer, parsed node set, reference node set, precision, recall, F1, and parse errors.
- [x] 4.6 Run stronger-model control if practical; otherwise record why it is not practical.

## 5. Summarize Failure Attribution

- [x] 5.1 Write `research/02-quality-gated-stateful-kv-reuse/experiments/graphwalks-six-case-ladder-2026-06-03/commands.md`.
- [x] 5.2 Write `research/02-quality-gated-stateful-kv-reuse/experiments/graphwalks-six-case-ladder-2026-06-03/model-info.json`.
- [x] 5.3 Write `research/02-quality-gated-stateful-kv-reuse/experiments/graphwalks-six-case-ladder-2026-06-03/summary.json`.
- [x] 5.4 Write `research/02-quality-gated-stateful-kv-reuse/experiments/graphwalks-six-case-ladder-2026-06-03/failure-taxonomy.md`.
- [x] 5.5 Write `research/02-quality-gated-stateful-kv-reuse/experiments/graphwalks-six-case-ladder-2026-06-03/failure-classifications.json` with one classification row per case.
- [x] 5.6 Validate with `openspec validate --all --strict` and relevant Track 01 tests if code changed.
