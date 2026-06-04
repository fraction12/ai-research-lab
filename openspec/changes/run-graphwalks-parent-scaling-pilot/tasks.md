## 1. OpenSpec Design Gate

- [x] Create `run-graphwalks-parent-scaling-pilot` OpenSpec change.
- [x] Define research question, scope, controls, metrics, artifact layout, failure taxonomy, and stop rules.
- [x] Validate the change with `openspec validate --changes run-graphwalks-parent-scaling-pilot --strict`.
- [x] Validate the repository with `openspec validate --all --strict`.

## 2. Preserve Completed Track 02 Work

- [x] Confirm the worktree sees `4578d7f` and preserves the paper-defense memo.
- [x] Validate completed `visible-evidence-slice-repair` OpenSpec work.
- [x] Create a local checkpoint commit for completed Track 02 visible-evidence artifacts before the scaling pilot.
- [x] Keep prompt-bearing raw artifacts under ignored Track 01 benchmark paths.
- [ ] Do not push unless explicitly asked.

## 3. Build Pilot Cohort and Evidence Slices

- [x] Build deterministic 50-case GraphWalks `parents` cohort under ignored Track 01 input paths.
- [x] Annotate answer-size, evidence edge count/bytes, duplicate edge, relevant-edge-position, prefix-length, and full-visible-pass buckets.
- [x] Extract incoming-edge evidence from stable graph prefix and target node only.
- [x] Record evidence hashes, edge counts, bytes, and token counts where available.
- [x] Confirm reference answer nodes are not used to construct evidence slices.

## 4. Run Control Matrix

- [x] Run `full_visible_compact_prompt` for sampled cases.
- [x] Run `hidden_prefix_session_tail` for sampled cases.
- [x] Run `hidden_prefix_compact_tail_no_evidence` for sampled cases.
- [x] Run `hidden_prefix_compact_visible_evidence_tail` for sampled cases.
- [x] Run `fresh_compact_visible_evidence_only` for sampled cases.
- [x] If runtime or blockers prevent the full 50-case matrix, stop at a deterministic 10/20-case slice and record the deviation.

## 5. Import and Analyze Results

- [x] Write Track 02 summaries under `research/02-quality-gated-stateful-kv-reuse/experiments/graphwalks-parent-scaling-pilot-2026-06-04/`.
- [x] Include `README.md`, `summary.json`, `case-metrics.json`, `bucket-analysis.json`, `failure-classifications.json`, `evidence-slices.json`, `commands.md`, `model-info.json`, and `artifact-manifest.json`.
- [x] Report scores by control, all-case view, full-visible-pass subset, hidden-prefix-fail subset, repairable hidden-prefix failures, fresh-evidence-only matches, and compact-no-evidence repairs.
- [x] Classify failures as model weakness, prompt protocol issue, scorer/parser brittleness, session/cache semantic issue, position/compatibility issue, runtime/storage issue, or ambiguity.
- [x] Preserve model hash, runner hash, backend flags, exact commands, prompt hashes, raw response hashes, and slot/cache telemetry.

## 6. Final Validation and Reporting

- [x] Re-run `openspec validate --changes run-graphwalks-parent-scaling-pilot --strict`.
- [x] Re-run `openspec validate --all --strict`.
- [x] Report exact artifact paths, scores, subset analyses, model/runner hashes, and final worktree clean/dirty status.
