# Control Feasibility

This note records setup-phase feasibility only. It does not interpret model quality.

## Summary

No Track 01 harness code changes are required before the first live execution pass. The existing CLI can cover the core replay, session-tail, dry-run, and scoring mechanics. Two controls need derived local case JSONL files rather than a new CLI mode.

| Control | Current feasibility | Track 01 code change needed now? | Notes |
| --- | --- | --- | --- |
| `full_replay_variance` | Covered by `flashcache_correctness_eval.py run --mode full --score` repeated across fixed output paths. | No | Use the six selected cases and repeat at `temperature 0.0`. |
| `session_tail_replay` | Covered by `run --mode session-tail --score`. | No | Use separate `--cache-dir` values per run to avoid slot artifact overlap. |
| `reset_restore_sanity` | Covered for the basic first pass by repeated `session-tail` runs, which prime, save, restore, and emit session setup telemetry. | No | The CLI does not expose a same-server explicit reset command. Add one only if repeated fresh-server restore telemetry leaves ambiguity. |
| `scorer_parser_brittleness` | Covered by `score` plus joining raw response JSONL with score JSON. | No | Score JSON includes parsed `predicted_nodes`, `answer_nodes`, precision, recall, and F1. Response JSONL preserves raw output, extracted response, and parse error. |
| `visible_prefix_session_formatted` | Feasible by derived local case JSONL. | No | Compose cases that keep the same references but make the visible prompt mimic restored-prefix/session-tail framing, then run `--mode full --answer-protocol json-answer`. |
| `stronger_tail_hints` | Feasible by derived local case JSONL. | No | Compose cases that prepend stricter GraphWalks node-list instructions to `tail_prompt`, then run `--mode session-tail --answer-protocol json-answer`. |
| `stronger_model_control` | Command shape is covered by `--model` or `--hf-repo`; model availability is unresolved. | No | No files were found under `benchmarks/models/` in this worktree. Live execution needs a model path or `--hf-repo`. |

## Derived Case Files To Create Before Live Runs

Visible-prefix/session-formatted control:

```text
research/01-ssd-native-inference-current/benchmarks/correctness-eval-inputs/graphwalks-six-case-ladder-2026-06-03/graphwalks-six-visible-prefix-session-formatted-cases.jsonl
```

Stronger tail hints control:

```text
research/01-ssd-native-inference-current/benchmarks/correctness-eval-inputs/graphwalks-six-case-ladder-2026-06-03/graphwalks-six-stronger-tail-hints-cases.jsonl
```

Both files should stay prompt-bearing and ignored. They should preserve the original `case_id`, `source_id`, `reference`, and `scoring` fields, and add a `control_id` field so downstream summaries can distinguish the control.

## Missing Control Surfaces

No required control surface is blocked for the approved setup phase.

Potential later addition: if reset/restore results remain ambiguous after repeated fresh-server session-tail runs, add a minimal same-server reset/restore check to the Track 01 harness and test it in isolation.
