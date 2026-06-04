## Why

The prior scaled KV capsule campaign stopped at full-visible baseline failures, so it mostly measured benchmark-instrument weakness rather than the capsule mechanism. Track 02 now needs a calibrated campaign that first finds boringly reliable full-visible retrieval and agent-context units, then freezes those units and runs the native live/restored capsule evidence ladder.

This keeps the research question narrow: can persistent native KV/state capsules preserve reusable context and reduce repeated prompt-token/time cost under quality gates? It does not claim that cache reuse makes the model inherently smarter.

## What Changes

- Add a calibrated Track 02 A-to-E campaign for native KV/state capsule evaluation.
- Add Phase A visible-baseline calibration that can systematically try prompt/data/output/scoring variants before promoting a unit.
- Freeze promoted evidence units before Phase B/C/D controls so prompt rescue does not contaminate capsule evidence.
- Run Phase B semantic capsule ladders on promoted retrieval units, with full-visible, fresh-tail, live-append, and restored-capsule controls.
- Run Phase C scale boundary search across promoted retrieval sizes.
- Run Phase D amortization economics for restored-capsule-passing units.
- Run Phase E small agent-context capsule benchmark only after at least one retrieval ladder passes.
- Require chunked native prefill/decode around the pinned runner's `n_batch=512` limit for long prompts.
- Package sanitized Track 02 summaries and keep prompt-bearing raw artifacts under ignored Track 01 benchmark paths.

## Capabilities

### New Capabilities

- `kv-capsule-calibrated-a-to-e-campaign`: Defines calibration, promotion, controls, metrics, stop/fallback rules, artifact boundaries, and interpretation requirements for the A-to-E KV capsule campaign.

### Modified Capabilities

- None.

## Impact

- Adds a new OpenSpec change under `openspec/changes/run-kv-capsule-calibrated-a-to-e-campaign/`.
- Adds ignored raw runner/output artifacts under `research/01-ssd-native-inference-current/benchmarks/kv-capsule-calibrated-a-to-e-campaign-2026-06-04/raw/`.
- Adds committed sanitized Track 02 artifacts under `research/02-quality-gated-stateful-kv-reuse/experiments/kv-capsule-calibrated-a-to-e-campaign-2026-06-04/`.
- Uses the existing pinned DushyantPC native direct C API route against the b9493/GPT-OSS bundle; no tracked Track 01 harness-code changes are planned.
