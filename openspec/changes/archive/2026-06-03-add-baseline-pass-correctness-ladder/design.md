## Context

The current correctness runner can sample cases, run full/session-tail modes, and score response pairs. The last GPT-OSS smoke showed a key methodology problem: if full-prompt output fails, a session-tail failure does not tell us whether the cache/session method damaged quality. We need a two-stage ladder that first establishes a full-prompt passing baseline.

## Goals / Non-Goals

**Goals:**
- Add a single command that creates all artifacts for a fair parity run.
- Preserve full baseline responses and scores even when no cases pass.
- Compare session-tail only on selected full-passing cases.
- Report prompt-time savings and parse errors for selected cases.

**Non-Goals:**
- Do not change dataset scoring definitions.
- Do not auto-tune prompts or search many generation settings in this change.
- Do not claim quality parity when the selected case set is empty.

## Decisions

1. Implement as a command in `flashcache_correctness_eval.py`.

   The ladder reuses existing case readers, response generation, scoring, and JSONL writers. Keeping it in the same module avoids a second orchestration surface.

2. Select by baseline score threshold.

   The default threshold is `1.0`, matching exact/pass semantics for IFEval and GraphWalks. The user can lower it for MRCR-style similarity experiments, but the report preserves the selected threshold.

3. Combine selected full responses with session-tail responses for final scoring.

   The scorer already expects paired response records. Filtering the original full responses avoids rerunning the baseline and keeps timings aligned to the selection step.

## Risks / Trade-offs

- [Risk] A small candidate set may produce zero selected cases. -> Mitigation: write a report anyway and make the next action obvious: sample easier/more cases or improve answer protocol.
- [Risk] Selection by numeric score can hide scorer-specific `passed` rules. -> Mitigation: report both score and pass status in the source score JSON, and default the threshold to exact score `1.0`.
- [Risk] Running full and session-tail in separate phases can add model variance. -> Mitigation: temperature defaults to `0`, and the response records preserve model, prompt hashes, and timing metadata.
