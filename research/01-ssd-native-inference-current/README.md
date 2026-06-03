# SSD-Native Inference Current Track

This folder preserves the original SSD-native inference project.

## Thesis

The dent is not "run any dense model directly from any SSD." The dent is storage-aware inference for agent workloads:

- persistent prefix and KV cache
- model-aware block storage
- SSD-backed long-context reuse
- MoE expert paging when the model shape supports it
- Apple Silicon / MLX and llama.cpp as practical local backends
- a benchmark harness that measures cold, warm, and repeated-agent-loop performance

Agent workloads are the wedge because they repeat system prompts, tool schemas, repo context, memory blocks, and long-lived session prefixes. That repeated shape lets the SSD become useful instead of pretending to be VRAM.

## Contents

- `docs/`: research notes, positioning, reports, benchmark graphs, roadmap, references.
- `benchmarks/`: benchmark scripts, fixtures, curated datasets, and ignored local raw scratch outputs.
- `flashcache/`: current wrapper/prototype source.
- `tests/`: tests for the current prototype and benchmark tooling.
- `learning-records/`: learning notes from the first track.

## Start Here

1. Read `docs/idea-brief.md`.
2. Read `docs/flashcache-system-report.md`.
3. Read `docs/research-positioning.md`.
4. Use `docs/research-paper-roadmap.md` for the first-track paper path.
5. Keep source links in `docs/references.md`.

## Validation

Run this track's tests from this folder:

```bash
python3 -m pytest tests
```

Run benchmark scripts from this folder so existing relative paths such as `benchmarks/fixtures/...` continue to work.
