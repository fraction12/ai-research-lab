## Context

The current strongest result is not "KV caching makes Gemma smarter." It is narrower and more defensible:

> On controlled and BFCL-derived tool-use tasks, restored llama.cpp sequence-file state can preserve native-live append behavior for a local Gemma 4 12B Code-mode agent, while fresh-tail and wrong-capsule controls stay closed.

The paper must be built around that claim boundary. The repo already contains:

- Mechanism evidence: `research/02-quality-gated-stateful-kv-reuse/experiments/gemma4-kv-capsule-replication-2026-06-05/`.
- Handmade agent-like viability evidence: `research/02-quality-gated-stateful-kv-reuse/experiments/code-mode-kv-capsule-agent-harness-2026-06-05/`.
- External BFCL pilot evidence: `research/02-quality-gated-stateful-kv-reuse/experiments/nonhandmade-code-mode-kv-agent-benchmark-2026-06-05/`.
- Prior positioning and failure discipline: `research/02-quality-gated-stateful-kv-reuse/paper-defense-memo-2026-06-04.md` and `failure-atlas.md`.

The existing BFCL primary-50 run is valuable pilot evidence:

- `direct_full_visible_tools`: 34/50.
- `code_mode_full_visible`: 37/50.
- `code_mode_native_live_append`: 35/50.
- `code_mode_restored_kv_capsule`: 35/50.
- `code_mode_fresh_tail_only`: 0/50, negative gate closed.
- `code_mode_wrong_capsule_negative`: 0/50, negative gate closed.
- `compact_visible_evidence_code_mode`: 11/50.
- Native live append and restored KV capsule had zero case-level disagreements.
- Restored capsule was not faster in that cohort.

This design turns the next phase into a paper-grade campaign that can be run later with one execution instruction.

## Paper Question

Can a local tool-using agent safely replace repeated visible stable context and tool schemas with restored model state plus a compact Code-mode interface, while preserving benchmark quality under strict negative controls?

## Primary Claim Shape

Allowed target claim:

> Quality-gated restored KV state can preserve native-live append behavior for local Code-mode tool-use tasks, and the control ladder identifies when hidden state is valid, leaked, degraded, or should fall back to visible context.

Secondary claim if evidence supports it:

> Code-mode tool-surface compression can improve or preserve tool-use quality compared with direct visible tool-schema exposure on some task families.

Efficiency claim only if evidence supports it:

> Amortized restored-state execution reduces repeated visible prompt cost for large stable prefixes or repeated volatile tails after capsule save/restore overhead is included.

Disallowed by default:

- Do not claim KV capsules make the model generally smarter.
- Do not claim new KV caching or new prompt caching as the novelty.
- Do not claim speedup from the existing BFCL primary-50 result.
- Do not claim official BFCL leaderboard comparability unless the official scoring path and submission constraints are satisfied.
- Do not use compact visible evidence as hidden-KV evidence.
- Do not blend handmade viability rows into primary external benchmark results.

## Experiment Spine

The paper campaign has five stages.

### Stage 0: Reproducibility And Readiness

Purpose: prove the repo, model profile, DushyantPC runtime, and existing pilot artifacts are ready before any long run.

Checks:

- Worktree clean or explicitly recorded dirty state.
- Latest `main` fetched.
- DushyantPC reachable.
- RTX 3060 visible and not saturated.
- No duplicate `python`, `llama-cli`, `llama-completion`, `llama-server`, or stale benchmark processes from prior runs.
- Gemma 4 12B profile resolves the intended Ollama blob or pinned GGUF.
- llama.cpp b9512 CUDA route exposes sequence-file state symbols and uses `llama.dll`.
- Raw prompt-bearing paths are ignored.
- Unit tests and OpenSpec validation pass.

Output:

- `execution-readiness.json`
- `commands.md`
- `artifact-manifest.json`

### Stage 1: BFCL Primary Expansion

Purpose: turn the BFCL primary-50 pilot into a paper-grade external benchmark result.

Default scope:

- Candidate pool: at least 500 BFCL rows when available from supported categories.
- Primary cohort target: 200 full-visible-passing rows.
- Minimum paper-eligible cohort: 100 full-visible-passing rows.
- Runs below 500 candidate rows are smoke or diagnostic probes only. They may harden the harness, but they do not satisfy paper calibration.
- Categories: `simple`, `multiple`, `parallel`, `parallel_multiple`, `irrelevance/no-call` if scorer support is faithful, and selected executable/API-style rows if deterministic scoring is faithful.
- Multi-turn BFCL remains separate until single-turn categories are stable.

Controls per selected row:

1. `direct_full_visible_tools`
2. `code_mode_full_visible`
3. `code_mode_fresh_tail_only`
4. `code_mode_native_live_append`
5. `code_mode_restored_kv_capsule`
6. `code_mode_wrong_capsule_negative`
7. `compact_visible_evidence_code_mode`

Primary selection:

- A row enters the primary semantic parity cohort only if `code_mode_full_visible` passes.
- Rows where fresh-tail or wrong-capsule pass are excluded from hidden-prefix claims and classified.
- Rows requiring unsupported scorer features are diagnostic-only.
- The campaign stops short of full paper claims if fewer than 100 clean full-visible-passing rows remain after scorer-support and negative-control filters.

Success criterion:

- Restored KV capsule matches native live append quality within a predeclared non-inferiority margin.
- Default margin: no more than 1 restored-only failure per 50 full-visible-passing rows.
- Negative controls must remain closed for at least 98% of prefix-dependent selected rows, and every leak must be classified.

Paper-facing calibration outputs:

- Per-category selected/rejected/diagnostic counts for `simple`, `multiple`, `parallel`, `parallel_multiple`, and `irrelevance/no-call` where supported.
- Live-vs-restored parity: scorer pass/fail, response hash, normalized response hash, generated-token hash, parsed call hash, and quality fields.
- Restored-only failures, including parser/scorer/runtime/model classifications.
- Fresh-tail and wrong-capsule leakage counts and classifications by category.
- Code-mode vs direct-tool gaps and compact-visible-evidence effects.
- Prompt-token deltas, stable-prefix tokens, tail tokens, capsule save/restore time, total wall time, and capsule bytes.
- Provenance fields: BFCL revision, source row hash, transform hash, scorer version, model profile, llama.cpp route identity, and capsule SHA.

### Stage 2: Stateful-Agent Follow-On

Purpose: add a harder benchmark source so the paper is not only a function-calling paper.

Preferred order:

1. ToolSandbox small smoke, because state dependency, canonicalization, insufficient-information cases, and tool/state checking map directly to hidden-state validity.
2. tau-bench/tau2 smoke, because it adds longer-horizon policy and database-state agent tasks.

Default scope:

- Smoke first: 10-20 tasks through all supported controls.
- Primary follow-on only after smoke: 50-100 full-visible-passing tasks.
- Unsupported controls must be recorded, not silently approximated.

Benchmark mapping:

- Stable prefix: tool inventory, state, policy, Code-mode bridge, scenario constraints, and output contract.
- Volatile tail: current user/task turn.
- Scorer: native benchmark state checker or faithful deterministic adapter.

Success criterion:

- Same as BFCL where controls are supported: restored matches native live append on full-visible-passing rows, negatives stay closed, failures classified by layer.

### Stage 3: Model Matrix

Purpose: show whether the result is Gemma-specific, model-size-sensitive, or a general local-agent runtime pattern.

Required:

- Primary local model: Gemma 4 12B through the working llama.cpp sequence-file route.
- Smaller local model: one feasible local model/profile that can run the same harness, used to expose failure/scale behavior.
- Stronger quality ceiling: a stronger model or frontier API for full-visible/direct-tool quality comparison only if it cannot use the same KV route.

Optional:

- GPT-OSS historical profile rerun if the harness still supports it cleanly.
- Second quantization/profile for Gemma only if it answers a specific robustness question.

Rules:

- Do not compare KV capsule conditions across models unless the model supports the same state route.
- For models without KV capsule support, report only full-visible, direct-tool, and Code-mode quality baselines.
- Keep model-specific tokenizer/template/calibration notes separate.

### Stage 4: Amortization And Efficiency

Purpose: test speed and token claims only after semantic validity is established.

Required measurements:

- Stable prefix tokens.
- Volatile tail tokens.
- Full visible prompt tokens.
- Restored visible prompt tokens.
- Prompt eval time.
- Decode time.
- Capsule save time.
- Capsule restore time.
- Capsule bytes.
- Total wall time.
- Repeated-tail amortization for `N in {1, 2, 5, 10, 25}` where practical.

Success criterion:

- Efficiency is paper-claimable only if restored or cached execution beats full-visible resend after including capsule creation/save/restore overhead under a realistic repeated-tail workload.

If not:

- Report semantic viability without claiming speed.

## Artifact Plan

Committed Track 02 root:

```text
research/02-quality-gated-stateful-kv-reuse/experiments/paper-grade-code-mode-kv-capsule-evaluation-2026-06-05/
```

Ignored Track 01 raw root:

```text
research/01-ssd-native-inference-current/benchmarks/paper-grade-code-mode-kv-capsule-evaluation-2026-06-05/
```

Required committed files:

```text
README.md
summary.json
execution-readiness.json
source-audit.json
candidate-calibration.json
case-metrics.json
control-matrix.json
failure-classifications.json
amortization.json
model-matrix.json
model-info.json
commands.md
artifact-manifest.json
paper-methods-notes.md
paper-results-outline.md
disallowed-claims.md
periodic-checkups.jsonl
```

Prompt-bearing raw artifacts, raw model outputs, generated code, raw tool outputs, token arrays, state files, and capsule bytes must remain in ignored Track 01 paths. Committed artifacts may contain hashes, counts, timings, labels, and distilled failure classes.

## Execution Handoff

When Sir later says to execute this campaign, the orchestrator should:

1. Fetch latest repo and verify this OpenSpec change still validates.
2. Run Stage 0 readiness checks locally and on DushyantPC.
3. Start Stage 1 BFCL candidate calibration.
4. Stop after calibration if full-visible pass rate, scorer support, or negative leakage makes the primary cohort non-paper-eligible.
5. Run the selected BFCL cohort with JSONL flushing and periodic progress summaries.
6. Write committed Track 02 summaries and leave raw artifacts ignored.
7. Ask for or proceed under predeclared approval to Stage 2 follow-on smoke.
8. Run Stage 3 model matrix only after the primary Gemma result is summarized.
9. Run Stage 4 amortization only after semantic gates pass.
10. Produce a final paper-data package and a paper outline.

Periodic checkup behavior:

- On request, check active process health, GPU status, current row/control counts, failure counts, last JSONL timestamp, artifact sizes, and stop-rule triggers.
- Append each checkup to `periodic-checkups.jsonl`.
- Do not restart or alter a run during checkup unless the stop rules require it.

## Risks And Mitigations

- BFCL adapter drift: keep scorer versions and parser repair fields top-level.
- Host repair overclaim: report alias normalization, host-filled args, and finalization source.
- Speed disappointment: separate semantic and efficiency claims.
- Benchmark leakage: enforce fresh-tail and wrong-capsule negatives.
- Model weakness: gate primary rows on full-visible Code-mode pass.
- Long-run fragility: flush JSONL per row/control and make checkups idempotent.
- Prior-art crowding: position the contribution as correctness-gated local-agent hidden-state policy, not as a new cache primitive.
