# Tail-Only KV Capsule Family 2 Structured Retrieval Scale

## Result

GPT-OSS Family 2 structured retrieval passed semantic continuation on the official sequence-file state route: full visible `30/30`, fresh tail `0/30`, live append `30/30`, and restored capsule append `30/30`.

The run is classified as `family2_sequence_state_restored_capsule_semantic_passed_hash_warning` because deterministic output hash parity was partial: full-vs-live matched `12/30`, and live-vs-restored matched `12/30`. Semantically, every restored capsule answer contained the hidden structured value, but exact output identity is not established across all cases.

## What This Proves

This is a narrow positive for tail-only restored sequence-state continuation on fabricated structured lookup records. It extends the Family 1 simple-codeword proof to a richer Family 2 lookup task on the same `seq_file` route.

## What It Does Not Prove

This does not prove Family 3 graph reasoning, GraphWalks, long-prefix agent behavior, broad retrieval, noiseless evidence repair, or model-independent KV capsule correctness.

## Controls

- `native_full_visible_prefix_plus_tail`: `30/30`
- `native_fresh_tail_only`: `0/30`
- `native_live_append_tail_only`: `30/30`
- `native_restored_capsule_append_tail_only`: `30/30`

## Route

- Requested route: `auto`
- Effective route: `seq_file`
- Internal route: `seq-file`
- Sequence file exports available: `True`
- Sequence memory exports available: `True`

## Telemetry Note

`ended_utc` and `process_cleanup_status` are null in the copied-back run info, likely because SSH/PC cleanup telemetry was interrupted. The accepted evidence is the complete 120-record raw file plus run-info decision copied back under the ignored raw boundary.
