## Why

The 50-case GraphWalks parents pilot showed that hidden-prefix controls failed while visible-evidence controls matched fresh evidence-only, even though slot telemetry reported saved/restored tokens and slot file I/O. Before interpreting more GraphWalks hidden-prefix results, we need a small semantic sanity test that asks whether the current pinned llama.cpp + GPT-OSS restore path actually behaves like a usable hidden-prefix continuation mechanism for later `/completion` tails.

## What Changes

- Add a focused hidden-prefix semantic-continuation probe with deterministic codeword and key/value retrieval cases.
- Compare `full_visible_prefix_plus_tail`, `fresh_tail_only`, and `restored_hidden_prefix_plus_tail` for every case.
- Record exact prompts, prompt hashes, raw outputs, normalized outputs, correctness, timing, and slot save/restore telemetry.
- Preserve prompt-bearing artifacts under ignored Track 01 benchmark paths and commit only Track 02 summaries.
- Define interpretation rules that separate backend/protocol semantic-restore failure from model weakness, prompt protocol issues, and later GraphWalks task-family limitations.
- Keep the probe tightly scoped: no noiseless GraphWalks evidence rerun and no broad benchmark run.

## Capabilities

### New Capabilities
- `hidden-prefix-semantic-continuation`: Defines the focused semantic-continuation probe, required controls, metrics, artifact layout, failure taxonomy, and interpretation rules for hidden-prefix slot/session restore.

### Modified Capabilities
- `llama-cpp-agent-cache-wrapper`: Require semantic-continuation validation before treating mechanical slot save/restore telemetry as evidence of hidden-prefix semantic reuse.

## Impact

- Affected experiment artifacts: Track 02 summaries under `research/02-quality-gated-stateful-kv-reuse/experiments/hidden-prefix-semantic-continuation-2026-06-04/`.
- Affected local benchmark artifacts: prompt-bearing raw inputs/outputs and slot cache files under `research/01-ssd-native-inference-current/benchmarks/hidden-prefix-semantic-continuation-2026-06-04/`.
- Affected repository hygiene: ignored raw benchmark paths must cover the semantic-continuation probe.
- No Track 01 harness code changes are required unless the probe cannot faithfully express the three-control ladder through an ignored local runner.
