## Why

Track 02 has now shown that tail-only raw `/completion` is not a valid semantic continuation primitive on `gpt-oss-20b-mxfp4.gguf`, and an alternate local model/format sanity check did not rescue that path. The next experiment needs to get closer to the actual reusable-state mechanism: restore a saved prefix slot, resend the full visible prompt, and measure whether llama.cpp reuses matching prefix tokens while preserving full-prompt correctness.

## What Changes

- Add a focused restored-prefix/full-resend probe for `gpt-oss-20b-mxfp4.gguf` on DushyantPC.
- Compare cold full-prompt baselines with restored-prefix full-prompt resends on tiny synthetic cases first.
- Add perturbation and wrong-slot controls to test whether prefix reuse is exact-match safe rather than hidden-memory leakage.
- Preserve exact model/backend metadata, commands, prompts, raw outputs, parsed answers, prompt hashes, token/timing telemetry, slot save/restore telemetry, and failure classifications.
- Use this experiment to decide whether to move the six GraphWalks cases to restored-prefix full-resend, or whether lower-level KV/prefix mechanics need a different implementation path.

## Capabilities

### New Capabilities

### Modified Capabilities

- `llama-cpp-agent-cache-wrapper`: Add requirements for a correctness-gated restored-prefix full-resend mechanism probe that measures reusable prefix acceleration without relying on tail-only hidden context.

## Impact

- Affected code: likely a small Track 01 benchmark/probe runner or a focused extension to the correctness evaluator; no broad harness refactor unless the spec proves it is necessary.
- Affected artifacts: new Track 02 experiment directory under `research/02-quality-gated-stateful-kv-reuse/experiments/restored-prefix-full-resend-2026-06-03/`.
- Affected raw outputs: ignored Track 01 benchmark result/cache paths for raw JSON, logs, prompts, and slot files.
- Explicitly excluded: vault-mind model, broad benchmarks, and GraphWalks reruns before the tiny mechanism probe passes.
