# Paper Results Tables

Date: 2026-06-07

Purpose: paper-ready result tables derived from `paper-data-ledger.md` and constrained by `paper-claims-ledger.md`.

## Table 1: Selected 100-Case Control Ladder

Source: `research/02-quality-gated-stateful-kv-reuse/experiments/paper-grade-code-mode-kv-capsule-evaluation-2026-06-05/selected-cohort-summary.json`

| Control | Records | Gate pass | Paper interpretation |
| --- | ---: | ---: | --- |
| `code_mode_full_visible` | 100 | 100/100 | Full stable context plus programmatic tool interface succeeds on the selected cohort. |
| `code_mode_native_live_append` | 100 | 100/100 | Native live prefix+tail behavior succeeds. |
| `code_mode_restored_kv_capsule` | 100 | 100/100 | Restored KV capsule preserves native behavior on all selected cases. |
| `code_mode_fresh_tail_only` | 100 | 100/100 negative gate; 0 leaks | Tail alone did not leak enough to solve the selected cases. |
| `code_mode_wrong_capsule_negative` | 100 | 100/100 negative gate; 0 leaks | Wrong hidden state did not solve the selected cases. |
| `direct_full_visible_tools` | 100 | 91/100 | Direct visible tool schemas were weaker than the programmatic interface on this cohort. |
| `compact_visible_evidence_code_mode` | 100 | 19/100 | Compact visible evidence alone did not explain the hidden-state result. |

Use for: main mechanism result, negative controls, interface ablation.

Do not use for: speedup claim.

## Table 2: Selected Cohort Timing Boundary

Source: `research/02-quality-gated-stateful-kv-reuse/experiments/paper-grade-code-mode-kv-capsule-evaluation-2026-06-05/selected-cohort-summary.json`

| Control | Mean total ms | Median total ms | Paper interpretation |
| --- | ---: | ---: | --- |
| `code_mode_full_visible` | 6766.7 | 6252.9 | Fastest among the positive programmatic-interface controls in this run. |
| `code_mode_native_live_append` | 6782.7 | 6253.5 | Similar to full visible. |
| `code_mode_restored_kv_capsule` | 8513.8 | 8042.3 | Semantically correct but slower in this mechanism run. |
| `direct_full_visible_tools` | 8179.8 | 6979.3 | Weaker quality and slower than programmatic full visible here. |
| `compact_visible_evidence_code_mode` | 9434.8 | 8993.6 | Weak quality and slower than restored KV. |

Paper sentence: "The selected-cohort control ladder supports semantic preservation, not a low-level restore speed claim."

## Table 3: Repeated-Work Runtime Comparison

Sources:

- `research/02-quality-gated-stateful-kv-reuse/experiments/paper-grade-code-mode-kv-capsule-evaluation-2026-06-05/repeated-work-speed-summary.json`
- `research/02-quality-gated-stateful-kv-reuse/experiments/paper-grade-code-mode-kv-capsule-evaluation-2026-06-05/repeated-work-speed-findings.md`

| System lane | Run label | Pass | Cumulative wall | Visible input telemetry | Output tokens | Compaction events | Paper interpretation |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| KV capsule + programmatic tool interface | `bfcl-repeated-work-speed-v1-kv-resume` | 100/100 | 853,499 ms | 3,900 | 6,267 | 0 | Reuses stable context through restored hidden state and small visible tails. |
| Codex/Ollama regular tools, natural text compaction | `bfcl-repeated-work-codex-natural-chained-v1` | 86/100 | 11,813,816 ms | 245,774,883 reported cumulative visible input tokens | 9,068,626 | 89 | Practical text-threaded harness baseline with audited session compaction. |
| Codex/Ollama attempted compaction, no BFCL compaction events | `bfcl-repeated-work-speed-v1` | 87/100 | 11,521,048 ms | 243,088,507 reported visible input tokens | 8,170,400 | 0 | Historical attempted baseline; not the paper-grade compaction comparator. |

Paper sentence: "On the selected repeated-work stream, the KV-capsule harness led on pass rate, cumulative wall time, and reported visible-context burden versus the tested natural Codex/Ollama text-compaction route."

Boundary: do not call this prompt-identical; do not treat Codex visible-token telemetry as clean per-task accounting.

## Table 4: Natural Codex Failure Breakdown

Source: `research/02-quality-gated-stateful-kv-reuse/experiments/paper-grade-code-mode-kv-capsule-evaluation-2026-06-05/repeated-work-speed-findings.md`

| BFCL category | Codex pass | Codex fail | Notes |
| --- | ---: | ---: | --- |
| `java` | 14/17 | 3 | Several failures despite parseable call output. |
| `javascript` | 0/1 | 1 | Single-row category; do not overinterpret. |
| `multiple` | 21/25 | 4 | Wrong args / duplicate / extra call style failures noted. |
| `parallel` | 13/14 | 1 | Mostly strong but not perfect. |
| `parallel_multiple` | 13/17 | 4 | Larger failure share; useful for failure taxonomy. |
| `simple` | 25/26 | 1 | Strong but not perfect. |
| Total | 86/100 | 14 | Findings say one failure parsed zero calls; most failures were parseable but incorrect calls. |

Use for: failure taxonomy and discussion.

Do not use for: causal claim that compaction summaries caused the failures.

## Table 5: Supporting BFCL Primary-50 Result

Source: `research/02-quality-gated-stateful-kv-reuse/experiments/nonhandmade-code-mode-kv-agent-benchmark-2026-06-05/bfcl-primary-50-v5-summary.md`

| Control | BFCL pass | Mean total ms | Interpretation |
| --- | ---: | ---: | --- |
| `direct_full_visible_tools` | 34/50 | 10637.3 | Direct visible baseline. |
| `code_mode_full_visible` | 37/50 | 8858.8 | Programmatic interface was strongest positive lane. |
| `code_mode_native_live_append` | 35/50 | 8642.0 | Native prefix+tail comparator. |
| `code_mode_restored_kv_capsule` | 35/50 | 10360.2 | Matched native live append case outcomes exactly. |
| `code_mode_fresh_tail_only` | 0/50 | 14843.9 | Negative control stayed closed. |
| `code_mode_wrong_capsule_negative` | 0/50 | 9502.9 | Negative control stayed closed. |
| `compact_visible_evidence_code_mode` | 11/50 | 12303.2 | Compact visible evidence was weak. |

Use for: support/background.

Do not use for: headline claim over the selected 100-case result.

## Table 6: Claim-to-Evidence Map

| Claim | Evidence IDs | Result table(s) |
| --- | --- | --- |
| Restored KV preserves native live-append behavior under controls. | E1, E9, E10, E11, E12 | Tables 1, 5 |
| Negative controls show the task tails were prefix-dependent. | E1, E9, E10, E11, E12 | Tables 1, 5 |
| Programmatic tool interface beat direct visible tools on the selected cohort. | E1, E2 | Table 1 |
| Compact visible evidence alone did not explain the result. | E1, E3, E9, E10 | Tables 1, 5 |
| KV-capsule runtime compared favorably to Codex/Ollama text compaction on repeated stable-context work. | E5, E6, E8 | Tables 3, 4 |
| Selected-cohort mechanism run does not show restored KV speedup. | E4 | Table 2 |

## Table Review

- Tables 1 through 3 should appear in the main paper.
- Table 4 can appear as a compact failure-analysis table or appendix table.
- Table 5 belongs in supporting evidence or appendix.
- Table 6 is a drafting aid and can become an appendix "evidence map" if useful.
