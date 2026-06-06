## Why

Gemma 4 12B now has narrow positive evidence that a saved llama.cpp sequence-file KV state can be restored and semantically appended with only volatile tail tokens, but the paper-facing HF benchmark also showed that bad task construction can make capsule results uninterpretable. The next useful step is a controlled prototype that tests whether KV capsules and Code mode together can help a local model perform tool-heavy, long-horizon agent work with less visible prompt surface while preserving full-visible behavior.

## What Changes

- Add a handoff-quality experiment design for a Code mode plus KV capsule local-agent harness prototype.
- Define a deterministic tool-use task suite that is prefix-dependent, agent-like, and small enough for staged smoke gates before any larger benchmark.
- Define the required control matrix: direct/full-visible tools, Code mode full-visible, Code mode fresh-tail, Code mode native live append, Code mode restored KV capsule append, wrong-capsule negative, and compact visible evidence controls.
- Specify metrics for task success, tool selection, generated-code validity, safety/policy behavior, capsule identity, live-vs-restored parity, prompt-token reduction, runtime costs, and failure taxonomy.
- Define artifact boundaries so prompt-bearing raw data stays under ignored benchmark paths while paper-facing summaries are committed under Track 02.
- Require another agent to prove the prototype with smoke gates before scaling to larger benchmarks.

## Capabilities

### New Capabilities

- `code-mode-kv-capsule-agent-harness`: Defines the prototype harness, task-suite design, controls, metrics, stop rules, artifacts, and interpretation rules for combining Code mode tool-surface compression with KV capsule state reuse on local models.

### Modified Capabilities

- `llama-cpp-agent-cache-wrapper`: Requires KV capsule experiments that use hidden stable prefixes for agent tasks to expose live append, restored append, wrong-capsule negative, capsule identity, prompt-size, and timing metadata.
- `research-positioning-doc`: Requires future Track 02/03 summaries to distinguish KV capsule effects, Code mode/tool-surface compression effects, compact visible evidence effects, and runtime-harness scheduling effects.

## Impact

- Adds OpenSpec artifacts under `openspec/changes/probe-code-mode-kv-capsule-agent-harness/`.
- Adds a Track 02 handoff document under `research/02-quality-gated-stateful-kv-reuse/docs/`.
- Future implementation will likely add or extend local benchmark scripts under `research/01-ssd-native-inference-current/benchmarks/`.
- Future raw prompt, tool-output, generated-code, capsule, and trace artifacts must remain under ignored benchmark directories, with only distilled summaries committed.
- Primary model target remains Gemma 4 12B on DushyantPC through the working llama.cpp sequence-file route unless a later spec changes the local benchmark model policy.
