## 1. Design And Provenance Gate

- [ ] 1.1 Commit or preserve the paper-facing experiment design doc under Track 02 docs.
- [ ] 1.2 Confirm `flashcache_correctness_eval.py list-datasets` reports `google/IFEval` and `openai/graphwalks`.
- [ ] 1.3 Pin or record the HF snapshot/revision used for candidate materialization.
- [ ] 1.4 Define the exact experiment id and ignored raw artifact directories.

## 2. Candidate Materialization

- [ ] 2.1 Build deterministic IFEval candidate pool from `google/IFEval` with supported deterministic checks.
- [ ] 2.2 Build deterministic GraphWalks `parents` candidate pool from `openai/graphwalks`.
- [ ] 2.3 Record source row ids or offsets, row hashes, prompt hashes, transform version, scorer version, and candidate selection metadata.
- [ ] 2.4 Verify no handmade benchmark cases enter the HF candidate pools.

## 3. Runner And Smoke Gates

- [ ] 3.1 Run 3-codeword and 3-key-value synthetic preflight through Gemma 4 12B using the lower-level sequence-file route.
- [ ] 3.2 Verify `full_visible`, `fresh_tail_only`, `native_live_append`, and `native_restored_capsule_append` behave as expected on preflight.
- [ ] 3.3 Run a 10-case HF live-append gate per family before the full matrix.
- [ ] 3.4 Stop and classify the route if native live append does not match full-visible quality on full-visible-passing cases.

## 4. Full-Visible Calibration And Cohort Selection

- [ ] 4.1 Run full-visible calibration on IFEval candidates.
- [ ] 4.2 Run full-visible calibration on GraphWalks candidates.
- [ ] 4.3 Select target cohorts of up to 50 full-visible-passing cases per family.
- [ ] 4.4 Record selected counts, rejected counts, thresholds, and whether each family is paper-parity eligible or diagnostic only.

## 5. Primary Control Matrix

- [ ] 5.1 Run `full_visible` for selected cases.
- [ ] 5.2 Run `fresh_tail_only` for selected cases.
- [ ] 5.3 Run `native_live_append` for selected cases.
- [ ] 5.4 Run `native_restored_capsule_append` for selected cases.
- [ ] 5.5 Run `wrong_capsule_negative` for selected cases.
- [ ] 5.6 Run `documented_full_prompt_cache_resend` for selected cases where the server route is available.

## 6. Secondary GraphWalks Analysis

- [ ] 6.1 Run `fresh_compact_evidence_only` on selected GraphWalks cases.
- [ ] 6.2 Run `capsule_plus_compact_evidence_tail` on selected GraphWalks cases.
- [ ] 6.3 Run `compact_tail_no_evidence` on selected GraphWalks cases.
- [ ] 6.4 Classify repairs as evidence scheduling, prompt protocol, hidden KV contribution, model weakness, scorer/parser issue, or ambiguity.

## 7. Amortization And Performance

- [ ] 7.1 Run repeated-tail amortization at repeat counts 1, 2, 5, 10, and 20 where runtime allows.
- [ ] 7.2 Separate capsule creation cost, save cost, restore cost, prompt eval cost, decode cost, and total wall time.
- [ ] 7.3 Compute speedup and token reduction versus full-visible resend for one-shot and amortized views.

## 8. Summary And Validation

- [ ] 8.1 Write Track 02 summary artifacts: `README.md`, `summary.json`, `case-metrics.json`, `control-matrix.json`, `candidate-calibration.json`, `amortization.json`, `failure-classifications.json`, `model-info.json`, `commands.md`, `artifact-manifest.json`, and `paper-methods-notes.md`.
- [ ] 8.2 Preserve prompt-bearing raw artifacts under ignored Track 01 benchmark directories and record hashes in the manifest.
- [ ] 8.3 Validate the OpenSpec change with `openspec validate run-hf-kv-capsule-paper-benchmark --type change --strict`.
- [ ] 8.4 Validate the repo with `openspec validate --all --strict`.
- [ ] 8.5 Report final paper-eligible claims, disallowed claims, failure taxonomy, artifact paths, and dirty worktree status.
