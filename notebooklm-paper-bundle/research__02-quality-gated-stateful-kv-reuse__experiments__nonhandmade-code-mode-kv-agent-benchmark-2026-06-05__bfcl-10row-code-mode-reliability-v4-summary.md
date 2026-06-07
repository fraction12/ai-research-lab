# BFCL 10-Row Code-Mode Reliability v4 Summary

Date: 2026-06-05

## Result

Gemma4 12B passed the target BFCL Code-mode smoke gate:

- `code_mode_full_visible`: 10/10 gate pass, 10/10 BFCL scorer pass.
- `direct_full_visible_tools`: 10/10 gate pass, 10/10 BFCL scorer pass.
- `code_mode_native_live_append`: 10/10 gate pass, 10/10 BFCL scorer pass.
- `code_mode_restored_kv_capsule`: 10/10 gate pass, 10/10 BFCL scorer pass.

This establishes a viable full-visible Code-mode calibration path for the 10-row non-handmade BFCL smoke cohort. It does not by itself prove KV capsule value over full-visible prompting; it proves the harness can now parse and score model-authored BFCL tool calls accurately enough to run the next comparison.

## Run Metadata

- Run label: `bfcl-10row-smoke-reliability-v4`
- Host: `DushyantPC`
- Model profile: `gemma4-12b`
- Backend: `cuda_v13`
- Effective state route: `seq_file`
- Command: `code_mode_kv_capsule_model_loop_runner.py --packet .../bfcl-10row-smoke-control-packet.jsonl --run-label bfcl-10row-smoke-reliability-v4 --state-route auto --predict 256 --max-steps 3 --max-repairs 1`
- Started UTC: `2026-06-05T21:39:10Z`
- Finished UTC: `2026-06-05T21:51:10Z`
- Record count: 70

Raw artifacts:

- `research/01-ssd-native-inference-current/benchmarks/nonhandmade-code-mode-kv-agent-benchmark-2026-06-05/raw/bfcl-10row-smoke-reliability-v4-model-loop-records.jsonl`
- `research/01-ssd-native-inference-current/benchmarks/nonhandmade-code-mode-kv-agent-benchmark-2026-06-05/raw/bfcl-10row-smoke-reliability-v4-model-loop-run-info.json`
- `research/01-ssd-native-inference-current/benchmarks/nonhandmade-code-mode-kv-agent-benchmark-2026-06-05/raw/bfcl-10row-smoke-reliability-v4-console.log`

## Control Matrix

| Control | Gate Pass | BFCL Score Pass | Positive Gate Pass |
| --- | ---: | ---: | ---: |
| `direct_full_visible_tools` | 10/10 | 10/10 | 10/10 |
| `code_mode_full_visible` | 10/10 | 10/10 | 10/10 |
| `code_mode_native_live_append` | 10/10 | 10/10 | 10/10 |
| `code_mode_restored_kv_capsule` | 10/10 | 10/10 | 10/10 |
| `compact_visible_evidence_code_mode` | 4/10 | 4/10 | 4/10 |
| `code_mode_fresh_tail_only` | 8/10 | 2/10 | 0/0 |
| `code_mode_wrong_capsule_negative` | 8/10 | 2/10 | 0/0 |

The two negative-control BFCL passes are the two no-call irrelevance rows. They are not evidence that hidden prefix information leaked; they pass because the correct BFCL behavior is to make zero calls, which a tail-only prompt can also do.

## Full-Visible Cases

| Case | Parsed Calls | Matched Calls | Repairs | Gate |
| --- | ---: | ---: | ---: | --- |
| `bfcl:irrelevance:irrelevance_0` | 0 | 0 | 1 | pass |
| `bfcl:irrelevance:irrelevance_1` | 0 | 0 | 1 | pass |
| `bfcl:multiple:multiple_0` | 1 | 1 | 0 | pass |
| `bfcl:multiple:multiple_1` | 1 | 1 | 0 | pass |
| `bfcl:parallel:parallel_0` | 2 | 2 | 1 | pass |
| `bfcl:parallel:parallel_1` | 2 | 2 | 1 | pass |
| `bfcl:parallel_multiple:parallel_multiple_0` | 2 | 2 | 1 | pass |
| `bfcl:parallel_multiple:parallel_multiple_1` | 2 | 2 | 1 | pass |
| `bfcl:simple:simple_0` | 1 | 1 | 0 | pass |
| `bfcl:simple:simple_1` | 1 | 1 | 0 | pass |

## What Changed

The reliability fixes were parser/protocol fixes, not answer completion:

- Parse Gemma native BFCL tool-call syntax such as `call:spotify.play{artist: "Taylor Swift", duration: 20}`.
- Preserve dotted function names instead of truncating at the first dot.
- Canonicalize known wrapper-key casing, including `Function_name`, while leaving benchmark argument keys intact.
- Trim harmless leading/trailing whitespace on generated string argument values.
- Merge BFCL retry candidates by normalized model-authored call identity so duplicate retries do not become scorer extras.
- Keep BFCL repair prompts answer-key free.

## Claim Boundary

Safe claim:

Gemma4 12B can now complete the 10-row non-handmade BFCL smoke cohort under the Code-mode full-visible path with 100% scorer accuracy in this harness.

Unsafe claim:

This does not yet prove that restored KV capsules improve quality, reduce token cost, or outperform full-visible prompting. The restored path also passed 10/10, but because the full-visible and native-live paths passed too, the next paper-grade question is comparative efficiency and prefix-dependence under larger, stricter cohorts.

## Next Step

Run the larger non-handmade BFCL cohort using this fixed parser/protocol layer, and report:

- full-visible pass rate as the calibration gate;
- native-live vs restored-KV parity;
- prompt/decode timing and state read/write cost;
- negative controls excluding no-call irrelevance rows from leakage interpretation;
- first-pass vs repair-assisted pass rate.
