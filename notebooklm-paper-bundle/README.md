# NotebookLM Paper Bundle

This folder is a copied source bundle for the KV capsule / programmatic tool-interface paper work. Originals remain in their normal repo locations.

## Start Here

- `research/02-quality-gated-stateful-kv-reuse/paper-publication-plan-2026-06-07.md`
- `research/02-quality-gated-stateful-kv-reuse/paper-defense-memo-2026-06-04.md`
- `research/02-quality-gated-stateful-kv-reuse/experiments/paper-grade-code-mode-kv-capsule-evaluation-2026-06-05/selected-cohort-findings.md`
- `research/02-quality-gated-stateful-kv-reuse/experiments/paper-grade-code-mode-kv-capsule-evaluation-2026-06-05/selected-cohort-summary.json`
- `research/02-quality-gated-stateful-kv-reuse/experiments/paper-grade-code-mode-kv-capsule-evaluation-2026-06-05/repeated-work-speed-findings.md`
- `research/02-quality-gated-stateful-kv-reuse/experiments/paper-grade-code-mode-kv-capsule-evaluation-2026-06-05/repeated-work-speed-summary.json`
- `research/02-quality-gated-stateful-kv-reuse/experiments/nonhandmade-code-mode-kv-agent-benchmark-2026-06-05/bfcl-primary-50-v5-summary.md`

## Key Code

- `research/01-ssd-native-inference-current/benchmarks/code_mode_kv_capsule_agent_harness.py`
- `research/01-ssd-native-inference-current/benchmarks/code_mode_kv_capsule_model_loop_runner.py`
- `research/01-ssd-native-inference-current/benchmarks/bfcl_code_mode_kv_adapter.py`
- `research/01-ssd-native-inference-current/benchmarks/paper_campaign_selected_cohort.py`
- `research/01-ssd-native-inference-current/benchmarks/paper_campaign_repeated_work_speed.py`
- `research/01-ssd-native-inference-current/tests/`

## What This Supports

Core claim: a KV-capsule harness can let the same local model reuse stable tool/context knowledge through restored hidden state instead of repeatedly carrying or compacting that context as text.

Evidence lanes:

- Mechanism: restored KV state matches native live append under controls.
- Interface: the compact programmatic tool-interface harness preserves hidden-prefix tool-use behavior.
- Runtime comparison: the repeated-work run compares the KV-capsule harness against a Codex/Ollama text-compaction harness using Gemma 4.

## Full File List

See `FILE_INDEX.txt`.
