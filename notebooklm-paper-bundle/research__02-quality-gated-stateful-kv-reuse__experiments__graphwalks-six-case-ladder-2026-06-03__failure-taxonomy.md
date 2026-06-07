# Failure Taxonomy

| Class | Confirming evidence in this ladder | Ruling-out evidence | Fallback implication |
| --- | --- | --- | --- |
| `model_weakness` | Full-prompt replay would fail or vary across runs. | Full-prompt replay passed 18/18 attempts across the six cases. | Not the primary explanation for this slice, though stronger-model control remains open. |
| `prompt_protocol_issue` | Full prompt passes but altered prompt formatting or answer-hint placement degrades quality. | Original full prompt remains stable. | Avoid relying on tail-only or reformatted prompt protocols for this task family without repair. |
| `scorer_parser_brittleness` | Raw output contains the right node set but scorer/parser rejects it. | Regular session-tail outputs parsed successfully but produced wrong/prose-like node sets; stronger-tail outputs were malformed model outputs, not parser-only mistakes. | Scorer is adequate for these failures; keep raw output evidence. |
| `session_cache_semantic_issue` | Full/visible-prefix controls pass while restored-prefix session-tail fails with stable telemetry. | Runtime save/restore telemetry has no obvious errors. | Fall back to full prompt for GraphWalks-style reasoning-over-prefix tasks. |
| `position_compatibility_issue` | Token counts, hashes, context size, restore positions, or compatibility keys mismatch. | Basic telemetry restored stable token counts with no runtime error. | Needs lower-level probe before claiming position-specific cause. |
| `runtime_storage_issue` | Save/restore errors, corrupted slot files, inconsistent `n_restored`, or response-level errors. | All session-tail runs had stable `n_restored`/`n_read` values and no response-level errors. | Not supported by this run. |

## Case-Level Read

- `graphwalks-6`, `graphwalks-9`, and `graphwalks-11`: primary `prompt_protocol_issue`, secondary `session_cache_semantic_issue`. The visible-prefix/session-formatted control also degraded, so formatting is a real confounder.
- `graphwalks-13`, `graphwalks-16`, and `graphwalks-19`: primary `session_cache_semantic_issue`. The visible-prefix/session-formatted control passed, while session-tail still failed repeatedly.
