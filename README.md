# AI Research Lab

This repository is a workspace for AI systems research. It keeps speculative ideas, negative-space scans, paper-roadmap work, prototypes, benchmark harnesses, and research notes in one place.

The lab posture is simple:

- look for problems that are not already solved
- challenge obvious assumptions with small falsifying experiments
- preserve evidence, failures, prompts, commands, and source trails
- separate paper discipline from idea discovery
- keep each research direction in its own folder

## Research Tracks

1. [SSD-Native Inference Current Track](research/01-ssd-native-inference-current/README.md)
   Existing Flashcache, SSD-backed local-agent inference, benchmark, and correctness-parity work.

2. [Quality-Gated Stateful KV Reuse](research/02-quality-gated-stateful-kv-reuse/README.md)
   Main next paper candidate: correctness contracts, failure attribution, and fallback policy for stateful KV/session reuse.

3. [Role-Aware Context Compilation](research/03-role-aware-context-compilation/README.md)
   Higher-risk direction: compile agent context into roles and intentionally recompute small anchors to recover quality.

4. [Negative-Space Research Ideas](research/04-negative-space-ideas/README.md)
   Living archive of frontier scans, marked-off prior art, and candidate gaps.

## Start Here

1. Read [research/README.md](research/README.md).
2. Pick the relevant track README.
3. Before claiming novelty, refresh the relevant prior-art scan.
4. Before running an experiment, write the hypothesis, baseline, controls, metrics, confounders, expected artifact, and stop rule.
5. Use root OpenSpec for meaningful changes.

## Lab Rules

- Do not call an idea new until prior art has been checked.
- Do not optimize an obvious path without asking what assumption it hides.
- Do not hide negative results; they are design material.
- Do not blend speed and quality into one comforting average.
- Do not move research across tracks without preserving source notes and raw evidence paths.
