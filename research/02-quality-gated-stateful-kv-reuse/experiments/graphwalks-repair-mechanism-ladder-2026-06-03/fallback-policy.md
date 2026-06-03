# Fallback Policy

Date: 2026-06-03

## Policy Result

All six fixed GraphWalks cases require full-prompt fallback for this model/protocol stack.

| Case | Policy | Supporting evidence |
| --- | --- | --- |
| `graphwalks-6` | `require_full_prompt` | Prior full prompt passed; live-tail and restored session-tail failed; anchor controls did not pass. |
| `graphwalks-9` | `require_full_prompt` | Prior full prompt passed; live-tail and restored session-tail failed; anchor controls partially improved but did not pass. |
| `graphwalks-11` | `require_full_prompt` | Prior full prompt passed; live-tail and restored session-tail failed; no anchor or visibility control repaired it. |
| `graphwalks-13` | `require_full_prompt` | Prior full prompt passed; live-tail and restored session-tail failed; 256-token anchor partially improved but did not pass. |
| `graphwalks-16` | `require_full_prompt` | Prior full prompt passed; live-tail and restored session-tail failed; 256-token anchor partially improved but did not pass. |
| `graphwalks-19` | `require_full_prompt` | Prior full prompt passed; live-tail and restored session-tail failed; 256-token anchor partially improved but did not pass. |

## Rule For This Cohort

For GraphWalks-style reasoning-over-prefix tasks, this ladder does not support `allow_session_tail`, `allow_live_tail_only`, or `allow_restore_with_anchor_recompute`.

Use full-prompt execution unless a future lower-level repair control produces exact correctness parity against full-prompt replay.

## Why Not Anchor Fallback Yet

The 256-token visible-anchor proxy raised mean F1 to approximately `0.4202`, and several cases partially improved. However, no case reached score `1.0`, and one case produced a JSON parse failure. It is useful mechanism evidence, not a safe fallback policy.
