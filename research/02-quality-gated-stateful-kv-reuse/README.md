# Quality-Gated Stateful KV Reuse

This is the next main research candidate.

## Research Question

Can stateful KV/session reuse for local agent loops preserve full-prompt quality often enough to be useful, and can the system detect when to fall back before quality degrades?

## Why This Is Separate From Track 01

Track 01 proved that reusable local-agent state can save prompt-processing time, but it also exposed correctness drift. This track starts from that drift instead of treating it as an afterthought.

## Core Hypothesis

Stateful KV reuse can be made useful for local agents if the runtime has a correctness contract:

- classify reuse risk by task family and prompt shape
- compare against full-prompt controls
- attribute failures to model weakness, prompt protocol, scorer brittleness, or cache/session semantics
- use fallback as part of the algorithm, not just an emergency escape

## Candidate Experiments

1. Reproduce the current GraphWalks failures from track 01.
2. Add visible-prefix/session-formatted controls.
3. Add repeated full-prompt replay for variance.
4. Compare local model sizes and quantization levels.
5. Build a simple quality-risk router.
6. Measure speed, fallback rate, task-family pass rate, and failure class together.

## Success Shape

A paper-worthy result would not merely show lower latency. It would define when stateful reuse is safe, when it is unsafe, and how a local system can know the difference.

## First Source Track

Use evidence from `../01-ssd-native-inference-current/`, especially:

- `docs/flashcache-system-report.md`
- `benchmarks/datasets/flashcache-correctness-parity-2026-06-03/`
- `docs/research-paper-roadmap.md`
