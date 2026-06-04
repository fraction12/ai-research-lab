## Why

Track 02 has shown that native restored KV/state capsules can preserve simple codeword and small structured-retrieval prefixes, while a mini-graph gate stopped at full-visible calibration. The next needed step is a gated campaign that measures whether capsules retain quality while reducing repeated prompt-token and prompt-time cost across multiple queries over reusable context.

## What Changes

- Add a focused Track 02 campaign for scaled amortized KV capsule evaluation.
- Run Phase 1 scaled structured retrieval with reusable prefixes, repeated tail queries, quality gates, capsule byte counts, and amortized break-even curves.
- Run Phase 2 reasoning calibration only after full-visible prompt formats prove reliable; do not import GraphWalks or rescue failed prompts mid-run.
- Run Phase 3 small agent-context capsule benchmark only if Phase 1 produces at least one interpretable restored-capsule pass.
- Package sanitized Track 02 summaries and keep prompt-bearing raw records, responses, token arrays, and state bytes under ignored Track 01 benchmark paths.
- Preserve the narrow framing: this tests reusable-context economics and quality gates, not whether KV cache makes the model inherently smarter.

## Capabilities

### New Capabilities

- `kv-capsule-scaled-amortized-benchmark-campaign`: Defines the gated scaled campaign, amortized metrics, artifact boundaries, stop rules, and interpretation requirements for Track 02 KV/state capsule benchmarking.

### Modified Capabilities

- None.

## Impact

- Adds a new OpenSpec change under `openspec/changes/run-kv-capsule-scaled-amortized-benchmark-campaign/`.
- Adds ignored raw campaign runner/output artifacts under `research/01-ssd-native-inference-current/benchmarks/kv-capsule-scaled-amortized-benchmark-campaign-2026-06-04/raw/`.
- Adds committed sanitized Track 02 campaign artifacts under `research/02-quality-gated-stateful-kv-reuse/experiments/kv-capsule-scaled-amortized-benchmark-campaign-2026-06-04/`.
- Uses the existing pinned DushyantPC native direct C API route against the b9493/GPT-OSS bundle; no tracked Track 01 harness code changes are planned.
