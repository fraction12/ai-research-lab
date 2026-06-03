## Context

The repo now has a paper roadmap and conservative positioning. That protects against overclaiming, but it can also bias future work toward obvious incremental experiments. The user wants the project to actively seek solutions that are not already obvious in prior art.

## Goals / Non-Goals

**Goals:**

- Add a research posture that rewards surprising but testable hypotheses.
- Keep unconventional work disciplined through baselines, controls, and falsification.
- Make future agents explicitly document why an experiment is against the grain and what would make it real.

**Non-Goals:**

- Do not weaken the evidence bar.
- Do not encourage vague speculation without executable tests.
- Do not make novelty claims before prior-art refresh and reproducible evidence.

## Decisions

- Add `docs/discovery-research-playbook.md`.
  - Rationale: discovery needs a durable method separate from the paper roadmap.
  - Alternative rejected: bury the guidance only in `AGENTS.md`, where it would be too compressed.

- Add a high-risk lane to `docs/research-paper-roadmap.md`.
  - Rationale: the publishable direction should make room for surprising mechanisms while keeping the main paper claim coherent.
  - Alternative rejected: create an unrelated speculative roadmap. That would split the project.

- Extend `AGENTS.md` with discovery-mode rules.
  - Rationale: future agents need explicit permission to propose uncomfortable experiments, plus guardrails against magical thinking.

## Risks / Trade-offs

- Speculation could crowd out measurement -> Mitigation: every high-risk hypothesis needs a baseline, control, falsifier, and expected artifact.
- Against-the-grain work could become novelty theater -> Mitigation: require the experiment to explain why the mainstream assumption might fail.
- Prior art may already cover an idea -> Mitigation: refresh references before presenting it as novel.
