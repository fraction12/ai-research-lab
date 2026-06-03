# AGENTS.md

## Project

This repo explores SSD-native inference for local agent workloads.

## Operating Rules

- Prefer evidence and benchmarks over claims.
- Keep docs decision-oriented: what to build, what to avoid, why.
- Treat SSD as a memory tier for reusable or predictable data, not as magic VRAM.
- Optimize for agent loops first: repeated prompts, tool schemas, repo context, and long sessions.
- Preserve links and source notes in `docs/references.md`.
- Read `docs/flashcache-metal-direction.md` before extending Flashcache or interpreting prompt-cache benchmarks. The goal is not merely to prove prompt caching; it is to use Flashcache as an evidence harness toward lower-level SSD-aware KV/prefix state management.

## Research Paper Mode

- Read `docs/research-positioning.md` and `docs/research-paper-roadmap.md` before making novelty claims or proposing paper-facing experiments.
- Treat "SSD-backed KV/prefix caching exists" as prior art. The current research wedge is quality-gated persistent/session KV reuse for local agent loops.
- Before running a paper-facing experiment, state the research question, baseline, controls, task families, metrics, and expected failure modes.
- Preserve exact model names, quantization, hardware, backend versions, command lines, prompts, raw outputs, and dataset paths.
- Report negative results and quality drift directly. Do not hide failures behind averaged latency or aggregate pass rates.
- Split results by task family when quality matters; instruction following, reasoning-over-prefix, tool use, RAG, and coding tasks should not be blended without explanation.
- Separate model weakness, prompt-protocol weakness, scorer brittleness, and cache/session semantics when interpreting failures.
- Update `docs/references.md` whenever a new paper, system, benchmark, or official doc is used to support project direction.

## Discovery Research Mode

- Read `docs/discovery-research-playbook.md` before proposing unconventional experiments.
- Do not only optimize the obvious path. Surface at least one non-obvious hypothesis when the user is asking for net-new research direction.
- For every strange idea, name the mainstream assumption it challenges, why it might work, why it might fail, the smallest falsifying test, and the stop rule.
- Prefer experiments that can expose mechanisms, not just better numbers.
- Treat failed cases as design material. Start from collapses like GraphWalks failures when they reveal hidden assumptions.
- Use recompute, fallback, prompt visibility, and quality checks as active design tools, not merely baselines.
- Stay disciplined: an against-the-grain idea is not progress until it survives controls and a prior-art refresh.

## Repo-Local Skills

Matt Pocock's `teach` skill is installed at `.codex/skills/teach`.
Use it when turning this research into a guided learning path, exercises, glossary, or learning record.
