## 1. Source And Provenance Audit

- [x] 1.1 Identify the exact BFCL source to use, including dataset or repo location, revision/commit, license note, available categories, scorer entrypoints, and local materialization command.
- [x] 1.2 Identify tau-bench/tau2-bench follow-on source details, including repo revision, domains, task counts, scorer/state-checker entrypoints, license note, and integration blockers.
- [x] 1.3 Identify ToolSandbox follow-on source details, including repo/paper source, scenario categories, scorer/state-checker availability, license note, and integration blockers.
- [x] 1.4 Write `source-audit.json` draft data and a short source-audit note with source URLs, revisions, categories, scorer status, and risk ranking.
- [x] 1.5 Confirm the first execution stage will use BFCL and record why tau-bench/tau2-bench and ToolSandbox are deferred until BFCL smoke gates pass.

## 2. Benchmark Case Materialization

- [x] 2.1 Define the external benchmark case schema with source id, revision, category, row id/offset, row hash, source fields used/excluded, stable prefix hash, volatile tail hash, full prompt hash, transform version, scorer version, `primary_eligible`, `primary_eligibility_reason`, and `prefix_dependency_class`.
- [x] 2.2 Implement or extend a materializer that converts BFCL rows into the Code-mode KV benchmark case schema without embedding handmade primary cases.
- [x] 2.3 Implement a no-model candidate dry run that materializes at least five BFCL rows and verifies expected function/tool calls can be reconstructed from source metadata.
- [x] 2.4 Add deterministic row sampling by category so BFCL smoke and selected cohorts can be rebuilt from revision plus seed.
- [x] 2.5 Write candidate calibration metadata under ignored raw paths and committed summary hashes under the Track 02 experiment path.

## 3. Scorer And Adapter Integrity

- [x] 3.1 Integrate BFCL-native scoring where available, or implement a deterministic scorer adapter that preserves expected function names, arguments, call multiplicity, irrelevance/no-call behavior, and category-specific constraints.
- [x] 3.2 Record unsupported BFCL scorer features separately from failures and mark categories with partial scorer support as diagnostic-only.
- [x] 3.3 Add tests for BFCL scorer adapter parsing, expected call comparison, argument normalization, no-call cases, and malformed model output.
- [x] 3.4 Add tests that reject rows without external provenance from primary cohorts.
- [x] 3.5 Add tests that fresh-tail and wrong-capsule pass results are flagged as leakage/protocol failures for prefix-dependent rows.

## 4. Seven-Control Runner Integration

- [x] 4.1 Extend the existing Code-mode KV capsule runner to accept external benchmark case records and preserve the same seven control ids.
- [x] 4.2 Ensure `code_mode_full_visible`, `code_mode_native_live_append`, and `code_mode_restored_kv_capsule` use identical benchmark stable-prefix/tail transforms except for visibility/persistence route.
- [x] 4.3 Ensure `code_mode_fresh_tail_only` and `code_mode_wrong_capsule_negative` cannot see the correct stable prefix.
- [x] 4.4 Ensure `direct_full_visible_tools` and `compact_visible_evidence_code_mode` are reported as secondary controls, not as main KV capsule evidence.
- [x] 4.5 Record per-control prompt tokens, timing, capsule route, sequence metadata, hashes, expected/parsed call and argument hashes, `template`, `template_alias`, `alias_registry_version`, `host_filled_args`, `final_source`, scorer result, parser status, and failure class.

## 5. Local Tests And Dry Runs

- [x] 5.1 Run Python compile checks for the changed benchmark runner, materializer, and scorer modules.
- [x] 5.2 Run unit tests for the existing handmade Code-mode KV harness to ensure the 30-case path was not broken.
- [x] 5.3 Run unit tests for the new BFCL materializer/scorer/summary path.
- [x] 5.4 Run a local no-model BFCL adapter dry run and verify artifact manifests contain source hashes and prompt hashes.
- [x] 5.5 Run `openspec validate run-nonhandmade-code-mode-kv-agent-benchmark --type change --strict`.

## 6. DushyantPC BFCL Smoke

- [x] 6.1 Confirm DushyantPC is reachable, GPU-enabled, idle, and has no duplicate Python or llama.cpp runs active.
- [x] 6.2 Sync the current runner, tests, OpenSpec plan, and experiment design to the Track 2/DushyantPC working tree as needed.
- [x] 6.3 Run a 10-row BFCL smoke across available categories through all seven controls on Gemma 4 12B.
- [x] 6.4 Stop and classify failures if full-visible Code-mode fails due to adapter/scorer bugs, native live append fails while full-visible passes, restored capsule fails while native live append passes, or negative controls pass on prefix-dependent rows.
- [x] 6.5 Write smoke `summary.json`, `control-matrix.json`, `failure-classifications.json`, `commands.md`, and `artifact-manifest.json`.

## 7. Primary BFCL Cohort

- [ ] 7.1 Run BFCL candidate calibration to find up to 50 to 100 full-visible-passing rows across selected categories.
- [ ] 7.2 Select the primary cohort only from `code_mode_full_visible` passing rows and record selected/rejected/leaked/diagnostic counts.
- [ ] 7.3 Run the selected BFCL cohort through all seven controls with row-level JSONL flushing.
- [ ] 7.4 Compute live/restored quality parity, response-hash parity, generated-token hash parity where available, restored-only failures, fresh-tail leaks, wrong-capsule failures, direct-tool baseline gaps, compact-evidence effects, prompt-token savings, one-shot timing, and amortized timing.
- [ ] 7.5 Write committed Track 02 summary artifacts and keep prompt-bearing raw artifacts under ignored Track 01 benchmark paths.

## 8. Follow-On Benchmark Decision

- [ ] 8.1 Review BFCL smoke/cohort failure modes with Track 2 before starting tau-bench/tau2 or ToolSandbox.
- [ ] 8.2 Choose the next source based on the BFCL result: tau-bench/tau2 for long-horizon policy/state tasks, or ToolSandbox for state dependency/canonicalization/insufficient-information stress.
- [ ] 8.3 Implement only a small follow-on smoke first, preserving the same seven controls where supported.
- [ ] 8.4 Mark unsupported controls or scorer features explicitly instead of silently adapting the benchmark into a different task.

## 9. Analysis, Claims, And Validation

- [x] 9.1 Write the final `README.md`, `paper-methods-notes.md`, and `disallowed-claims.md` for the non-handmade benchmark experiment.
- [ ] 9.2 Update or prepare benchmark summary tooling to report source benchmark, task family, control outcomes, negative-control status, live/restored parity, efficiency, and artifact paths.
- [ ] 9.3 Ask Track 2 for a skeptical paper-claim review before presenting the result as paper-grade.
- [ ] 9.4 Run relevant unit tests, OpenSpec validation for this change, and `openspec validate --all --strict`.
- [ ] 9.5 Report the final answer with source links, artifact paths, allowed claims, disallowed claims, unresolved risks, and dirty worktree status.
