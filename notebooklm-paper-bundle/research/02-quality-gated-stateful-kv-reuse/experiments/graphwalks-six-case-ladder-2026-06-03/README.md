# GraphWalks Six-Case Ladder

Date: 2026-06-03

This directory records the focused Track 02 correctness ladder for the six GraphWalks cases where the prior full-prompt gate passed and session-tail failed.

## Scope

Fixed case set: `graphwalks-6`, `graphwalks-9`, `graphwalks-11`, `graphwalks-13`, `graphwalks-16`, and `graphwalks-19`.

## Result

- Full-prompt replay variance: 3 runs, 18/18 case attempts passed.
- Session-tail replay/reset-restore sanity: 3 runs, 0/18 case attempts passed.
- Visible-prefix/session-formatted control: 3/6 cases passed.
- Stronger tail hints: 0/6 cases passed; all produced malformed JSON/prose outputs.
- Stronger-model control: not practical in the same llama.cpp/GGUF harness.

## Main Finding

The six-case GraphWalks collapse reproduces on DushyantPC in the proper checkout. Full-prompt variance is not the cause. Basic save/restore telemetry does not show a runtime/storage failure. The likely interpretation is split: `graphwalks-13`, `graphwalks-16`, and `graphwalks-19` point strongly at restored-prefix/session-tail semantic non-equivalence, while `graphwalks-6`, `graphwalks-9`, and `graphwalks-11` also show prompt-format sensitivity.

## Artifacts

- `summary.json`: aggregate control results, timings, artifact hashes, and findings.
- `model-info.json`: machine, backend, model, and run parameters.
- `failure-taxonomy.md`: taxonomy used for interpretation.
- `failure-classifications.json`: one classification row per case.
- `commands.md`: setup and live commands.
