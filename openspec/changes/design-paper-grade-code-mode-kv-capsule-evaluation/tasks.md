## 1. Campaign Spec And Validation

- [x] 1.1 Create OpenSpec proposal, design, tasks, and spec deltas for the paper-grade Code-mode + KV capsule evaluation campaign.
- [x] 1.2 Run `openspec validate design-paper-grade-code-mode-kv-capsule-evaluation --type change --strict`.
- [x] 1.3 Run `openspec validate --all --strict` or record why full validation is deferred.
- [x] 1.4 Review this campaign against the current BFCL primary-50 artifacts and update if the pilot summary changes.

## 2. Stage 0 Readiness Implementation

- [x] 2.1 Add or identify a readiness script that checks repo revision, dirty state, ignored raw paths, model profile, llama.cpp route, DushyantPC reachability, GPU status, and duplicate process state.
- [x] 2.2 Ensure readiness output writes `execution-readiness.json`.
- [x] 2.3 Add tests or dry-run checks for the readiness script where practical.

## 3. BFCL Primary Expansion

- [ ] 3.1 Materialize a deterministic BFCL candidate pool of at least 500 supported rows where available.
- [ ] 3.2 Run candidate calibration and select a target primary cohort of 200 full-visible-passing rows, with a minimum paper-eligible cohort of 100.
- [ ] 3.3 Preserve category balance across simple, multiple, parallel, parallel-multiple, irrelevance/no-call, and any executable/API categories with faithful scoring.
- [ ] 3.4 Run all seven controls on the selected primary cohort using Gemma 4 12B.
- [ ] 3.5 Compute live-vs-restored parity, restored-only failures, fresh-tail leaks, wrong-capsule leaks, direct-tool gaps, compact-evidence effects, prompt-token deltas, and timing.
- [ ] 3.6 Write Track 02 summary artifacts and keep raw artifacts under ignored Track 01 paths.

## 4. Stateful-Agent Follow-On

- [ ] 4.1 Audit ToolSandbox source, revision, license, scenarios, state checker, and integration blockers.
- [ ] 4.2 Implement or specify ToolSandbox materialization into the stable-prefix/volatile-tail/control schema.
- [ ] 4.3 Run a 10-20 task ToolSandbox smoke through all supported controls.
- [ ] 4.4 Decide whether ToolSandbox can support a 50-100 task primary follow-on or must remain diagnostic.
- [ ] 4.5 Audit tau-bench/tau2 as a second follow-on and record whether it should run before or after ToolSandbox primary.

## 5. Model Matrix

- [ ] 5.1 Confirm the pinned Gemma 4 12B profile for primary paper runs.
- [ ] 5.2 Choose and configure one smaller local model profile for scale/failure behavior.
- [ ] 5.3 Choose one stronger quality-ceiling model or API baseline and define which controls it can honestly run.
- [ ] 5.4 Run model-matrix smokes before any broad model comparison.
- [ ] 5.5 Write `model-matrix.json` with supported controls, unsupported reasons, tokenizer/template notes, and claim boundaries.

## 6. Amortization And Efficiency

- [ ] 6.1 Add repeated-tail amortization runs for `N in {1, 2, 5, 10, 25}` where practical.
- [ ] 6.2 Include capsule save/restore overhead in every efficiency calculation.
- [ ] 6.3 Report one-shot and amortized timing separately from semantic pass rates.
- [ ] 6.4 Mark speed claims disallowed unless restored/capsule execution beats full-visible resend under realistic repeated-tail workloads.

## 7. Periodic Checkups

- [x] 7.1 Add a checkup command or documented routine that reports active process health, GPU status, current row/control counts, failure counts, last JSONL timestamp, artifact sizes, and stop-rule triggers.
- [x] 7.2 Append every checkup to `periodic-checkups.jsonl`.
- [x] 7.3 Ensure checkups do not mutate or restart active runs unless a stop rule requires it.

## 8. Paper Package

- [ ] 8.1 Write `paper-methods-notes.md` from the final campaign data.
- [ ] 8.2 Write `paper-results-outline.md` with tables/figures needed for the paper.
- [ ] 8.3 Update `disallowed-claims.md` based on the final evidence.
- [ ] 8.4 Ask for skeptical review of claims before drafting the paper.
- [ ] 8.5 Produce the final paper-data handoff with artifact paths, allowed claims, disallowed claims, unresolved risks, and reproduction commands.
