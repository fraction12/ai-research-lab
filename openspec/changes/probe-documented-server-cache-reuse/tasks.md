## 1. Define Probe Contract

- [x] 1.1 Create OpenSpec proposal, design, tasks, and spec deltas for documented server cache reuse.
- [x] 1.2 Define controls, metrics, log evidence, artifact layout, stop rules, and interpretation before running.
- [x] 1.3 Validate the change with `openspec validate probe-documented-server-cache-reuse --type change --strict`.

## 2. Build Local Probe Runner

- [x] 2.1 Add ignore coverage for `benchmarks/documented-server-cache-reuse-*` prompt-bearing artifacts.
- [x] 2.2 Create an ignored local runner for deterministic codeword variants.
- [x] 2.3 Implement all five controls with explicit `id_slot: 0`.
- [x] 2.4 Record request payloads, prompt hashes, raw outputs, exact/contained-answer scores, timing, slot telemetry, and server-log index evidence.

## 3. Run On DushyantPC

- [x] 3.1 Sync the ignored runner to the DushyantPC checkout.
- [x] 3.2 Run the documented cache-reuse probe with the pinned GPT-OSS model and llama.cpp runner.
- [x] 3.3 Copy raw outputs, command records, and log/cache artifacts back to the Mac worktree.
- [x] 3.4 Stop before any GraphWalks or noiseless-evidence work.

## 4. Record Track 02 Artifacts

- [x] 4.1 Write `README.md` with research question, result, and interpretation.
- [x] 4.2 Write `summary.json` with aggregate scores, cache-evidence decision, and semantic decision.
- [x] 4.3 Write `case-metrics.json` and `failure-classifications.json`.
- [x] 4.4 Write `commands.md`, `model-info.json`, `artifact-manifest.json`, and `server-log-index.json`.

## 5. Validate And Land

- [x] 5.1 Run relevant OpenSpec validation.
- [x] 5.2 Run `openspec validate --all --strict`.
- [x] 5.3 Confirm prompt-bearing artifacts remain ignored.
- [x] 5.4 Commit locally if coherent; do not push without explicit approval.
