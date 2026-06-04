## 1. Define Probe Contract

- [x] 1.1 Create OpenSpec proposal, design, tasks, and spec deltas for the semantic-continuation probe.
- [x] 1.2 Define controls, metrics, artifact layout, stop rules, and failure taxonomy before running the probe.
- [x] 1.3 Validate the change with `openspec validate probe-hidden-prefix-semantic-continuation --type change --strict`.

## 2. Build Local Probe Runner

- [x] 2.1 Add ignore coverage for `benchmarks/hidden-prefix-semantic-continuation-*` prompt-bearing artifacts.
- [x] 2.2 Create an ignored local runner that generates deterministic codeword and key/value cases.
- [x] 2.3 Implement `full_visible_prefix_plus_tail`, `fresh_tail_only`, and `restored_hidden_prefix_plus_tail` controls.
- [x] 2.4 Record prompt hashes, raw outputs, normalized outputs, exact-match pass/fail, contained-answer pass/fail, timing, and slot telemetry.

## 3. Run On DushyantPC

- [x] 3.1 Sync the ignored runner to the DushyantPC checkout.
- [x] 3.2 Run the probe using the pinned GPT-OSS model and llama.cpp runner.
- [x] 3.3 Copy raw outputs, command records, and cache telemetry back to the Mac worktree.
- [x] 3.4 Stop before any noiseless GraphWalks evidence rerun.
- [x] 3.5 Apply the codeword-gate stop rule and exclude the single non-codeword stray record from analysis.

## 4. Record Track 02 Artifacts

- [x] 4.1 Write `README.md` with the research question, result, and interpretation.
- [x] 4.2 Write `summary.json` with aggregate scores and semantic-continuation decision.
- [x] 4.3 Write `case-metrics.json` and `failure-classifications.json`.
- [x] 4.4 Write `commands.md`, `model-info.json`, and `artifact-manifest.json`.

## 5. Validate And Land

- [x] 5.1 Run relevant OpenSpec validation.
- [x] 5.2 Run `openspec validate --all --strict`.
- [x] 5.3 Confirm prompt-bearing artifacts remain ignored.
- [x] 5.4 Commit locally if the probe artifacts are coherent; do not push without explicit approval.
