## Why

The six-case GraphWalks mechanism chain shows that compact visible evidence can repair hidden-prefix/session-tail failures, but it is still only a focused mechanism result. Track 02 needs a larger, still-controlled `parents` pilot to learn when hidden cached context fails, when compact evidence repairs it, and whether the effect is really hidden KV contribution or token-efficient evidence scheduling.

## What Changes

- Add a 50-case GraphWalks `parents` scaling pilot with deterministic sampling and bucket annotations.
- Compare five paired controls per case: full visible compact prompt, hidden-prefix session tail, hidden-prefix compact no-evidence tail, hidden-prefix compact visible evidence tail, and fresh compact visible-evidence-only.
- Preserve prompt-bearing inputs and raw outputs under ignored Track 01 benchmark paths while committing only Track 02 summaries and OpenSpec artifacts.
- Require per-case evidence slices extracted from the stable graph prefix and requested target node, not from reference answers.
- Record correctness, precision/recall/F1, prompt/decode timing, evidence size, prefix length, parsing/truncation signals, failure classification, and subset analyses.
- Define stop rules for runtime blockers or excessive pilot duration before running the full five-control matrix.

## Capabilities

### New Capabilities
- `graphwalks-parent-scaling-pilot`: Defines the controlled 50-case GraphWalks `parents` pilot, artifact layout, control matrix, metrics, failure taxonomy, and interpretation rules.

### Modified Capabilities
- `flashcache-correctness-eval-suite`: Requires the correctness workflow to support or faithfully record the five-control GraphWalks `parents` pilot, including compact visible evidence controls and local prompt-bearing artifacts.
- `research-positioning-doc`: Requires Track 02 summaries to frame this pilot as role-aware context compilation / quality-gated context scheduling evidence, not broad GraphWalks quality or pure KV reuse.

## Impact

- Affects Track 02 OpenSpec planning and committed experiment summaries under `research/02-quality-gated-stateful-kv-reuse/experiments/graphwalks-parent-scaling-pilot-2026-06-04/`.
- Produces prompt-bearing local artifacts under ignored Track 01 benchmark paths:
  - `research/01-ssd-native-inference-current/benchmarks/correctness-eval-inputs/graphwalks-parent-scaling-pilot-2026-06-04/`
  - `research/01-ssd-native-inference-current/benchmarks/correctness-eval-results/graphwalks-parent-scaling-pilot-2026-06-04/raw/`
  - `research/01-ssd-native-inference-current/benchmarks/correctness-eval-cache/graphwalks-parent-scaling-pilot-2026-06-04/`
- May require a small local runner or case-composition script under ignored benchmark artifacts. Track 01 harness code should remain unchanged unless the design proves it is necessary.
- Uses the pinned DushyantPC GPT-OSS llama.cpp path and records model/runner hashes, flags, commands, prompt hashes, raw output hashes, and slot/cache telemetry.
