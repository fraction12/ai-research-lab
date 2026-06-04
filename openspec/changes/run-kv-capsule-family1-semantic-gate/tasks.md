## 1. Define Family 1 Gate

- [x] 1.1 Create proposal, design, tasks, and spec deltas for the reviewed Family 1 capsule gate.
- [x] 1.2 State the research question, controls, metrics, stop rules, and artifact boundary before model-bearing execution.
- [x] 1.3 Validate `run-kv-capsule-family1-semantic-gate` with OpenSpec strict validation.

## 2. Prepare Runner And Sync

- [x] 2.1 Add ignore coverage for `benchmarks/kv-capsule-family1-semantic-gate-*` prompt-bearing artifacts if needed.
- [x] 2.2 Sync DushyantPC to the Mac commit containing the parity bridge and this OpenSpec change without destructive commands.
- [x] 2.3 Create or copy an ignored native direct C API runner under the new raw path.
- [x] 2.4 Remove or make unreachable any server or broad benchmark execution path for this assignment.
- [x] 2.5 Run syntax checks before model-bearing execution.

## 3. Run Family 1 Controls

- [x] 3.1 Run `native_full_visible_prefix_plus_tail` on 3 simple codeword cases using canonical `add_special=true` full-prompt route.
- [x] 3.2 Stop if full-visible guard fails; guard passed 3/3 so the ladder advanced.
- [x] 3.3 Run `native_fresh_tail_only` and stop/quarantine if it unexpectedly contains the answer; fresh tail missed 0/3 as expected.
- [x] 3.4 Run `native_live_append_tail_only` and stop before restored capsule interpretation if it fails; live append passed 3/3.
- [x] 3.5 Run `native_restored_capsule_append_tail_only` only if live append passes; restored capsule passed 3/3.
- [x] 3.6 Do not run Family 2, mini graph, GraphWalks, broad benchmarks, or noiseless evidence.

## 4. Package Artifacts

- [x] 4.1 Write `README.md` with outcome, stop rule, and interpretation.
- [x] 4.2 Write `summary.json` with aggregate pass/fail, selected route, decision, timings, and state byte counts/hashes.
- [x] 4.3 Write sanitized `case-metrics.json` with no raw prompts, raw responses, token ID arrays, generated token arrays, top-k arrays, or state bytes.
- [x] 4.4 Write `failure-classifications.json`, `commands.md`, `model-info.json`, and `artifact-manifest.json`.
- [x] 4.5 Write `capsule-contract.md` because restored capsule ran.
- [x] 4.6 Confirm raw prompt-bearing artifacts remain ignored.

## 5. Validate And Land

- [x] 5.1 Run `openspec validate run-kv-capsule-family1-semantic-gate --type change --strict`; rechecked by orchestration on 2026-06-04.
- [x] 5.2 Run `openspec validate --all --strict`; rechecked by orchestration on 2026-06-04.
- [x] 5.3 Commit locally if coherent; landed as local commit `382e677` (`Record KV capsule Family 1 gate`) with no push.
