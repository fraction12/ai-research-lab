# KV Capsule Scaled Amortized Benchmark Campaign - 2026-06-04

## Answer First

This campaign did not produce interpretable restored-capsule amortization evidence. Every scaled structured-retrieval Phase 1 size failed the native full-visible quality guard before fresh-tail, live-append, or restored-capsule controls could run.

Phase 1 full-visible scores:

- 25 rows: 2/10 answer-contained
- 100 rows: 0/10 answer-contained
- 250 rows: 0/10 answer-contained

Phase 2 reasoning calibration also failed full-visible calibration across all tested reusable-prefix templates:

- adjacency table: 0/5
- edge triples table: 0/5
- simple sentence facts: 0/5
- JSON-ish object/list: 0/5

Phase 3 did not run because Phase 1 had no restored-capsule-pass unit.

## Interpretation

This is not a restored-capsule semantic failure. No restored capsule control ran in this campaign. The result is a quality/protocol boundary for the pinned native GPT-OSS route: the model could not reliably solve the scaled visible prompts, so capsule reuse economics cannot be interpreted for these prompt families.

Family 1 and Family 2 remain positive small-gate evidence. This campaign shows the next scaling step needs a stronger full-visible baseline or a better calibrated structured-prefix prompt before amortized KV capsule claims are fair.

## Scope

- Runner: native Python `ctypes` direct llama.cpp C API.
- Model path: pinned GPT-OSS blob recorded in `model-info.json`.
- Backend: `cuda_v13` on DushyantPC.
- Base commit: `1a35780 Record KV capsule Family 3 gate`.
- Raw prompt-bearing artifacts remain ignored under Track 01 benchmark paths.

## Artifact Map

Committed summaries:

- `summary.json`
- `phase-results.json`
- `case-metrics.json`
- `amortization.json`
- `failure-classifications.json`
- `commands.md`
- `model-info.json`
- `artifact-manifest.json`

Ignored raw evidence:

- `research/01-ssd-native-inference-current/benchmarks/kv-capsule-scaled-amortized-benchmark-campaign-2026-06-04/raw/campaign-records.jsonl`
- `research/01-ssd-native-inference-current/benchmarks/kv-capsule-scaled-amortized-benchmark-campaign-2026-06-04/raw/campaign-run-info.json`
- `research/01-ssd-native-inference-current/benchmarks/kv-capsule-scaled-amortized-benchmark-campaign-2026-06-04/raw/campaign-console.txt`
- `research/01-ssd-native-inference-current/benchmarks/kv-capsule-scaled-amortized-benchmark-campaign-2026-06-04/raw/kv_capsule_scaled_campaign.py`

## Next Direction

Do not expand to GraphWalks from this result. The next useful move is a full-visible-first scaled structured prompt calibration: find a reusable-prefix format that reaches 100% visible quality at a modest row count, then rerun the same capsule amortization gates unchanged.
