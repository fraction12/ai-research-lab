## Why

The calibrated A-to-E campaign stopped correctly at Phase A: no 10-row full-visible retrieval variant reached the promotion gate, so no restored-capsule result was interpretable. Track 02 now needs a smaller focused rescue campaign that isolates whether the boundary is prompt/data format, native runner route/protocol, or model weakness, then runs capsule controls only on a frozen unit that has a boringly reliable visible baseline.

## What Changes

- Add a focused visible-baseline rescue and route-control campaign for Track 02.
- Calibrate full-visible retrieval units at tiny scales first: 1, 3, 5, and 10 rows.
- Try format families that include the prior Family 2 positive shape, ultra-simple codebook lines, XML/tagged records, short TSV, natural facts, and explicit single/three-record sanity cases.
- Add route controls to compare the native ctypes route with known-positive Family 1/2 checks and available llama.cpp alternate routes when practical.
- Run live/restored capsule controls only for promoted frozen units.
- Package sanitized summaries under Track 02 and keep prompt-bearing raw evidence ignored under Track 01.

## Capabilities

### New Capabilities

- `kv-capsule-visible-baseline-rescue`: Defines the rescue ladder, route controls, promotion rules, capsule evidence conditions, amortization metrics, artifact boundaries, and interpretation rules.

### Modified Capabilities

- None.

## Impact

- Adds a new OpenSpec change under `openspec/changes/run-kv-capsule-visible-baseline-rescue/`.
- Adds ignored raw runner/output artifacts under `research/01-ssd-native-inference-current/benchmarks/kv-capsule-visible-baseline-rescue-2026-06-04/raw/`.
- Adds committed sanitized Track 02 artifacts under `research/02-quality-gated-stateful-kv-reuse/experiments/kv-capsule-visible-baseline-rescue-2026-06-04/`.
- Uses the existing pinned DushyantPC native direct C API route against the b9493/GPT-OSS bundle and may use already-installed llama.cpp route controls if available.
