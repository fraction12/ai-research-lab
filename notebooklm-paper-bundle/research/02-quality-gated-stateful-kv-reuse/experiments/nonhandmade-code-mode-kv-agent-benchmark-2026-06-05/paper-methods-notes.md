# Paper Methods Notes

## Research Question

Can a persisted KV state capsule be restored and used as a semantic equivalent of native live append for non-handmade tool-call benchmark tasks, while exposing fewer prompt tokens at the visible tail?

## Source

Benchmark source: BFCL v3, Hugging Face dataset revision `61fc0608cfd831fcfbbaa676ebdfef0ed963eeda`, leaderboard checkpoint `f7cf735`, adapter scorer `bfcl_expected_call_scorer_v1`.

The smoke uses revision-pinned rows from `simple`, `multiple`, `parallel`, `parallel_multiple`, and `irrelevance`, two rows per category. Raw prompt-bearing packet and model outputs remain under ignored Track 01 benchmark paths.

## Controls

The seven controls are:

1. `direct_full_visible_tools`
2. `code_mode_full_visible`
3. `code_mode_fresh_tail_only`
4. `code_mode_native_live_append`
5. `code_mode_restored_kv_capsule`
6. `code_mode_wrong_capsule_negative`
7. `compact_visible_evidence_code_mode`

For positive controls, `control_gate_passed=true` means the model produced the expected scored answer. For negative controls, `control_gate_passed=true` means the control behaved as expected, usually by not answering.

## Smoke Gate

A row is usable as restored-capsule evidence only if direct full-visible, Code-mode full-visible, native live append, and restored KV capsule all pass, while fresh-tail and wrong-capsule controls do not contain the expected answer. Under that rule, 2/10 rows are usable parity evidence in this smoke.

## Efficiency Notes

Restored capsule mean prompt evaluation on usable rows was lower than native live append, but total wall time was higher. This smoke supports a semantic parity claim, not a speedup claim.

## Known Limitations

The scorer is a deterministic expected-call adapter, not the official BFCL evaluator. Rows that require official BFCL semantics beyond this adapter must be marked diagnostic-only or excluded from primary claims.
