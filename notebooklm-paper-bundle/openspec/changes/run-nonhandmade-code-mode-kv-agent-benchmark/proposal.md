## Why

The 30-case Code-mode + KV capsule harness is a strong internal viability result, but it is still handmade. To make the Track 02 result paper-grade, the same control ladder needs to run on benchmark-derived tool-use tasks with preserved source provenance, benchmark scoring semantics, and negative controls.

## What Changes

- Add a non-handmade benchmark experiment for the existing Code-mode + KV capsule control ladder.
- Use BFCL as the first external benchmark source because it provides broad function-calling/tool-selection coverage, including single, multiple, parallel, irrelevance, executable, and multi-turn categories.
- Treat tau-bench/tau2-bench and ToolSandbox as harder stateful-agent follow-on sources after the BFCL adapter and smoke gates are honest.
- Build deterministic benchmark-derived candidate pools with source ids, source row hashes, source revisions, license notes, benchmark categories, transform hashes, and scorer versions.
- Preserve the exact seven-control ladder from the 30-case internal viability run:
  - `direct_full_visible_tools`
  - `code_mode_full_visible`
  - `code_mode_fresh_tail_only`
  - `code_mode_native_live_append`
  - `code_mode_restored_kv_capsule`
  - `code_mode_wrong_capsule_negative`
  - `compact_visible_evidence_code_mode`
- Gate primary claims on benchmark rows where the full-visible Code-mode baseline passes, then compare restored capsules against native live append and full-visible behavior.
- Record tool-call quality, benchmark scorer outputs, prompt/capsule performance, telemetry, failure classifications, and paper-claim boundaries by benchmark family rather than blending everything into one score.
- Keep prompt-bearing raw artifacts in ignored benchmark output paths while committing paper-facing summaries and manifests under Track 02.

## Capabilities

### New Capabilities

- `nonhandmade-code-mode-kv-agent-benchmark`: Defines the benchmark-derived Code-mode + KV capsule experiment, including source selection, candidate materialization, controls, metrics, stop rules, artifact schema, and interpretation rules.

### Modified Capabilities

- `benchmark-result-summary`: Requires paper-facing summaries to distinguish handmade viability results from non-handmade benchmark evidence and report control-ladder outcomes by source benchmark and task family.
- `flashcache-correctness-eval-suite`: Requires correctness workflows used for this experiment to preserve external benchmark provenance, deterministic transforms, baseline-pass gating, and per-control scoring.
- `llama-cpp-agent-cache-wrapper`: Requires paper-facing Code-mode + KV capsule runs to expose native live append, restored capsule append, capsule metadata, prompt-token deltas, wrong-capsule negatives, and live/restored parity fields.
- `research-positioning-doc`: Requires Track 02 positioning to separate Code-mode runtime-harness value, hidden KV capsule value, visible context-compilation value, and negative controls when interpreting this benchmark.

## Impact

- Adds OpenSpec artifacts under `openspec/changes/run-nonhandmade-code-mode-kv-agent-benchmark/`.
- Adds a paper-facing experiment design document under `research/02-quality-gated-stateful-kv-reuse/docs/`.
- Future implementation will likely extend the existing Code-mode + KV capsule runner under `research/01-ssd-native-inference-current/benchmarks/`.
- Future implementation will materialize external benchmark inputs and prompt-bearing raw outputs under ignored benchmark directories.
- Primary runtime target remains Gemma 4 12B on DushyantPC through the working llama.cpp CUDA sequence-file route.
- No destructive migration is required.
