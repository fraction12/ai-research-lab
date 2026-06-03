## Context

The project has accumulated several evidence layers: research positioning, benchmark graphs, large-prefix timing runs, session-tail timing runs, and a correctness parity run with 42 full-passing selected cases. The latest result is mixed: session-tail saved prompt time but dropped correctness, especially on GraphWalks.

## Goals / Non-Goals

**Goals:**
- Produce a single report that a human can read to understand the system direction.
- Separate proven facts from hypotheses and next steps.
- Explain the SSD-backed approach without claiming SSD is VRAM or claiming invention of KV caching.
- Include the model-quality caveat: GPT-OSS 20B is not a frontier model, so failures may come from the model, prompt protocol, or cache/session semantics.

**Non-Goals:**
- Do not add new benchmark runs in this change.
- Do not change Flashcache runtime behavior.
- Do not present the report as a paper or public launch claim.

## Decisions

1. Make the report a Markdown doc under `docs/`.

   The intended reader is the project owner and future coding agents. Markdown keeps it source-controlled, linkable, and easy to update after future runs.

2. Use a verdict-plus-evidence structure.

   The report should state the bottom line early, then back it with recorded benchmark data. This prevents the reader from drowning in raw JSON while preserving traceability.

3. Treat quality as the primary open risk.

   The speed evidence is strong enough to justify more work. The correctness parity run shows that the next layer must prove answer equivalence or route around unsafe cases.

## Risks / Trade-offs

- [Risk] A "final report" can sound like the research is finished. -> Mitigation: title and content frame it as the current system report and call out open gates.
- [Risk] The report may overgeneralize from one local model. -> Mitigation: include an explicit model caveat and recommend stronger-model/control runs.
- [Risk] The report may duplicate existing docs. -> Mitigation: synthesize and link existing docs rather than copying every detail.
