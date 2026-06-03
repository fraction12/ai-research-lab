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

## Repo-Local Skills

Matt Pocock's `teach` skill is installed at `.codex/skills/teach`.
Use it when turning this research into a guided learning path, exercises, glossary, or learning record.
