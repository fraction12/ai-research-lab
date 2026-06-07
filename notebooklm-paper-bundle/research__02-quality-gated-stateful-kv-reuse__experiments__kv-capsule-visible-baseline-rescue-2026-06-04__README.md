# KV Capsule Visible Baseline Rescue - 2026-06-04

## Decision

The run completed without interpretable restored-capsule evidence.

A 1-row visible unit promoted during calibration, but the same frozen unit failed the Phase C full-visible guard. Because the full-visible evidence guard failed before fresh-tail, live-append, or restored-capsule controls, this run cannot support a claim about restored KV capsule quality.

## Key Results

- Total records: `624`
- Phase A calibration records: `617`
- Phase A semantic matches: `200`
- Phase A exact/normalized matches: `17`
- Promoted calibration units: `1`
- Route-control decision: `native_route_known_positive_control_failure`
- Phase C decision: `promoted_unit_full_visible_regressed`
- Restored capsule pass units: `0`

## Boundary

No 3-row or larger unit met the strict promotion gate. Several variants at 3 and 5 rows got semantic containment, but the exact/normalized answer protocol did not hold.

The route controls are a major caveat: both native known-positive controls failed. That means this run primarily exposes native-route/prompt-protocol instability and calibration-to-evidence non-reproducibility, not a clean cache mechanism result.

## Artifacts

- `summary.json`: decision, phase summaries, route caveat, and interpretation.
- `phase-results.json`: sanitized phase-level results.
- `calibration-results.json`: sanitized Phase A attempt summaries.
- `case-metrics.json`: sanitized per-record metrics with prompt/answer text removed.
- `route-controls.json`: sanitized route-control outcome and alternate route availability.
- `amortization.json`: not-interpretable status.
- `failure-classifications.json`: failure counts by phase, row, variant, and class.
- `commands.md`: local/remote commands used.
- `model-info.json`: model/backend metadata.
- `artifact-manifest.json`: package manifest and sanitation notes.

## Sanitation

Committed artifacts intentionally exclude raw prompts, tails, full prompts, raw responses, expected answer strings, token arrays, generated token arrays, top-k arrays, and state bytes. Raw prompt-bearing files remain under the ignored Track 01 benchmark path.
