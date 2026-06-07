# BFCL Primary 50 V5 Summary

Completed: 2026-06-06 UTC

## Run

- Run label: `bfcl-primary-50-tool-surface-v5`
- Host: `DushyantPC`
- Model profile: `gemma4-12b`
- Backend: `cuda_v13`
- Harness: `code_mode_kv_capsule_agent_harness_v8`
- Prompt protocol: `openclaw_code_mode_compiled_template_v1`
- Source benchmark: BFCL v3, Hugging Face revision `61fc0608cfd831fcfbbaa676ebdfef0ed963eeda`
- Controls per case: 7
- Cases: 50
- Records: 350
- Raw records path, ignored: `research/01-ssd-native-inference-current/benchmarks/nonhandmade-code-mode-kv-agent-benchmark-2026-06-05/raw/bfcl-primary-50-tool-surface-v5-model-loop-records.jsonl`
- Raw records sha256: `c3944cb70be872816e317055f206037c3927f1b25a43a253a8555d369c3cba95`
- Run-info sha256: `2b76d17f8f94b969d719df33cfde0a401e243254b76e07382cdb665464e5e40a`

## Headline Results

| Control | BFCL pass | Gate pass | Mean total ms |
| --- | ---: | ---: | ---: |
| `direct_full_visible_tools` | 34/50 | 34/50 | 10637.3 |
| `code_mode_full_visible` | 37/50 | 37/50 | 8858.8 |
| `code_mode_native_live_append` | 35/50 | 35/50 | 8642.0 |
| `code_mode_restored_kv_capsule` | 35/50 | 35/50 | 10360.2 |
| `code_mode_fresh_tail_only` | 0/50 | 50/50 | 14843.9 |
| `code_mode_wrong_capsule_negative` | 0/50 | 50/50 | 9502.9 |
| `compact_visible_evidence_code_mode` | 11/50 | 11/50 | 12303.2 |

For positive controls, gate pass means BFCL pass. For negative controls, gate pass means the control stayed closed.

## Task Bucket Split

| Bucket | Direct full | Code full | Native append | Restored capsule | Fresh tail | Wrong capsule | Compact evidence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `bfcl_simple` | 13/13 | 12/13 | 12/13 | 12/13 | 0/13 | 0/13 | 6/13 |
| `bfcl_multiple` | 10/13 | 10/13 | 10/13 | 10/13 | 0/13 | 0/13 | 2/13 |
| `bfcl_parallel` | 4/12 | 6/12 | 5/12 | 5/12 | 0/12 | 0/12 | 1/12 |
| `bfcl_parallel_multiple` | 7/12 | 9/12 | 8/12 | 8/12 | 0/12 | 0/12 | 2/12 |

## Interpretation

The strongest result is native append versus restored KV capsule parity: `code_mode_native_live_append` and `code_mode_restored_kv_capsule` had identical BFCL pass/fail outcomes on all 50 cases. There were zero case-level disagreements.

The negative controls stayed fully closed. `code_mode_fresh_tail_only` passed 0/50 and `code_mode_wrong_capsule_negative` passed 0/50. That supports the claim that these rows depended on the hidden/tool prefix and were not answerable from the volatile tail alone.

Code Mode outperformed direct visible tools on this cohort: `code_mode_full_visible` passed 37/50 versus 34/50 for `direct_full_visible_tools`. The clearest difference is in parallel and parallel-multiple rows, where direct visible schemas struggled more often.

Restored KV capsule did not beat full visible quality in this run. `code_mode_restored_kv_capsule` passed 35/50 versus 37/50 for `code_mode_full_visible`. The quality claim should be semantic preservation relative to native live append, not broad quality improvement over a full visible prompt.

Restored KV capsule was also not faster on this cohort. Mean total time was 10360.2 ms for restored KV capsule versus 8858.8 ms for Code-mode full visible and 8642.0 ms for native live append. The run supports semantic viability, not speedup. Future speed claims require larger stable prefixes, amortized repeated tails, or lower restore overhead.

## Harness Fixes Discovered During The Run

The primary run exposed measurement issues before producing a clean result. These were fixed and covered by tests before v5:

- Repaired doubled quote markers around model-authored JSON keys such as `""function_name""`.
- Added recovery for truncated outer `tool_calls` wrappers when the model emitted a clear `function_name` plus balanced `arguments` object.
- Prevented inner argument dictionaries such as `budget` or `gradeDict` from being misread as tool names.
- Extended the deterministic BFCL adapter scorer to handle nested expected argument structures, such as `budget: {"min": ..., "max": ...}` and nested grade dictionaries.

These fixes are measurement-instrument hardening, not benchmark hand-tuning. They preserve strict expected-call matching while accepting BFCL-compatible nested argument shapes and common Gemma4 tool-call formatting glitches.

## Claim Boundary

Allowed:

- Restored KV capsule matched native live append quality on this BFCL primary-50 cohort.
- Fresh-tail and wrong-capsule negative controls remained closed on all 50 rows.
- Code Mode was stronger than direct visible tool schemas on this measured cohort.
- The current implementation demonstrates semantic viability, not a performance win.

Disallowed:

- Do not claim restored KV capsules make the model generally smarter.
- Do not claim a speedup from this run.
- Do not claim official BFCL leaderboard comparability; this uses a deterministic adapter scorer.
- Do not use compact visible evidence as hidden-KV evidence.
