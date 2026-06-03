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

## Repo-Local Skills

Matt Pocock's `teach` skill is installed at `.codex/skills/teach`.
Use it when turning this research into a guided learning path, exercises, glossary, or learning record.
