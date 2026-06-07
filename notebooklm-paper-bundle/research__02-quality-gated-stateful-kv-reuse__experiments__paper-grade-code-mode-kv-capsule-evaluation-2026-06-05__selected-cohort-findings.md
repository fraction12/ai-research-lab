# Selected Cohort Findings

Date: 2026-06-06

This records the completed minimum selected-cohort run for the paper-grade Code Mode + KV capsule evaluation.

## Source Run

- Mac checkout: `/Volumes/MacSSD/Projects/ai-research-lab`
- DushyantPC execution checkout: `C:\ai\paper`
- Run label: `bfcl-paper-selected-cohort-v1`
- Model profile: `gemma4-12b`
- Source packet: `bfcl-paper-selected-cohort-v1-control-packet.jsonl`
- Model-loop records: `bfcl-paper-selected-cohort-v1-model-loop-records.jsonl`
- Raw prompt-bearing artifacts remain ignored under Track 01:
  `research/01-ssd-native-inference-current/benchmarks/paper-grade-code-mode-kv-capsule-evaluation-2026-06-05/raw/`

## Result

- Control records completed: `700 / 700`
- Cases completed: `100 / 100`
- Controls per case: `7`
- Task status: completed successfully

The cohort is the paper-campaign minimum cohort selected from calibration. Calibration found `162` clean primary-eligible rows, below the `200` ideal target but above the `100` minimum threshold.

## Core Signal

- Code Mode full visible: `100 / 100`
- Native live append: `100 / 100`
- Restored KV capsule: `100 / 100`
- Restored KV failures: `0`
- Native/restored hash parity: `100 / 100`
- Fresh-tail leaks: `0`
- Wrong-capsule leaks: `0`

Interpretation: restored KV state preserved the native live-append behavior on every selected case, while both negative controls remained closed. This is the paper-critical viability result.

## Baseline Comparisons

- Direct full visible tools: `91 / 100`
- Direct tool gaps: `9`
- Compact visible evidence Code Mode: `19 / 100`

Interpretation: compact visible evidence was much weaker than the restored hidden-prefix route, and direct visible tools lagged Code Mode full-visible execution. The result supports the claim that the advantage is not merely summarizing context or showing tools directly; it is the combination of stable hidden state and a compact execution contract.

## Category Mix

- `simple`: `26`
- `multiple`: `25`
- `parallel_multiple`: `17`
- `java`: `17`
- `parallel`: `14`
- `javascript`: `1`

## Timing

Mean total latency by control:

- Direct full visible tools: `8179.8 ms`
- Code Mode full visible: `6766.7 ms`
- Native live append: `6782.7 ms`
- Restored KV capsule: `8513.8 ms`
- Fresh-tail negative: `9738.9 ms`
- Wrong-capsule negative: `7571.6 ms`
- Compact visible evidence: `9434.8 ms`

Timing note: this run supports semantic state preservation, not a speed claim. Restored KV was slower than native live append in this implementation.

## Paper-Safe Claim

On a 100-case BFCL-derived selected cohort, Gemma 4 12B with Code Mode and restored KV capsules matched native live-append behavior on all selected cases, with zero restored-only failures and zero negative-control leaks. Compact visible evidence passed only `19 / 100`, suggesting that restored hidden state carries useful task information beyond a compact visible baseline.

Do not claim broad speedup from this run. Do not claim the result covers all BFCL categories. The correct framing is quality-gated hidden-state reuse for local tool-using agents under strict controls.
