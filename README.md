# SSD Native Inference

Research and prototype notes for making local inference treat SSDs as a first-class memory tier.

## Thesis

The dent is not "run any dense model directly from any SSD." The dent is storage-aware inference for agent workloads:

- persistent prefix and KV cache
- model-aware block storage
- SSD-backed long-context reuse
- MoE expert paging when the model shape supports it
- Apple Silicon / MLX and llama.cpp as practical local backends
- a benchmark harness that measures cold, warm, and repeated-agent-loop performance

Agent workloads are the wedge because they repeat system prompts, tool schemas, repo context, memory blocks, and long-lived session prefixes. That repeated shape lets the SSD become useful instead of pretending to be VRAM.

## Start Here

1. Read [docs/idea-brief.md](docs/idea-brief.md).
2. Read the paper-oriented plan in [docs/research-paper-roadmap.md](docs/research-paper-roadmap.md).
3. Use the discovery posture in [docs/discovery-research-playbook.md](docs/discovery-research-playbook.md).
4. Do the [6-hour learning plan](docs/learning-plan-6-hours.md).
5. Use [docs/technical-map.md](docs/technical-map.md) as the system map.
6. Start with [docs/prototype-plan.md](docs/prototype-plan.md).
7. Keep sources in [docs/references.md](docs/references.md).

## Installed Skills

Matt Pocock's `teach` skill is installed repo-locally at:

`/.codex/skills/teach`

Source: `mattpocock/skills`, path `skills/in-progress/teach`.
