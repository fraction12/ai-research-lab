# Non-Handmade Code-Mode KV Capsule Benchmark Smoke

This experiment moved the Code-mode plus KV capsule control ladder from handmade tasks to BFCL v3 rows pinned to dataset revision `61fc0608cfd831fcfbbaa676ebdfef0ed963eeda`.

## Result

The 10-row smoke completed 70/70 records on DushyantPC with Gemma4 12B, CUDA backend `cuda_v13`, and sequence-state route `seq_file`.

The primary 50-row v5 run completed 350/350 records. Restored KV capsule matched native live append exactly at 35/50 BFCL pass with zero case-level disagreements. Fresh-tail and wrong-capsule negatives stayed closed at 0/50. See `bfcl-primary-50-v5-summary.md` for the final primary-cohort results and claim boundaries.

The strongest signal is live/restored parity: restored KV capsule output matched native live append by normalized response hash and generated-token hash on all 10 rows. Two rows passed the strict usable evidence gate: `bfcl:multiple:multiple_1` and `bfcl:simple:simple_0`.

The smoke is not a benchmark win. Five rows failed visible baselines, two irrelevance rows are diagnostic only because no-call behavior is not prefix-dependent hidden evidence, and `bfcl:simple:simple_1` passed visible baselines but failed native live append and restored capsule.

## Interpretation

The transport path now appears semantically valid for the model-loop runner: restored capsule behaves exactly like native live append. The next research problem is cohort selection and task suitability, not basic KV restore semantics.

On usable rows, restored capsule reduced mean prompt evaluation time versus native live append by 90.4 percent, but total wall time was slower in this smoke because save/restore, loop, and decode overhead dominated.

## Next Step

Run BFCL candidate calibration over 50 to 100 rows and select a primary cohort only from rows that pass direct full-visible, Code-mode full-visible, native live append, and negative controls. Exclude irrelevance/no-call rows from primary hidden-prefix evidence.
