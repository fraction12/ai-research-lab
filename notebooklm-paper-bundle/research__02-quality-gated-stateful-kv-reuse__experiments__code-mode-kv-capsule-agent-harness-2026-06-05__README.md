# Code Mode + KV Capsule Agent Harness 2026-06-05

## Status

Stage `thirty-case-v9` completed on Gemma 4 12B through the llama.cpp CUDA sequence-file route.

Decision: `thirty-case-v9_passed_core_with_secondary_gap`.

The core Code-mode/KV controls passed on all 30 cases. Secondary baselines showed useful gaps: direct full-visible tools were less reliable on tool-path and retry/trace cases, and compact visible evidence was not enough for most multi-step and trace tasks.

## Control Summary

| Control | Gate pass | Answer contained | Interpretation |
| --- | ---: | ---: | --- |
| `code_mode_full_visible` | 30/30 | 30/30 | Code-mode bridge is viable when stable context is visible. |
| `code_mode_native_live_append` | 30/30 | 30/30 | Tail-only append after live prefix prefill works. |
| `code_mode_restored_kv_capsule` | 30/30 | 30/30 | Restored sequence-file capsule matches live append. |
| `code_mode_fresh_tail_only` | 30/30 | 0/30 | Negative control stayed negative. |
| `code_mode_wrong_capsule_negative` | 30/30 | 0/30 | Wrong capsule stayed negative. |
| `direct_full_visible_tools` | 19/30 | 23/30 | Secondary baseline gap: direct tools were fragile. |
| `compact_visible_evidence_code_mode` | 11/30 | 11/30 | Secondary ablation: compact evidence was insufficient. |

Live/restored hash parity was exact on all 30 cases for generated token hash, normalized response hash, and response hash.

## Mechanism Evidence

- Restored controls used `seq_file`.
- Stable prefix was not resent in tail deltas: 0/30 restored records had `delta_prompt_contains_stable_prefix`.
- Restored capsule size averaged about 208 MB.
- Sequence tokens saved/loaded averaged about 605.
- Mean visible prompt tokens dropped from about 337 for `code_mode_full_visible` to about 43 for `code_mode_restored_kv_capsule`.
- Mean prompt eval time dropped from about 3375 ms for `code_mode_full_visible` to about 423 ms for `code_mode_restored_kv_capsule`.
- Total restored wall time was still higher than native live append because save/restore overhead remains material in this prototype.

## Important Repair

The first 12-case model run exposed a Code-mode bridge brittleness, not a KV failure. Gemma emitted near-template names such as `max_failure_modulo` for the intended `max_failure_module` template. The adapter originally rejected those aliases, causing full-visible, live append, and restored capsule to fail identically on `parallel_aggregation-08`.

The runner now normalizes observed compiled-template aliases, records the canonical template plus alias, and flushes JSONL after every row. A targeted rerun and the full 12-case/30-case reruns passed the core controls after that repair.

## Interpretation

This is positive viability evidence for a local-agent runtime harness:

- Code mode made Gemma 4 more reliable than direct visible tool schemas on retry, policy, and trace-continuation cases.
- KV capsule restore preserved the same behavior as native live append while using only the volatile tail in the visible prompt.
- Fresh-tail and wrong-capsule controls stayed negative, so the task suite did not simply leak answers through the tail.
- Compact visible evidence alone was much weaker, so the result is not reducible to tiny visible summaries.

This is not yet a broad paper benchmark. The next paper-facing benchmark should reuse this exact control ladder on non-handmade task sources.
