## 1. Design And Handoff

- [x] 1.1 Preserve the handoff-quality experiment plan under Track 02 docs.
- [x] 1.2 Confirm the plan links the OpenClaw Code mode note, local-agent runtime harness synthesis note, Gemma 4 KV capsule replication result, and failed HF benchmark validity lesson.
- [x] 1.3 Define the experiment id, raw artifact directories, committed summary directory, and artifact manifest schema.
- [x] 1.4 Confirm the implementation owner will not launch a large benchmark until smoke and viability gates pass.

## 2. Harness Contract And Fixtures

- [x] 2.1 Define the stable prefix template with agent rules, Code mode contract, catalog hash, policy invariants, workspace map, trace facts, and answer format.
- [x] 2.2 Define the volatile tail template with current task request, case id, and optional compact evidence slice.
- [x] 2.3 Build the hidden tool catalog fixture with deterministic search, describe, call, denial, stale id, and wrong-session behavior.
- [x] 2.4 Create task fixtures for six buckets: single-tool selection, dependent multi-tool calls, parallel aggregation, bounded retry, trace continuation, and denied/invalid tool access.
- [x] 2.5 Add fixture hashing for source fixture, stable prefix, tail, catalog, visible contract, policy set, and scorer version.

## 3. Code Mode Route

- [x] 3.1 Implement or select a simulated Code mode route that exposes only the execution interface to the model and keeps the full catalog hidden.
- [x] 3.2 Validate generated code or structured call plans before executing catalog calls.
- [x] 3.3 Record code validation status, syntax/runtime errors, timeout, memory/output limit flags, and tool-call transcript hashes.
- [ ] 3.4 If real OpenClaw Code mode is available, add it as a separate route with identical case ids and control ids rather than replacing the simulated route.
- [x] 3.5 Repair the model-bearing Gemma route so Code mode is a bounded OpenClaw-shaped `EXEC -> EXEC_RESULT -> FINAL` loop, not a one-shot final-answer generation.
- [x] 3.6 Parse strict `EXEC` JSON plus narrow Gemma/OpenClaw-style exec fragments while rejecting channel/thought text and model-authored host results as final answers.
- [x] 3.7 Execute parsed exec-code tool operations through the deterministic hidden catalog, append compact observations to the same llama sequence when needed, and record whether the final answer came from model text or an answer-bearing host tool result.

## 4. KV Capsule Integration

- [x] 4.1 Reuse the working Gemma 4 12B llama.cpp sequence-file route from the prior KV capsule replication.
- [x] 4.2 Add control ids for `code_mode_native_live_append`, `code_mode_restored_kv_capsule`, and `code_mode_wrong_capsule_negative`.
- [x] 4.3 Record capsule route, capsule id, sequence id where available, `n_past` where available, prefix token count, capsule bytes/hash, save timing, restore timing, prompt eval timing, decode timing, and total wall time.
- [x] 4.4 Ensure wrong-capsule, wrong-catalog, or wrong-session passes trigger a stop-rule classification.
- [x] 4.5 Add hidden-control guardrails proving native-live/restored runs append only tail, tool observations, and final prompts after prefix prefill or restore.

## 5. Control Matrix

- [x] 5.1 Run `direct_full_visible_tools` for each selected case.
- [x] 5.2 Run `code_mode_full_visible` for each selected case.
- [x] 5.3 Run `code_mode_fresh_tail_only` for each selected case.
- [x] 5.4 Run `code_mode_native_live_append` for each selected case.
- [x] 5.5 Run `code_mode_restored_kv_capsule` for each selected case.
- [x] 5.6 Run `code_mode_wrong_capsule_negative` for each selected case.
- [x] 5.7 Run `compact_visible_evidence_code_mode` for each selected case.
- [ ] 5.8 Optionally run `tool_search_no_code_mode` when hidden catalog search can be tested without generated programs.

## 6. Staged Runs

- [x] 6.1 Run a harness-only dry run with stubbed model outputs to validate fixture generation, scoring, and artifact writing.
- [x] 6.2 Rerun the two-case model smoke after the Code-mode loop repair across all required controls.
- [x] 6.3 Run a twelve-case viability suite with two cases per bucket.
- [x] 6.4 Run a thirty-case viability suite with five cases per bucket only if the twelve-case suite is interpretable.
- [x] 6.5 Stop and classify instead of scaling if full-visible fails, native live append fails, fresh tail-only leaks, restored diverges from live, or wrong-capsule unexpectedly passes.
- [x] 6.6 Do not run 12-case or 30-case model gates until direct full-visible and Code-mode full-visible pass the repaired two-case loop gate and negative controls remain negative.

## 7. Analysis And Summaries

- [x] 7.1 Write per-case records with quality, tool-use, code-validity, safety, capsule, prompt-size, timing, and failure-class fields.
- [x] 7.2 Summarize by task bucket, control id, full-visible-pass subset, fresh-tail-fail subset, live-append-pass subset, restored-vs-live mismatches, restored-vs-full-visible mismatches, and wrong-capsule outcomes.
- [x] 7.3 Compute prompt-token reduction and wall-time deltas versus direct full-visible and Code mode full-visible baselines.
- [x] 7.4 Classify each failure as task invalidity, model weakness, prompt protocol, Code mode contract, tool-catalog semantics, generated-code issue, capsule semantics, compact-evidence effect, scorer/parser brittleness, runtime/storage, transport, or ambiguous.
- [x] 7.5 Write disallowed claims and next recommended benchmark only after the viability results are known.
- [x] 7.6 Update the smoke analysis to distinguish missing tool-loop protocol, model tool-selection failures, final-copy failures, and hidden KV capsule divergence.

## 8. Artifacts And Validation

- [x] 8.1 Keep raw prompts, generated code, tool outputs, capsule files, and trace payloads under ignored Track 01 benchmark directories.
- [x] 8.2 Commit only distilled Track 02 experiment summaries and artifact manifests.
- [x] 8.3 Run `openspec validate probe-code-mode-kv-capsule-agent-harness --type change --strict`.
- [x] 8.4 Run `openspec validate --all --strict`.
- [x] 8.5 Report final artifact paths, validation results, dirty worktree status, and whether the probe is ready for implementation.
