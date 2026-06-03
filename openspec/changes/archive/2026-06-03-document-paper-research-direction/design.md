## Context

The repo already records that KV caching, prefix caching, prompt-state reuse, and SSD-backed KV storage are established areas. A newer online scan further narrows the project wedge: prompt caching for long-horizon agentic tasks and workflow-aware KV reuse now exist as explicit research topics, while correctness contracts for persistent/session KV reuse on local non-frontier agents remain much less visible.

## Goals / Non-Goals

**Goals:**

- Keep the repo's public claims conservative and source-backed.
- Make the publishable topic explicit enough to guide experiments.
- Add a repeatable research workflow for future documentation, benchmarks, and paper drafting.
- Update agent instructions so future work captures failures, controls, and negative results.

**Non-Goals:**

- Do not claim the project invented SSD-backed KV caching.
- Do not write the paper yet.
- Do not add new benchmark code or runtime implementation in this change.
- Do not convert all existing docs into formal OpenSpec artifacts.

## Decisions

- Create `docs/research-paper-roadmap.md` as the canonical paper-program guide.
  - Rationale: the project needs a single file that says what paper we are trying to write and what evidence would make it credible.
  - Alternative rejected: keep the plan only in chat or OpenSpec. That would make future research work harder to recover.

- Extend `docs/research-positioning.md` instead of replacing it.
  - Rationale: it already has the right conservative prior-art posture; the new work should sharpen it with the latest negative-space scan.
  - Alternative rejected: create a separate prior-art-only file. That would split novelty guidance across too many docs.

- Update `AGENTS.md` with research-mode operating rules.
  - Rationale: future agents need to behave like research assistants: preserve exact sources, controls, raw results, failed hypotheses, and model caveats.
  - Alternative rejected: rely on implicit memory from this conversation. That is too brittle for a paper-oriented project.

## Risks / Trade-offs

- Overfitting to today's literature scan -> Mitigation: mark the scan date and require refreshes before public claims or submission drafts.
- Overclaiming novelty -> Mitigation: phrase the topic as a correctness-contract and methodology contribution unless experiments prove a stronger systems contribution.
- Documentation drift -> Mitigation: cross-link roadmap, references, positioning, and AGENTS guidance.
