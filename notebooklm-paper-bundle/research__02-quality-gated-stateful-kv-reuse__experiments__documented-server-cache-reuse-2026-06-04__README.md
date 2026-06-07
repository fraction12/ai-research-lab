# Documented Server Cache Reuse Probe

Date: 2026-06-04

This probe tests the documented llama.cpp server cache-reuse route after hidden tail-only continuation failed: restore a prefix slot, then resend the full `prefix + tail` prompt with `cache_prompt: true` and explicit `id_slot: 0`.

## Result

| Control | Answer contained | Mean prompt tokens | Mean prompt ms |
| --- | ---: | ---: | ---: |
| `full_visible_no_cache` | 10/10 | 31.0 | 625.4 |
| `fresh_tail_only` | 0/10 | 14.0 | 410.1 |
| `restored_tail_only` | 0/10 | 14.0 | 410.4 |
| `restored_full_prompt_cache_prompt` | 10/10 | 19.0 | 477.8 |
| `full_prompt_cache_prompt_without_restore` | 10/10 | 31.0 | 623.4 |

Decision: `documented_cache_reuse_semantic_and_computational_reuse_observed`.

The main documented route recovered the codeword in 10/10 cases and used fewer prompt-eval tokens than clean full-prompt controls. Restored tail-only remained a semantic miss in 10/10 cases, as expected.

## Interpretation

The pinned GPT-OSS llama.cpp path supports semantic and computational cache reuse when the full visible prompt is resent for prefix matching. This is useful reusable context, but it is not invisible hidden context: the prefix must be resent so the server can match it against the restored slot.

Server logs are preserved as ignored raw artifacts. `server-log-index.json` contains hashes and sanitized cache-related excerpts/pattern counts for audit. No GraphWalks or noiseless-evidence rerun was performed.
