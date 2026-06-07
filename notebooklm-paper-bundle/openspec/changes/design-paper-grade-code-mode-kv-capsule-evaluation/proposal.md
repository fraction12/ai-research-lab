## Why

The lab now has a coherent result chain:

- Gemma 4 12B replicated the narrow sequence-file KV capsule mechanism on prefix-dependent tasks.
- The 30-case handmade Code-mode + KV capsule harness passed the core controls with strict fresh-tail and wrong-capsule negatives.
- The first BFCL primary-50 run moved the idea onto external benchmark-derived rows and showed exact native-live/restored-capsule quality parity, while also showing that current restored capsules are not yet faster.

This is promising enough for a paper campaign, but the existing evidence is not yet sufficient for a proper research paper. The next step needs to be predeclared, benchmark-derived, model-controlled, and execution-ready on DushyantPC.

## What Changes

- Add a paper-grade evaluation campaign for the Code-mode + KV capsule local-agent runtime idea.
- Treat the existing BFCL primary-50 result as pilot evidence, not the final paper result.
- Define a full paper experiment with:
  - expanded BFCL cohorts,
  - at least one harder stateful-agent benchmark follow-on,
  - a model matrix,
  - seven-control ladder preservation,
  - strict negative controls,
  - live-vs-restored semantic parity gates,
  - prompt/token/timing/amortization measurement,
  - paper-ready artifacts and periodic run checkups.
- Make the change executable later by specifying stage order, DushyantPC readiness checks, commands/artifact expectations, stop rules, and handoff requirements.

## Capabilities

### New Capabilities

- `paper-grade-code-mode-kv-capsule-evaluation`: Defines the full research-paper evaluation campaign for quality-gated KV state reuse plus Code Mode in local tool-using agents.

### Modified Capabilities

- `benchmark-result-summary`: Requires paper-campaign summaries to distinguish pilot, primary, replication, diagnostic, and ablation evidence.
- `llama-cpp-agent-cache-wrapper`: Requires model-bearing paper runs to record execution readiness, route identity, live/restored parity, capsule overhead, and periodic checkup state.
- `research-positioning-doc`: Requires the paper claim to separate KV reuse, Code-mode tool-surface compression, visible evidence scheduling, host repair, and fallback policy.

## Impact

- Adds OpenSpec artifacts under `openspec/changes/design-paper-grade-code-mode-kv-capsule-evaluation/`.
- Does not execute model-bearing runs yet.
- Future execution will run on DushyantPC using Gemma 4 12B as the primary local model and the working llama.cpp sequence-file route.
- Future implementation will write prompt-bearing raw artifacts under ignored Track 01 benchmark paths and committed paper summaries under Track 02.
- This change should be validated before any broad paper-campaign execution begins.
